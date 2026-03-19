"""Unit tests for screen signature detection."""

import os
import sys
import unittest
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from signatures import ScreenId, detect_screen, detect_screen_from_file, extract_content_descs

UI_TREES_DIR = Path(__file__).parent.parent / "walkthrough-screenshots" / "ui-trees"

# Map XML filenames to expected ScreenIds
EXPECTED_SCREENS = {
    "ui_about.xml": ScreenId.ABOUT_ME,
    "ui_complete.xml": ScreenId.ONBOARDING_COMPLETE,
    "ui_discover.xml": ScreenId.DISCOVER,
    "ui_life.xml": ScreenId.LIFESTYLE,
    "ui_loc.xml": ScreenId.LOCATION_PERMISSION,
    "ui_main.xml": ScreenId.DISCOVER,  # main is discover tab
    "ui_matches.xml": ScreenId.MATCHES,
    "ui_matches2.xml": ScreenId.MATCHES,
    "ui_mydejting2.xml": ScreenId.PROFILE_MY_DEJTING,
    "ui_notif.xml": ScreenId.NOTIFICATION_PERMISSION,
    "ui_photos.xml": ScreenId.PHOTOS,
    "ui_profile.xml": ScreenId.PROFILE_GET_MORE,
    "ui_w.xml": ScreenId.ORIENTATION,  # "What's your sexual orientation?"
    "ui_walk.xml": ScreenId.GENDER,  # "What's your gender?"
}


class TestScreenSignatures(unittest.TestCase):

    def test_all_xml_baselines_detected(self):
        """Each of the 14 XML baselines should detect to the correct screen."""
        if not UI_TREES_DIR.exists():
            self.skipTest(f"UI trees directory not found: {UI_TREES_DIR}")

        results = {}
        for filename, expected in EXPECTED_SCREENS.items():
            filepath = UI_TREES_DIR / filename
            if not filepath.exists():
                self.fail(f"Missing XML baseline: {filepath}")
            screen_id, score = detect_screen_from_file(str(filepath))
            results[filename] = (screen_id, score, expected)
            self.assertEqual(
                screen_id, expected,
                f"{filename}: expected {expected.name}, got {screen_id.name} (score={score:.1f})"
            )
            self.assertGreater(score, 0, f"{filename}: score should be > 0")

        # Print summary
        print(f"\n{'File':<25} {'Expected':<25} {'Detected':<25} {'Score':>6}")
        print("-" * 85)
        for filename, (detected, score, expected) in sorted(results.items()):
            status = "✅" if detected == expected else "❌"
            print(f"{status} {filename:<23} {expected.name:<25} {detected.name:<25} {score:>6.1f}")

    def test_unknown_for_garbage_xml(self):
        """Garbage XML should return UNKNOWN."""
        screen_id, score = detect_screen("<hierarchy><node/></hierarchy>")
        self.assertEqual(screen_id, ScreenId.UNKNOWN)
        self.assertEqual(score, 0.0)

    def test_unknown_for_empty_xml(self):
        """Empty content-desc values should return UNKNOWN."""
        xml = '<hierarchy rotation="0"><node content-desc="" /></hierarchy>'
        screen_id, score = detect_screen(xml)
        self.assertEqual(screen_id, ScreenId.UNKNOWN)

    def test_unknown_for_invalid_xml(self):
        """Invalid XML should return UNKNOWN."""
        screen_id, score = detect_screen("not xml at all")
        self.assertEqual(screen_id, ScreenId.UNKNOWN)

    def test_extract_content_descs(self):
        """Should extract non-empty content-desc values."""
        xml = '''<hierarchy rotation="0">
            <node content-desc="Hello" />
            <node content-desc="" />
            <node content-desc="World" />
        </hierarchy>'''
        descs = extract_content_descs(xml)
        self.assertEqual(descs, ["Hello", "World"])

    def test_minimum_confidence(self):
        """Detected screens should have reasonable confidence scores."""
        if not UI_TREES_DIR.exists():
            self.skipTest(f"UI trees directory not found: {UI_TREES_DIR}")
        for filename in EXPECTED_SCREENS:
            filepath = UI_TREES_DIR / filename
            if filepath.exists():
                _, score = detect_screen_from_file(str(filepath))
                self.assertGreaterEqual(
                    score, 5.0,
                    f"{filename}: confidence score {score:.1f} is too low (min 5.0)"
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
