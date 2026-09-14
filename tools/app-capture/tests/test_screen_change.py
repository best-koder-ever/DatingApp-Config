"""Tests for change detection.

The numbers are measured from real 1080x2340 captures, so the threshold is justified by data
rather than picked by feel. If someone retunes it, these tests say what breaks.
"""

import pathlib
import sys
import unittest

import numpy as np
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from screen_change import (  # noqa: E402
    ScreenWatcher,
    difference,
    dominant_colors,
    fingerprint,
    is_blank,
    load_image,
)

TMP = pathlib.Path("/tmp")
# Measured: same-screen churn tops out ~0.004, a real navigation starts ~0.095.
MEASURED_SAME_SCREEN_MAX = 0.0042
MEASURED_NEW_SCREEN_MIN = 0.0956


def fixture(name: str) -> Image.Image | None:
    p = TMP / name
    return load_image(p.read_bytes()) if p.exists() else None


class TestFingerprint(unittest.TestCase):
    def test_identical_images_have_zero_difference(self) -> None:
        img = fixture("forum1.png")
        if img is None:
            self.skipTest("fixture screenshot missing")
        self.assertEqual(difference(fingerprint(img), fingerprint(img)), 0.0)

    def test_fingerprint_is_small_and_normalised(self) -> None:
        img = fixture("forum1.png")
        if img is None:
            self.skipTest("fixture screenshot missing")
        fp = fingerprint(img)
        self.assertEqual(fp.shape, (32, 32))
        self.assertGreaterEqual(float(fp.min()), 0.0)
        self.assertLessEqual(float(fp.max()), 1.0)

    def test_solid_colour_images_differ_by_known_amount(self) -> None:
        black = Image.new("RGB", (100, 100), (0, 0, 0))
        white = Image.new("RGB", (100, 100), (255, 255, 255))
        self.assertEqual(difference(fingerprint(black), fingerprint(white)), 1.0)
        self.assertEqual(difference(fingerprint(black), fingerprint(black)), 0.0)


class TestThresholdSitsBetweenRealCases(unittest.TestCase):
    """The whole design rests on this margin: navigation must clear the bar, churn must not."""

    def test_default_threshold_is_between_same_screen_and_new_screen(self) -> None:
        self.assertGreater(ScreenWatcher().threshold, MEASURED_SAME_SCREEN_MAX * 2)
        self.assertLess(ScreenWatcher().threshold, MEASURED_NEW_SCREEN_MIN)

    def test_real_navigations_exceed_the_threshold(self) -> None:
        pairs = [
            ("app2.png", "cur.png"),      # welcome -> discover
            ("forum1.png", "forum2.png"),  # feed -> topic sub-page
        ]
        for a, b in pairs:
            ia, ib = fixture(a), fixture(b)
            if ia is None or ib is None:
                self.skipTest("fixture screenshots missing")
            with self.subTest(pair=f"{a}->{b}"):
                delta = difference(fingerprint(ia), fingerprint(ib))
                self.assertGreater(delta, ScreenWatcher().threshold)

    def test_same_screen_churn_does_not_exceed_the_threshold(self) -> None:
        """forum1 vs forum3 are the same feed with the FAB moved -- must NOT count as a new screen."""
        ia, ib = fixture("forum1.png"), fixture("forum3.png")
        if ia is None or ib is None:
            self.skipTest("fixture screenshots missing")
        delta = difference(fingerprint(ia), fingerprint(ib))
        self.assertLess(delta, ScreenWatcher().threshold)


