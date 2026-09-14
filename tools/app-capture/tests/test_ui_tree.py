"""Tests for the uiautomator XML parser.

Every expectation here comes from a real 1080x2340 dump taken off the device earlier, so the
numbers are not invented -- the centre of "Dev Sign In" is the coordinate that was actually
tapped successfully, and the density is the device's real 450-physical/480-override split.
"""

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from ui_tree import UiTree  # noqa: E402

FIXTURES = pathlib.Path(__file__).resolve().parents[1] / "fixtures"
SCREEN = (1080, 2340)
# The override, not `wm density`'s physical 450. Using 450 here would skew every dp value.
DENSITY = 480


def load(name: str) -> UiTree:
    return UiTree.parse((FIXTURES / name).read_text(encoding="utf-8"), SCREEN)


class TestWelcomeScreen(unittest.TestCase):
    def setUp(self) -> None:
        self.tree = load("welcome_screen.xml")

    def test_visible_labels_are_found(self) -> None:
        for label in ("Dev Sign In", "Fresh Onboard", "Skin Coral", "Logga in"):
            with self.subTest(label=label):
                self.assertIsNotNone(self.tree.find(label), f"{label} should be findable")

    def test_dev_sign_in_centre_matches_the_coordinate_tapped_on_device(self) -> None:
        """The bug this guards: an off-by-one or wrong bounds parse silently taps the wrong button."""
        node = self.tree.find("Dev Sign In")
        assert node is not None
        self.assertEqual(node.bounds, (84, 1932, 372, 2064))
        self.assertEqual(node.center, (228, 1998))

    def test_neighbour_buttons_are_distinguishable(self) -> None:
        """Regression: "Dev Sign In" and "Fresh Onboard" sit adjacent and I once hit the wrong one."""
        dev = self.tree.find("Dev Sign In")
        fresh = self.tree.find("Fresh Onboard")
        assert dev is not None and fresh is not None
        self.assertNotEqual(dev.center, fresh.center)
        self.assertLess(dev.bounds[2], fresh.bounds[0])  # dev ends before fresh begins

    def test_exact_match_does_not_return_a_substring_hit(self) -> None:
        self.assertIsNone(self.tree.find("Dev", exact=True))
        self.assertIsNotNone(self.tree.find("Dev", exact=False))

    def test_every_fixture_node_is_clickable_and_enabled(self) -> None:
        clickable = self.tree.clickable()
        self.assertEqual(len(clickable), 7)
        self.assertTrue(all(n.enabled for n in clickable))

    def test_password_and_editable_detection(self) -> None:
        self.assertEqual(self.tree.editable(), [])  # no fields on the welcome screen
        self.assertEqual(self.tree.counts()["password_fields"], 0)


class TestForumFeed(unittest.TestCase):
    def setUp(self) -> None:
        self.tree = load("forum_feed.xml")

    def test_numeric_entities_are_unescaped(self) -> None:
        """uiautomator writes newlines as &#10;; leaving them raw poisons every label comparison."""
        node = self.tree.find("Community")
        assert node is not None
        self.assertEqual(node.label, "Community\nFlik 6 av 6")
        self.assertIn("\n", node.label)
        self.assertNotIn("&#10;", node.label)

    def test_non_ascii_entities_are_unescaped(self) -> None:
        self.assertIsNotNone(self.tree.find("Första dejter"))  # &#246;
        self.assertIsNotNone(self.tree.find("Nytt inlägg"))  # &#228;

    def test_find_all_returns_every_tab(self) -> None:
        self.assertEqual(len(self.tree.find_all("Flik")), 3)

    def test_find_does_not_return_the_full_screen_wrapper(self) -> None:
        """Regression: "screen:community" is a [0,0][1080,2340] wrapper published BEFORE the
        tab. Document order returned it, and its centre is the middle of the screen -- so
        tapping "Community" would have tapped nothing useful."""
        node = self.tree.find("Community")
        assert node is not None
        self.assertNotIn("screen:", node.label)
        self.assertEqual(node.label, "Community\nFlik 6 av 6")

    def test_find_prefers_the_smaller_specific_target(self) -> None:
        node = self.tree.find("Community")
        assert node is not None
        self.assertLess(node.area, 1080 * 2340)

    def test_find_control_returns_a_clickable_node(self) -> None:
        node = self.tree.find_control("Community")
        assert node is not None
        self.assertTrue(node.clickable)

    def test_password_field_is_flagged(self) -> None:
        self.assertEqual(self.tree.counts()["password_fields"], 1)
        pw = [n for n in self.tree.editable() if n.is_password]
        self.assertEqual(len(pw), 1)

    def test_zero_area_nodes_are_not_meaningful(self) -> None:
        """A [0,0][0,0] node would produce a tap at (0,0) -- the status bar."""
        self.assertFalse(any(n.area == 0 for n in self.tree.meaningful()))

    def test_labels_prefer_content_desc_over_text(self) -> None:
        edit = self.tree.editable()[0]
        self.assertEqual(edit.text, "Test 639248392306135262")
        self.assertEqual(edit.label, "Test 639248392306135262")  # falls back to text

    def test_headings_are_ordered_by_height(self) -> None:
        headings = self.tree.headings(density=DENSITY)
        heights = [n.height for n in headings]
        self.assertEqual(heights, sorted(heights, reverse=True))


class TestDensityConversion(unittest.TestCase):
    """dp maths is only correct with the *override* density; this is the classic silent bug."""

    def setUp(self) -> None:
        self.tree = load("welcome_screen.xml")

    def test_dev_sign_in_is_exactly_44dp_high(self) -> None:
        node = self.tree.find("Dev Sign In")
        assert node is not None
        w, h = node.size_dp(DENSITY)
        self.assertAlmostEqual(w, 96.0, places=2)
        self.assertAlmostEqual(h, 44.0, places=2)

    def test_undersized_control_is_flagged_at_override_density(self) -> None:
        """"Villkor" is 126x63px -> 42x21dp, so it is a genuine touch-target violation."""
        node = self.tree.find("Villkor")
        assert node is not None
        self.assertLess(node.min_side_dp(DENSITY), 44.0)

    def test_wrong_density_would_change_the_verdict(self) -> None:
        """Proves the override matters: at physical 450 the same node measures differently."""
        node = self.tree.find("Villkor")
        assert node is not None
        at_450 = node.size_dp(450)[0]
        at_480 = node.size_dp(480)[0]
        self.assertNotAlmostEqual(at_450, at_480, places=2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
