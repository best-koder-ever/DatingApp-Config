"""Regression Detection — compare screenshots and UI trees against baselines.

Two comparison strategies:
1. Screenshot SSIM (structural similarity) via Pillow
2. UI tree structural diff (content-desc text comparison)
"""

import io
from pathlib import Path
from xml.etree import ElementTree

from PIL import Image


def screenshot_similarity(current: bytes | Path, baseline: bytes | Path) -> float:
    """Compare two screenshots using pixel-level mean absolute error.

    Returns similarity as float 0.0–1.0 (1.0 = identical).
    Both images are resized to the same dimensions before comparison.
    """
    if isinstance(current, Path):
        current = current.read_bytes()
    if isinstance(baseline, Path):
        baseline = baseline.read_bytes()

    img_a = Image.open(io.BytesIO(current)).convert("RGB")
    img_b = Image.open(io.BytesIO(baseline)).convert("RGB")

    # Resize to common size (smaller of the two)
    w = min(img_a.width, img_b.width)
    h = min(img_a.height, img_b.height)
    img_a = img_a.resize((w, h), Image.LANCZOS)
    img_b = img_b.resize((w, h), Image.LANCZOS)

    pixels_a = list(img_a.getdata())
    pixels_b = list(img_b.getdata())

    if len(pixels_a) != len(pixels_b):
        return 0.0

    total_diff = 0
    for pa, pb in zip(pixels_a, pixels_b):
        total_diff += sum(abs(a - b) for a, b in zip(pa, pb))

    max_diff = len(pixels_a) * 3 * 255  # 3 channels, 255 max per channel
    if max_diff == 0:
        return 1.0
    return 1.0 - (total_diff / max_diff)


def _extract_structure(xml_string: str) -> list[tuple[str, str, bool]]:
    """Extract ordered list of (content_desc, class, clickable) from XML."""
    try:
        root = ElementTree.fromstring(xml_string)
    except ElementTree.ParseError:
        return []

    elements = []
    for elem in root.iter("node"):
        desc = elem.get("content-desc", "")
        cls = elem.get("class", "")
        clickable = elem.get("clickable") == "true"
        if desc:  # Only track elements with meaningful content
            elements.append((desc, cls, clickable))
    return elements


def ui_tree_diff(
    current_xml: str, baseline_xml: str
) -> dict:
    """Compare UI tree structures. Returns diff report.

    Report keys:
      - added: elements in current but not baseline
      - removed: elements in baseline but not current
      - similarity: 0.0–1.0 based on intersection/union
    """
    current_elems = _extract_structure(current_xml)
    baseline_elems = _extract_structure(baseline_xml)

    current_descs = [e[0] for e in current_elems]
    baseline_descs = [e[0] for e in baseline_elems]

    current_set = set(current_descs)
    baseline_set = set(baseline_descs)

    added = current_set - baseline_set
    removed = baseline_set - current_set
    common = current_set & baseline_set

    union = current_set | baseline_set
    similarity = len(common) / len(union) if union else 1.0

    return {
        "added": sorted(added),
        "removed": sorted(removed),
        "common_count": len(common),
        "current_count": len(current_set),
        "baseline_count": len(baseline_set),
        "similarity": similarity,
    }


class RegressionChecker:
    """Check screenshots and UI trees against stored baselines."""

    # Thresholds
    SCREENSHOT_PASS = 0.95
    SCREENSHOT_WARN = 0.80
    TREE_PASS = 0.90
    TREE_WARN = 0.70

    def __init__(self, baselines_dir: str | Path):
        self.baselines_dir = Path(baselines_dir)

    def check_screenshot(
        self, current: bytes, screen_name: str
    ) -> dict:
        """Compare current screenshot against baseline.

        Returns: {status: pass|warn|fail, similarity: float, baseline_path: str}
        """
        baseline_path = self.baselines_dir / "resized" / f"*{screen_name}*.png"
        # Try to find a matching baseline by screen name
        candidates = list(self.baselines_dir.glob(f"resized/*{screen_name}*.png"))
        if not candidates:
            # Try numbered files
            candidates = list(self.baselines_dir.glob("resized/*.png"))

        if not candidates:
            return {"status": "skip", "similarity": 0.0, "baseline_path": "none"}

        # Use first matching baseline
        baseline_path = candidates[0]
        sim = screenshot_similarity(current, baseline_path)

        if sim >= self.SCREENSHOT_PASS:
            status = "pass"
        elif sim >= self.SCREENSHOT_WARN:
            status = "warn"
        else:
            status = "fail"

        return {
            "status": status,
            "similarity": sim,
            "baseline_path": str(baseline_path),
        }

    def check_ui_tree(
        self, current_xml: str, screen_name: str
    ) -> dict:
        """Compare current UI tree against baseline XML."""
        candidates = list(self.baselines_dir.glob(f"ui-trees/*{screen_name}*.xml"))
        if not candidates:
            candidates = list(self.baselines_dir.glob("ui-trees/*.xml"))

        if not candidates:
            return {"status": "skip", "similarity": 0.0, "diff": {}}

        baseline_xml = candidates[0].read_text(encoding="utf-8")
        diff = ui_tree_diff(current_xml, baseline_xml)

        if diff["similarity"] >= self.TREE_PASS:
            status = "pass"
        elif diff["similarity"] >= self.TREE_WARN:
            status = "warn"
        else:
            status = "fail"

        return {
            "status": status,
            "similarity": diff["similarity"],
            "diff": diff,
            "baseline_path": str(candidates[0]),
        }
