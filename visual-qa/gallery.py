#!/usr/bin/env python3
"""
visual-qa/gallery.py — Static HTML screenshot gallery generator.

Generates a self-contained HTML page from visual QA test results showing:
  • Captured screenshot  |  Baseline  |  Diff overlay  (side-by-side)
  • Results grouped by use-case with pass/fail badges

Usage:
    python3 visual-qa/gallery.py [OPTIONS]

Options:
    --screenshots DIR   Directory containing captured test screenshots (default: visual-qa/screenshots)
    --baselines   DIR   Directory containing baseline images           (default: visual-qa/baselines)
    --output      FILE  Path for the generated HTML file              (default: visual-qa/reports/gallery.html)
    --diff-threshold N  Pixel-difference threshold to mark as FAIL    (default: 5.0  percent)
    --title       TEXT  Page title                                     (default: "Visual QA Gallery")

Directory layout expected:
    screenshots/
        <use_case>/
            <test_name>.png
    baselines/
        <use_case>/
            <test_name>.png          (optional; missing baseline shown as placeholder)

Output:
    A single self-contained HTML file (all images inlined as data-URIs).

Exit codes:
    0  All tests passed (or no screenshots found)
    1  At least one test failed the diff threshold
"""

import argparse
import base64
import io
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Optional Pillow import (diff generation only)
# ---------------------------------------------------------------------------
try:
    from PIL import Image, ImageChops, ImageEnhance
    _PILLOW_AVAILABLE = True
except ImportError:  # pragma: no cover
    _PILLOW_AVAILABLE = False


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TestResult:
    use_case: str
    test_name: str
    screenshot_path: Optional[Path]
    baseline_path: Optional[Path]
    diff_percent: float = 0.0
    passed: bool = True
    diff_image_b64: str = ""   # base64-encoded PNG diff, empty if not computed


@dataclass
class UseCaseGroup:
    name: str
    results: list = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)


# ---------------------------------------------------------------------------
# Image helpers
# ---------------------------------------------------------------------------

def _image_to_b64(path: Optional[Path], placeholder_text: str = "") -> str:
    """Return a base64-encoded data-URI for an image, or a grey SVG placeholder."""
    if path and path.exists():
        with open(path, "rb") as fh:
            data = base64.b64encode(fh.read()).decode()
        suffix = path.suffix.lower().lstrip(".")
        mime = "image/png" if suffix in ("png", "") else f"image/{suffix}"
        return f"data:{mime};base64,{data}"
    # Generate a simple SVG placeholder
    label = placeholder_text.replace("&", "&amp;").replace("<", "&lt;")
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200">'
        '<rect width="100%" height="100%" fill="#2a2a2a"/>'
        f'<text x="50%" y="50%" fill="#888" font-family="monospace" '
        f'font-size="14" text-anchor="middle" dominant-baseline="middle">{label}</text>'
        "</svg>"
    )
    data = base64.b64encode(svg.encode()).decode()
    return f"data:image/svg+xml;base64,{data}"


def _compute_diff(screenshot: Optional[Path], baseline: Optional[Path]) -> tuple[float, str]:
    """
    Compute pixel-level diff between screenshot and baseline.

    Returns:
        (diff_percent, diff_image_b64)
        diff_percent  — percentage of pixels that differ (0–100)
        diff_image_b64 — base64 PNG of the diff image (empty string on failure)
    """
    if not _PILLOW_AVAILABLE:
        return 0.0, ""
    if not screenshot or not baseline:
        return 0.0, ""
    if not screenshot.exists() or not baseline.exists():
        return 0.0, ""

    try:
        img_a = Image.open(screenshot).convert("RGB")
        img_b = Image.open(baseline).convert("RGB")

        # Resize to same dimensions (use screenshot size as reference)
        if img_a.size != img_b.size:
            img_b = img_b.resize(img_a.size, Image.LANCZOS)

        diff = ImageChops.difference(img_a, img_b)

        # Amplify diff for visibility
        enhanced = ImageEnhance.Brightness(diff).enhance(5.0)

        # Calculate percentage of changed pixels
        diff_bytes = diff.tobytes()
        total = diff.width * diff.height
        # Each pixel is 3 bytes (R,G,B); count pixels where any channel > threshold
        changed = sum(
            1 for i in range(0, len(diff_bytes), 3)
            if any(diff_bytes[i + c] > 10 for c in range(3))
        )
        diff_percent = (changed / total) * 100 if total else 0.0

        buf = io.BytesIO()
        enhanced.save(buf, format="PNG")
        diff_b64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
        return diff_percent, diff_b64

    except Exception:  # noqa: BLE001
        return 0.0, ""