class TestScreenWatcher(unittest.TestCase):
    def test_first_frame_is_always_captured(self) -> None:
        w = ScreenWatcher()
        img = Image.new("RGB", (100, 100), (10, 20, 30))
        self.assertTrue(w.observe(img).changed)

    def test_repeated_identical_frames_settle_and_do_not_recapture(self) -> None:
        w = ScreenWatcher(settle_frames=2)
        img = Image.new("RGB", (100, 100), (10, 20, 30))
        w.observe(img)  # first, always captured
        results = [w.observe(img).changed for _ in range(5)]
        self.assertFalse(any(results), "a static screen must not keep re-capturing")

    def test_transition_poll_is_not_captured_then_settled_screen_is_captured_once(self) -> None:
        """The contract that matters.

        The poll where the picture jumps IS the transition. Capturing there is exactly what makes
        `uiautomator dump` fail with "could not get idle state", so it must be skipped. The screen
        is then captured once, after it has stopped moving.
        """
        w = ScreenWatcher(settle_frames=2)
        a = Image.new("RGB", (100, 100), (10, 20, 30))
        b = Image.new("RGB", (100, 100), (200, 210, 220))
        w.observe(a)
        w.observe(a)

        self.assertFalse(w.observe(b).changed, "must not capture on the transition poll")

        settled = [w.observe(b).changed for _ in range(6)]
        self.assertEqual(settled.count(True), 1, "must capture the settled screen exactly once")

        # Latency is bounded by settle_frames rather than a hardcoded index, so retuning the
        # setting cannot silently break this test.
        self.assertTrue(
            any(settled[: w.settle_frames]),
            f"capture should land within {w.settle_frames} poll(s) of the screen settling",
        )

    def test_settle_frames_is_never_zero(self) -> None:
        """A zero would reintroduce the mid-transition dump this whole mechanism exists to avoid."""
        self.assertGreaterEqual(ScreenWatcher().settle_frames, 1)

    def test_continuous_animation_never_settles_and_is_not_captured(self) -> None:
        """Guards the mid-transition case that makes uiautomator fail with 'could not get idle state'."""
        w = ScreenWatcher(threshold=0.02, settle_frames=2)
        w.observe(Image.new("RGB", (100, 100), (0, 0, 0)))
        captured = 0
        for i in range(12):
            shade = (i * 20) % 255
            if w.observe(Image.new("RGB", (100, 100), (shade, shade, shade))).changed:
                captured += 1
        self.assertEqual(captured, 0, "nothing should be captured while the screen is moving")

    def test_reset_allows_recapturing_the_same_screen(self) -> None:
        w = ScreenWatcher(settle_frames=2)
        img = Image.new("RGB", (100, 100), (10, 20, 30))
        w.observe(img)
        w.observe(img)
        w.reset()
        self.assertTrue(w.observe(img).changed)


class TestBlankDetection(unittest.TestCase):
    def test_flat_black_frame_is_blank(self) -> None:
        """A FLAG_SECURE app captures as one flat colour -- this is how that is caught."""
        self.assertTrue(is_blank(Image.new("RGB", (200, 400), (0, 0, 0))))

    def test_real_screenshots_are_not_blank(self) -> None:
        for name in ("forum1.png", "forum2.png", "app2.png", "cur.png"):
            img = fixture(name)
            if img is None:
                continue
            with self.subTest(name=name):
                self.assertFalse(is_blank(img), f"{name} was wrongly flagged as blank")

    def test_dark_but_structured_screen_is_not_blank(self) -> None:
        """Dark mode is not a blocked capture; only FLATNESS plus darkness means blocked."""
        arr = np.zeros((200, 200, 3), dtype=np.uint8)
        arr[:, 100:] = 40  # a real dark UI has structure
        self.assertFalse(is_blank(Image.fromarray(arr)))


class TestDominantColors(unittest.TestCase):
    def test_solid_image_returns_that_colour(self) -> None:
        colours = dominant_colors(Image.new("RGB", (50, 50), (255, 0, 0)))
        self.assertEqual(len(colours), 1)
        self.assertEqual(colours[0][0], (240, 0, 0))  # quantised to a 16-step palette
        self.assertAlmostEqual(colours[0][1], 1.0, places=3)

    def test_shares_are_relative_to_the_whole_image_and_capped_at_one(self) -> None:
        """Top-N only, so shares sum to <= 1 rather than exactly 1.

        Keeping them relative to the whole image is the point: it says how much of the screen a
        colour actually owns, which is what you want when recovering a palette.
        """
        img = fixture("forum1.png")
        if img is None:
            self.skipTest("fixture screenshot missing")
        total = sum(share for _, share in dominant_colors(img))
        self.assertLessEqual(total, 1.0)
        self.assertGreater(total, 0.5, "the dominant few colours should own most of the screen")

    def test_requesting_more_colours_covers_more_of_the_image(self) -> None:
        img = fixture("forum1.png")
        if img is None:
            self.skipTest("fixture screenshot missing")
        few = sum(s for _, s in dominant_colors(img, count=2))
        many = sum(s for _, s in dominant_colors(img, count=12))
        self.assertLessEqual(few, many)

    def test_ordered_by_share_descending(self) -> None:
        img = fixture("forum1.png")
        if img is None:
            self.skipTest("fixture screenshot missing")
        shares = [s for _, s in dominant_colors(img)]
        self.assertEqual(shares, sorted(shares, reverse=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
