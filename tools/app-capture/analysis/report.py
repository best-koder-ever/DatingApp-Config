"""Turn a run folder into an analysis.

This is where the three capture layers finally combine. Neither the screenshot nor the tree is
enough alone, but together they answer questions neither can:

* **Palette and text colour.** The tree knows an element's rect; only the screenshot knows what
  colour is inside it. Crop the rect, sample, and you recover exact fills.
* **Contrast.** Same trick, then WCAG maths. The tree cannot express contrast at all.
* **Type size.** The tree exposes no font metrics -- genuinely not an accessibility concept -- so
  size is inferred from the rect height of a text node.
* **Spacing.** Rect deltas give real margins and padding, which reveals the underlying grid.
* **Occlusion.** Two nodes with valid bounds can still overlap on screen. Nothing in the tree
  flags that; comparing rects does.

Runs are re-analysable without the phone, which is the point: retuning the report must never mean
recording the flow again.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image
from screen_change import dominant_colors
from ui_tree import Node, UiTree

# WCAG 2.1 thresholds for normal-weight body text.
CONTRAST_AA = 4.5
CONTRAST_AA_LARGE = 3.0
# Android's minimum touch target. Below this, a control is hard to hit.
MIN_TOUCH_DP = 44.0

# Below this, an email/phone is likely real user data rather than demo content.
PII_PATTERNS = (
    r"[\w.+-]+@[\w-]+\.[\w.]+",       # email
    r"(?<!\d)(?:\+?\d[\s-]?){7,15}(?!\d)",  # phone-ish run of digits
)


# ── colour maths ───────────────────────────────────────────────────────────────


def _relative_luminance(rgb: tuple[int, int, int]) -> float:
    """WCAG relative luminance. Note the sRGB gamma curve -- a plain weighted average is wrong."""
    def channel(c: int) -> float:
        s = c / 255.0
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    """WCAG contrast ratio, 1.0 (identical) to 21.0 (black on white)."""
    l1, l2 = _relative_luminance(fg), _relative_luminance(bg)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def _hex(rgb: tuple[int, int, int]) -> str:
    return "#%02X%02X%02X" % rgb


def _pick_text_and_bg(image: Image.Image) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    """Split a crop into (text colour, background colour).

    The background is the most common colour. The text is the colour furthest in luminance from
    it, among reasonably common colours -- extremes beat frequency here, because text is
    deliberately a minority of the pixels.
    """
    colours = dominant_colors(image, count=8)
    if not colours:
        return (0, 0, 0), (255, 255, 255)

    bg = max(colours, key=lambda c: c[1])[0]
    bg_lum = _relative_luminance(bg)
    candidates = [c for c, share in colours if share > 0.005] or [bg]

    text = max(candidates, key=lambda c: abs(_relative_luminance(c) - bg_lum))
    return text, bg


# ── per-screen findings ────────────────────────────────────────────────────────


@dataclass
class ElementFinding:
    label: str
    role: str
    bounds: tuple[int, int, int, int]
    min_side_dp: float
    text_color: str = ""
    background: str = ""
    contrast: float = 0.0
    pii: bool = False


@dataclass
class ScreenFinding:
    index: int
    t_ms: int
    title: str
    png: str
    node_counts: dict[str, int] = field(default_factory=dict)
    copy: list[str] = field(default_factory=list)
    controls: list[ElementFinding] = field(default_factory=list)
    palette: list[tuple[str, float]] = field(default_factory=list)
    grid_dp: float | None = None
    issues: list[str] = field(default_factory=list)


@dataclass
class RunReport:
    run_dir: Path
    device: dict
    density: int
    screens: list[ScreenFinding] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def summary_lines(self) -> list[str]:
        out = [f"{len(self.screens)} screens captured",
               f"density {self.density} (used for all dp maths)"]
        issues = sum(len(s.issues) for s in self.screens)
        out.append(f"{issues} issue(s) found")
        pii = sum(1 for s in self.screens for c in s.controls if c.pii)
        if pii:
            out.append(f"{pii} control(s) may contain personal data - review before sharing")
        return out


def _looks_like_pii(text: str) -> bool:
    import re

    return any(re.search(p, text) for p in PII_PATTERNS)


def _infer_grid(values: list[float]) -> float | None:
    """Guess the spacing system from the most common gap between numbers.

    Rounded to the nearest 4dp, because design systems are almost always built on a 4 or 8 step
    and raw gaps carry sub-pixel noise.
    """
    if len(values) < 3:
        return None
    gaps = [round(b - a) for a, b in zip(values, values[1:]) if b - a > 1]
    if not gaps:
        return None
    common = max(set(gaps), key=gaps.count)
    return float(common - (common % 4)) or None


def _detect_occlusion(nodes: list[Node]) -> list[str]:
    """Flag controls whose hit areas overlap significantly.

    This is the bug class that a tree dump alone reports as healthy: both nodes exist, are
    clickable, and have valid bounds. Only geometry shows one is painted over the other. A real
    example was a floating feedback button covering the first post's up-arrow, so tapping "up"
    opened the wrong thing entirely.
    """
    issues: list[str] = []
    live = [n for n in nodes if n.clickable and n.area > 0 and n.label]
    for i, a in enumerate(live):
        for b in live[i + 1:]:
            ax1, ay1, ax2, ay2 = a.bounds
            bx1, by1, bx2, by2 = b.bounds
            ox = max(0, min(ax2, bx2) - max(ax1, bx1))
            oy = max(0, min(ay2, by2) - max(ay1, by1))
            if ox <= 0 or oy <= 0:
                continue
            overlap = ox * oy
            smaller = min(a.area, b.area)
            # >60% of the smaller control buried is a real conflict, not an edge touch.
            if smaller and overlap / smaller > 0.6:
                issues.append(
                    f"overlap: {a.label!r} {a.bounds} is covered by {b.label!r} {b.bounds}"
                )
    return issues


def analyse_run(run_dir: Path) -> RunReport:
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    device = manifest.get("device", {})
    # The override, not the physical value, or every dp figure is wrong.
    density = int(manifest.get("effective_density") or device.get("density_override")
                  or device.get("density_physical") or 480)
    screen_px = (int(device.get("width", 1080)), int(device.get("height", 2340)))

    report = RunReport(run_dir=run_dir, device=device, density=density)

    for entry in manifest.get("screens", []):
        png_path = run_dir / entry["png"]
        if not png_path.exists():
            report.warnings.append(f"missing screenshot for screen {entry.get('index')}")
            continue

        image = Image.open(png_path).convert("RGB")
        sf = ScreenFinding(index=entry.get("index", 0), t_ms=entry.get("t_ms", 0),
                           title="", png=entry["png"])

        xml_rel = entry.get("xml")
        tree: UiTree | None = None
        if xml_rel and (run_dir / xml_rel).exists():
            tree = UiTree.parse((run_dir / xml_rel).read_text(encoding="utf-8"), screen_px)
        else:
            report.warnings.append(f"screen {sf.index}: no tree (dump may have failed)")

        if tree:
            sf.node_counts = tree.counts()

            # Title: the largest text on screen. Proxies "what this screen is called".
            #
            # Deliberately draws on ALL text, not just non-clickable text: a lot of screens put
            # their heading inside a button or a tappable row, and restricting to inert nodes
            # made those screens come back untitled.
            heads = [n for n in tree.meaningful() if n.text and len(n.text.strip()) > 1]
            if heads:
                best = max(heads, key=lambda n: (n.height, -n.bounds[1]))
                sf.title = best.text.strip().splitlines()[0][:60]

            seen: set[str] = set()
            for n in tree.meaningful():
                if n.text and n.text not in seen:
                    seen.add(n.text)
                    sf.copy.append(n.text)

            # Sample each control's rect out of the screenshot: fill and text colour.
            for n in tree.clickable():
                text, bg = _pick_text_and_bg(image.crop(n.bounds))
                ratio = contrast_ratio(text, bg)
                sf.controls.append(ElementFinding(
                    label=n.label[:50], role=n.cls.split(".")[-1], bounds=n.bounds,
                    min_side_dp=round(n.min_side_dp(density), 1),
                    text_color=_hex(text), background=_hex(bg),
                    contrast=round(ratio, 2),
                    pii=_looks_like_pii(n.label) or n.is_password,
                ))

            # Palette across the whole screen.
            sf.palette = [(_hex(c), round(s, 3)) for c, s in dominant_colors(image, count=6)]

            # Grid, from the vertical rhythm of the text nodes.
            tops = sorted({float(n.bounds[1]) for n in tree.text_nodes()})
            sf.grid_dp = _infer_grid(tops)

            sf.issues.extend(_detect_occlusion(tree.nodes))

        # Touch targets and contrast are audited from the findings, so they work without a tree.
        for c in sf.controls:
            if c.min_side_dp < MIN_TOUCH_DP:
                sf.issues.append(
                    f"touch target: {c.label!r} is {c.min_side_dp}dp "
                    f"(min {MIN_TOUCH_DP:g}dp) at {c.bounds}"
                )
            if c.contrast and c.contrast < CONTRAST_AA:
                sf.issues.append(
                    f"contrast: {c.label!r} is {c.contrast}:1 "
                    f"({c.text_color} on {c.background}), below {CONTRAST_AA}:1"
                )
            if c.pii:
                sf.issues.append(f"possible personal data in {c.label!r} - redact before sharing")

        report.screens.append(sf)

    (run_dir / "report.md").write_text(_render(report), encoding="utf-8")
    (run_dir / "analysis.json").write_text(
        json.dumps({
            "density": density,
            "screens": [
                {"index": s.index, "t_ms": s.t_ms, "title": s.title, "copy": s.copy,
                 "palette": s.palette, "grid_dp": s.grid_dp, "issues": s.issues,
                 "counts": s.node_counts,
                 "controls": [c.__dict__ for c in s.controls]}
                for s in report.screens
            ],
            "warnings": report.warnings,
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return report


def _render(r: RunReport) -> str:
    lines = [
        "# App flow capture",
        "",
        f"- device: {r.device.get('model', '?')} ({r.device.get('serial', '?')})",
        f"- screen: {r.device.get('width')}x{r.device.get('height')} px, density {r.density}",
        f"- screens captured: {len(r.screens)}",
        "",
    ]
    if r.warnings:
        lines += ["## Warnings", ""] + [f"- {w}" for w in r.warnings] + [""]

    lines += ["## Flow", "", "| # | t (ms) | screen | controls | issues |", "|---|---|---|---|---|"]
    for s in r.screens:
        title = s.title.replace("|", "\\|") or "(untitled)"
        lines.append(f"| {s.index} | {s.t_ms} | {title} | {len(s.controls)} | {len(s.issues)} |")
    lines.append("")

    for s in r.screens:
        lines += [f"## Screen {s.index} - {s.title or '(untitled)'}", "",
                  f"t = {s.t_ms} ms  |  `{s.png}`", ""]
        if s.palette:
            lines += ["**Palette**", "",
                      "| colour | share |", "|---|---|"]
            lines += [f"| `{c}` | {sh:.1%} |" for c, sh in s.palette]
            lines.append("")
        if s.grid_dp:
            lines += [f"**Spacing grid:** ~{s.grid_dp:g}dp between text baselines", ""]
        if s.copy:
            lines += ["**Copy (exact)**", ""] + [f"- {c}" for c in s.copy[:40]] + [""]
        if s.controls:
            lines += ["**Controls**", "",
                      "| label | role | dp | contrast | text | bg |", "|---|---|---|---|---|---|"]
            for c in s.controls:
                label = c.label.replace("|", "\\|") or "(unlabelled)"
                lines.append(f"| {label} | {c.role} | {c.min_side_dp} | {c.contrast}:1 "
                             f"| `{c.text_color}` | `{c.background}` |")
            lines.append("")
        if s.issues:
            lines += ["**Issues**", ""] + [f"- {i}" for i in s.issues] + [""]

    return "\n".join(lines)