# ---------------------------------------------------------------------------
# Gallery builder
# ---------------------------------------------------------------------------

def collect_results(
    screenshots_dir: Path,
    baselines_dir: Path,
    diff_threshold: float,
) -> list[UseCaseGroup]:
    """Walk screenshots_dir and build UseCaseGroup list."""
    groups: dict[str, UseCaseGroup] = {}

    if not screenshots_dir.exists():
        return []

    for use_case_dir in sorted(screenshots_dir.iterdir()):
        if not use_case_dir.is_dir():
            continue
        use_case = use_case_dir.name
        group = groups.setdefault(use_case, UseCaseGroup(name=use_case))

        for img_path in sorted(use_case_dir.iterdir()):
            if img_path.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
                continue
            test_name = img_path.stem
            baseline_path = baselines_dir / use_case / img_path.name

            diff_percent, diff_b64 = _compute_diff(img_path, baseline_path)
            passed = diff_percent <= diff_threshold or not baseline_path.exists()

            group.results.append(TestResult(
                use_case=use_case,
                test_name=test_name,
                screenshot_path=img_path,
                baseline_path=baseline_path if baseline_path.exists() else None,
                diff_percent=diff_percent,
                passed=passed,
                diff_image_b64=diff_b64,
            ))

    return list(groups.values())


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    :root {{
      --bg: #111;
      --surface: #1a1a1a;
      --surface2: #242424;
      --border: #333;
      --text: #e0e0e0;
      --text-muted: #888;
      --pass: #4caf50;
      --fail: #f44336;
      --accent: #FF7F50;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: var(--bg); color: var(--text); font-family: system-ui, monospace; }}
    header {{
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 1.2rem 2rem;
      display: flex;
      align-items: center;
      gap: 1.5rem;
    }}
    header h1 {{ font-size: 1.4rem; font-weight: 600; color: var(--accent); }}
    .summary {{
      display: flex; gap: 2rem; font-size: 0.85rem; color: var(--text-muted);
    }}
    .summary span strong {{ color: var(--text); }}
    .summary .fail-count {{ color: var(--fail); }}
    main {{ padding: 1.5rem 2rem; max-width: 1600px; margin: 0 auto; }}

    /* Use-case sections */
    .group {{ margin-bottom: 2.5rem; }}
    .group-header {{
      display: flex; align-items: center; gap: 0.8rem;
      padding: 0.7rem 1rem;
      background: var(--surface);
      border-left: 4px solid var(--border);
      border-radius: 4px 4px 0 0;
      cursor: pointer;
      user-select: none;
    }}
    .group-header.pass  {{ border-left-color: var(--pass); }}
    .group-header.fail  {{ border-left-color: var(--fail); }}
    .group-title {{ font-size: 1rem; font-weight: 600; flex: 1; }}
    .badge {{
      display: inline-block;
      padding: 0.2rem 0.6rem;
      border-radius: 9999px;
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.05em;
    }}
    .badge.pass {{ background: var(--pass); color: #000; }}
    .badge.fail {{ background: var(--fail); color: #fff; }}
    .group-body {{ display: none; }}
    .group-body.open {{ display: block; }}
    .group-body-inner {{
      border: 1px solid var(--border);
      border-top: none;
      border-radius: 0 0 4px 4px;
      padding: 1rem;
      background: var(--surface2);
      display: flex;
      flex-wrap: wrap;
      gap: 1.2rem;
    }}

    /* Test cards */
    .card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 6px;
      overflow: hidden;
      width: 100%;
      max-width: 960px;
    }}
    .card-header {{
      display: flex; align-items: center; gap: 0.6rem;
      padding: 0.5rem 0.8rem;
      border-bottom: 1px solid var(--border);
      font-size: 0.85rem;
    }}
    .card-header .test-name {{ flex: 1; font-weight: 600; }}
    .diff-pct {{ color: var(--text-muted); font-size: 0.78rem; }}
    .images {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0;
    }}
    .img-panel {{
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 0.6rem 0.4rem 0.4rem;
      border-right: 1px solid var(--border);
    }}
    .img-panel:last-child {{ border-right: none; }}
    .img-panel label {{
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-muted);
      margin-bottom: 0.4rem;
    }}
    .img-panel img {{
      width: 100%;
      max-height: 280px;
      object-fit: contain;
      border-radius: 3px;
      background: #0a0a0a;
      cursor: zoom-in;
    }}
    /* Lightbox */
    #lightbox {{
      display: none;
      position: fixed; inset: 0;
      background: rgba(0,0,0,0.92);
      z-index: 1000;
      align-items: center;
      justify-content: center;
    }}
    #lightbox.open {{ display: flex; }}
    #lightbox img {{ max-width: 95vw; max-height: 95vh; border-radius: 4px; }}
    #lightbox-close {{
      position: absolute; top: 1rem; right: 1.5rem;
      color: #fff; font-size: 2rem; cursor: pointer; line-height: 1;
    }}
    /* Responsive */
    @media (max-width: 700px) {{
      .images {{ grid-template-columns: 1fr; }}
    }}
    footer {{
      text-align: center; padding: 1.5rem;
      color: var(--text-muted); font-size: 0.75rem;
      border-top: 1px solid var(--border);
    }}
  </style>
