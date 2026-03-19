"""Regression Detection — compare screenshots and UI trees against baselines.

Two comparison strategies:
1. Screenshot SSIM (structural similarity) via Pillow
2. UI tree structural diff (content-desc text comparison)

Baselines are stored in visual-qa/baselines/<use_case>/<NN>-<slug>.{png,xml}
organised by use case and screen sequence number, e.g.:
  baselines/onboarding/01-welcome.png
  baselines/onboarding/01-welcome.xml
"""

import io
from functools import lru_cache
from pathlib import Path
from xml.etree import ElementTree

from PIL import Image
from signatures import ScreenId


# ---------------------------------------------------------------------------
# Ordered screen lists per use case for baseline file naming.
# Each entry: (slug, ScreenId) → files will be "<NN>-<slug>.png" / ".xml"
# ---------------------------------------------------------------------------
USE_CASE_SCREENS: dict[str, list[tuple[str, ScreenId]]] = {
    "onboarding": [
        ("welcome", ScreenId.WELCOME),
        ("phone-entry", ScreenId.PHONE_ENTRY),
        ("sms-code", ScreenId.SMS_CODE),
        ("community-guidelines", ScreenId.COMMUNITY_GUIDELINES),
        ("first-name", ScreenId.FIRST_NAME),
        ("birthday", ScreenId.BIRTHDAY),
        ("gender", ScreenId.GENDER),
        ("orientation", ScreenId.ORIENTATION),
        ("match-preferences", ScreenId.MATCH_PREFERENCES),
        ("age-range", ScreenId.AGE_RANGE),
        ("relationship-goals", ScreenId.RELATIONSHIP_GOALS),
        ("lifestyle", ScreenId.LIFESTYLE),
        ("interests", ScreenId.INTERESTS),
        ("about-me", ScreenId.ABOUT_ME),
        ("photos", ScreenId.PHOTOS),
        ("location-permission", ScreenId.LOCATION_PERMISSION),
        ("notification-permission", ScreenId.NOTIFICATION_PERMISSION),
        ("onboarding-complete", ScreenId.ONBOARDING_COMPLETE),
    ],
    "discovery": [
        ("discover", ScreenId.DISCOVER),
        ("matches", ScreenId.MATCHES),
    ],
    "messaging": [
        ("discover", ScreenId.DISCOVER),
        ("matches", ScreenId.MATCHES),
        ("matches-messages", ScreenId.MATCHES_MESSAGES),
        ("chat", ScreenId.CHAT),
    ],
    "safety": [
        ("discover", ScreenId.DISCOVER),
        ("profile-get-more", ScreenId.PROFILE_GET_MORE),
        ("profile-safety", ScreenId.PROFILE_SAFETY),
        ("profile-my-dejting", ScreenId.PROFILE_MY_DEJTING),
        ("settings", ScreenId.SETTINGS),
    ],
}