</head>
<body>
<header>
  <h1>🖼 {title}</h1>
  <div class="summary">
    <span>Use-cases: <strong>{total_groups}</strong></span>
    <span>Screenshots: <strong>{total_tests}</strong></span>
    <span class="fail-count">Failures: <strong>{total_failed}</strong></span>
    <span>Generated: <strong>{generated_at}</strong></span>
  </div>
</header>
<main>
{groups_html}
</main>
<div id="lightbox" onclick="closeLightbox()">
  <span id="lightbox-close" onclick="closeLightbox()">✕</span>
  <img id="lightbox-img" src="" alt="full-size preview">
</div>
<footer>
  DatingApp Visual QA Gallery &mdash; generated by <code>visual-qa/gallery.py</code>
</footer>
<script>
  // Toggle group bodies
  document.querySelectorAll('.group-header').forEach(function(hdr) {{
    hdr.addEventListener('click', function() {{
      var body = hdr.nextElementSibling;
      body.classList.toggle('open');
    }});
  }});
  // Auto-open failed groups
  document.querySelectorAll('.group-header.fail').forEach(function(hdr) {{
    hdr.nextElementSibling.classList.add('open');
  }});
  // Open first group if all pass
  var first = document.querySelector('.group-header');
  if (first && !document.querySelector('.group-header.fail')) {{
    first.nextElementSibling.classList.add('open');
  }}
  // Lightbox
  function openLightbox(src) {{
    document.getElementById('lightbox-img').src = src;
    document.getElementById('lightbox').classList.add('open');
  }}
  function closeLightbox() {{
    document.getElementById('lightbox').classList.remove('open');
    document.getElementById('lightbox-img').src = '';
  }}
  document.querySelectorAll('.img-panel img').forEach(function(img) {{
    img.addEventListener('click', function(e) {{
      e.stopPropagation();
      openLightbox(this.src);
    }});
  }});
  document.addEventListener('keydown', function(e) {{
    if (e.key === 'Escape') closeLightbox();
  }});
</script>
</body>
</html>
"""

_GROUP_TEMPLATE = """\
<section class="group">
  <div class="group-header {pass_class}">
    <span class="group-title">{name}</span>
    <span class="badge {pass_class}">{status}</span>
    <span style="color:var(--text-muted);font-size:0.8rem">{total} test(s) &mdash; {failed} failed</span>
  </div>
  <div class="group-body">
    <div class="group-body-inner">
{cards_html}
    </div>
  </div>
</section>"""

_CARD_TEMPLATE = """\
      <div class="card">
        <div class="card-header">
          <span class="test-name">{test_name}</span>
          <span class="badge {pass_class}">{status}</span>
          {diff_pct_html}
        </div>
        <div class="images">
          <div class="img-panel">
            <label>Screenshot</label>
            <img src="{screenshot_src}" alt="screenshot" loading="lazy">
          </div>
          <div class="img-panel">
            <label>Baseline</label>
            <img src="{baseline_src}" alt="baseline" loading="lazy">
          </div>
          <div class="img-panel">
            <label>Diff</label>
            <img src="{diff_src}" alt="diff" loading="lazy">
          </div>
        </div>
      </div>"""


def _render_group(group: UseCaseGroup) -> str:
    cards = []
    for r in group.results:
        pass_class = "pass" if r.passed else "fail"
        status = "PASS" if r.passed else "FAIL"
        diff_pct_html = (
            f'<span class="diff-pct">Δ {r.diff_percent:.2f}%</span>'
            if r.baseline_path else ""
        )
        diff_src = (
            r.diff_image_b64
            if r.diff_image_b64
            else _image_to_b64(None, "No diff available")
        )
        cards.append(_CARD_TEMPLATE.format(
            test_name=r.test_name,
            pass_class=pass_class,
            status=status,
            diff_pct_html=diff_pct_html,
            screenshot_src=_image_to_b64(r.screenshot_path, "No screenshot"),
            baseline_src=_image_to_b64(r.baseline_path, "No baseline"),
            diff_src=diff_src,
        ))
    return _GROUP_TEMPLATE.format(
        name=group.name,
        pass_class="pass" if group.passed else "fail",
        status="PASS" if group.passed else "FAIL",
        total=group.total,
        failed=group.failed,
        cards_html="\n".join(cards),
    )


def generate_gallery(
    screenshots_dir: Path,
    baselines_dir: Path,
    output_path: Path,
    diff_threshold: float,
    title: str,
) -> bool:
    """
    Build the gallery HTML and write to output_path.

    Returns True if all tests passed, False if any failed.
    """
    from datetime import datetime, timezone

    groups = collect_results(screenshots_dir, baselines_dir, diff_threshold)

    total_tests = sum(g.total for g in groups)
    total_failed = sum(g.failed for g in groups)
    groups_html = "\n".join(_render_group(g) for g in groups)

    if not groups:
        groups_html = (
            '<p style="color:var(--text-muted);padding:2rem;text-align:center">'
            "No screenshots found. Run visual QA tests first.</p>"
        )

    html = _HTML_TEMPLATE.format(
        title=title,
        total_groups=len(groups),
        total_tests=total_tests,
        total_failed=total_failed,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        groups_html=groups_html,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    print(f"✅  Gallery written to: {output_path}")
    print(f"    Use-cases : {len(groups)}")
    print(f"    Screenshots: {total_tests}")
    print(f"    Failures  : {total_failed}")
    if not _PILLOW_AVAILABLE:
        print("⚠️   Pillow not installed — diff images skipped. Install with: pip install Pillow")

    return total_failed == 0


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def _parse_args(argv=None):
    repo_root = Path(__file__).parent
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--screenshots",
        type=Path,
        default=repo_root / "screenshots",
        metavar="DIR",
        help="Directory of captured screenshots (default: visual-qa/screenshots)",
    )
    parser.add_argument(
        "--baselines",
        type=Path,
        default=repo_root / "baselines",
        metavar="DIR",
        help="Directory of baseline images (default: visual-qa/baselines)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=repo_root / "reports" / "gallery.html",
        metavar="FILE",
        help="Output HTML path (default: visual-qa/reports/gallery.html)",
    )
    parser.add_argument(
        "--diff-threshold",
        type=float,
        default=5.0,
        metavar="N",
        help="Pixel-diff %% threshold to mark a test as FAIL (default: 5.0)",
    )
    parser.add_argument(
        "--title",
        default="Visual QA Gallery",
        metavar="TEXT",
        help="Page title (default: 'Visual QA Gallery')",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv)
    all_passed = generate_gallery(
        screenshots_dir=args.screenshots,
        baselines_dir=args.baselines,
        output_path=args.output,
        diff_threshold=args.diff_threshold,
        title=args.title,
    )
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