@lru_cache(maxsize=None)
def _build_screen_index(use_case: str) -> dict[ScreenId, str]:
    """Build a ScreenId → "NN-slug" mapping for a use case (cached)."""
    return {
        screen_id: f"{i + 1:02d}-{slug}"
        for i, (slug, screen_id) in enumerate(USE_CASE_SCREENS.get(use_case, []))
    }


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
    """Check screenshots and UI trees against stored baselines.

    Baselines are organised as:
        <baselines_dir>/<use_case>/<NN>-<slug>.png
        <baselines_dir>/<use_case>/<NN>-<slug>.xml

    Example:
        checker = RegressionChecker("visual-qa/baselines")
        result = checker.check_screenshot(png_bytes, "onboarding", ScreenId.WELCOME)
    """

    # Thresholds
    SCREENSHOT_PASS = 0.95
    SCREENSHOT_WARN = 0.80
    TREE_PASS = 0.90
    TREE_WARN = 0.70

    def __init__(self, baselines_dir: str | Path):
        """
        Args:
            baselines_dir: Root baselines directory, e.g. ``visual-qa/baselines/``.
                           Sub-directories per use case are expected inside:
                           ``<baselines_dir>/<use_case>/<NN>-<slug>.{png,xml}``
        """
        self.baselines_dir = Path(baselines_dir)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _baseline_path(
        self, use_case: str, screen_id: ScreenId, ext: str
    ) -> Path | None:
        """Return the baseline file path for a screen, or None if absent."""
        index = _build_screen_index(use_case)
        prefix = index.get(screen_id)
        if prefix is not None:
            p = self.baselines_dir / use_case / f"{prefix}.{ext}"
            return p if p.exists() else None
        # Fall back to a name-based glob for unknown/extra screens
        slug = screen_id.name.lower().replace("_", "-")
        candidates = sorted(
            (self.baselines_dir / use_case).glob(f"*-{slug}.{ext}")
        )
        return candidates[0] if candidates else None

    # ------------------------------------------------------------------
    # Public comparison methods
    # ------------------------------------------------------------------

    def check_screenshot(
        self, current: bytes, use_case: str, screen_id: ScreenId
    ) -> dict:
        """Compare *current* screenshot against the stored baseline.

        Args:
            current: Raw PNG bytes of the current screenshot.
            use_case: One of "onboarding", "discovery", "messaging", "safety".
            screen_id: The :class:`~signatures.ScreenId` being compared.

        Returns:
            ``{status: pass|warn|fail|skip, similarity: float, baseline_path: str}``
        """
        baseline_path = self._baseline_path(use_case, screen_id, "png")
        if baseline_path is None:
            return {"status": "skip", "similarity": 0.0, "baseline_path": "none"}

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
        self, current_xml: str, use_case: str, screen_id: ScreenId
    ) -> dict:
        """Compare *current* UI tree against the stored baseline XML.

        Args:
            current_xml: Raw uiautomator XML string.
            use_case: One of "onboarding", "discovery", "messaging", "safety".
            screen_id: The :class:`~signatures.ScreenId` being compared.

        Returns:
            ``{status: pass|warn|fail|skip, similarity: float, diff: dict,
            baseline_path: str}``
        """
        baseline_path = self._baseline_path(use_case, screen_id, "xml")
        if baseline_path is None:
            return {"status": "skip", "similarity": 0.0, "diff": {}}

        baseline_xml = baseline_path.read_text(encoding="utf-8")
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
            "baseline_path": str(baseline_path),
        }

    # ------------------------------------------------------------------
    # Baseline capture
    # ------------------------------------------------------------------

    def save_baseline(
        self,
        use_case: str,
        screen_id: ScreenId,
        screenshot: bytes | None = None,
        xml: str | None = None,
    ) -> dict[str, str]:
        """Write screenshot and/or XML to the baselines directory.

        Creates ``<baselines_dir>/<use_case>/`` if it does not exist.

        Args:
            use_case: Target sub-directory (e.g. "onboarding").
            screen_id: Screen whose baseline is being saved.
            screenshot: Raw PNG bytes, or ``None`` to skip.
            xml: uiautomator XML string, or ``None`` to skip.

        Returns:
            Dict with ``"png"`` and/or ``"xml"`` keys pointing to written paths.
        """
        index = _build_screen_index(use_case)
        prefix = index.get(screen_id)
        if prefix is None:
            # Unlisted screen — use a plain slug so it can still be stored
            prefix = f"00-{screen_id.name.lower().replace('_', '-')}"

        case_dir = self.baselines_dir / use_case
        case_dir.mkdir(parents=True, exist_ok=True)

        written: dict[str, str] = {}
        if screenshot is not None:
            png_path = case_dir / f"{prefix}.png"
            png_path.write_bytes(screenshot)
            written["png"] = str(png_path)
        if xml is not None:
            xml_path = case_dir / f"{prefix}.xml"
            xml_path.write_text(xml, encoding="utf-8")
            written["xml"] = str(xml_path)
        return written
