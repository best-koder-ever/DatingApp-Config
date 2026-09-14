"""Decide when a screen is worth capturing.

`uiautomator dump` costs ~1-2s, so dumping on a timer is wasteful: you pay full price for every
second the user spends reading one screen. Instead poll cheap `screencap` frames and only dump
when the picture has actually moved on.

The hard part is telling *navigation* apart from *animation*. A spinner, a blinking cursor or a
progress bar changes pixels constantly without the screen having become a new screen. So compare
downscaled, blurred fingerprints: that discards small high-frequency churn and keeps big layout
changes, which is exactly the navigation signal.

Also detects the `FLAG_SECURE` case -- a screen that captures as one flat colour, which means the
app has blocked screen capture and there is nothing to record.
"""

from __future__ import annotations

import io
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageFilter

# 32x32 keeps ~1KB per fingerprint and is insensitive to a moving cursor.
FINGERPRINT_SIZE = 32


def load_image(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data)).convert("RGB")


def fingerprint(image: Image.Image, size: int = FINGERPRINT_SIZE) -> np.ndarray:
    """A small luminance grid standing in for the screen.

    Grayscale, downscaled, and lightly blurred. Blur matters: without it, anti-aliased text and
    sub-pixel drift on a static screen register as change.
    """
    small = image.convert("L").resize((size, size), Image.Resampling.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(radius=0.8))
    return np.asarray(small, dtype=np.float32) / 255.0


def difference(a: np.ndarray, b: np.ndarray) -> float:
    """Mean absolute difference, 0.0 identical to 1.0 polar opposite."""
    return float(np.abs(a - b).mean())


@dataclass
class ChangeVerdict:
    changed: bool
    delta: float
    threshold: float

    def __str__(self) -> str:  # pragma: no cover - debugging aid
        return f"{'CHANGED' if self.changed else 'same'} (delta={self.delta:.4f} vs {self.threshold})"


class ScreenWatcher:
    """Tracks the last accepted fingerprint and decides when to capture.

    `threshold` is deliberately a parameter rather than a constant: how much churn a screen
    produces varies wildly by app (a chat with a live timer vs a static form).
    """

    def __init__(self, threshold: float = 0.035, settle_frames: int = 2):
        self.threshold = threshold
        # Number of consecutive stable polls required before accepting. Waiting for the screen
        # to STOP moving avoids dumping mid-transition, which is where uiautomator fails with
        # "could not get idle state".
        self.settle_frames = settle_frames
        self._last_accepted: np.ndarray | None = None
        self._previous: np.ndarray | None = None
        self._stable_count = 0

    def reset(self) -> None:
        self._last_accepted = None
        self._previous = None
        self._stable_count = 0

    def observe(self, image: Image.Image) -> ChangeVerdict:
        """Feed one polled frame; returns whether the screen has settled somewhere new."""
        fp = fingerprint(image)

        # Not enough history yet: the first frame is always worth capturing.
        if self._last_accepted is None:
            self._last_accepted = fp
            self._previous = fp
            return ChangeVerdict(True, 1.0, self.threshold)

        moving = difference(fp, self._previous) if self._previous is not None else 0.0
        self._previous = fp

        if moving > self.threshold:
            # Still animating or mid-transition. Hold off and reset the settle counter.
            self._stable_count = 0
            return ChangeVerdict(False, moving, self.threshold)

        self._stable_count += 1
        if self._stable_count < self.settle_frames:
            return ChangeVerdict(False, moving, self.threshold)

        # Settled. Is this somewhere new, or the same screen we already captured?
        delta = difference(fp, self._last_accepted)
        if delta <= self.threshold:
            return ChangeVerdict(False, delta, self.threshold)

        self._last_accepted = fp
        self._stable_count = 0
        return ChangeVerdict(True, delta, self.threshold)


def is_blank(image: Image.Image, dark_max: float = 0.06, flatness_max: float = 0.01) -> bool:
    """True for a flat dark frame, i.e. the app refused to be captured (FLAG_SECURE).

    Both conditions are required. A genuinely dark-but-real screen still has structure, so its
    standard deviation stays above `flatness_max`; a blocked capture is uniformly black.
    """
    fp = fingerprint(image)
    return float(fp.mean()) < dark_max and float(fp.std()) < flatness_max


def dominant_colors(image: Image.Image, count: int = 5) -> list[tuple[tuple[int, int, int], float]]:
    """Most common colours as (rgb, share), quantised so near-identical shades collapse.

    This is the payload of pairing a screenshot with an element's bounds: crop first, then call
    this, and you recover the fill colour that the accessibility tree cannot express.
    """
    small = image.convert("RGB")
    # Quantise to a coarse palette; 16 levels per channel is fine for "what colour is this".
    arr = (np.asarray(small, dtype=np.uint16) // 16 * 16).astype(np.uint8)
    flat = arr.reshape(-1, 3)
    if flat.size == 0:
        return []

    packed = (flat[:, 0].astype(np.uint32) << 16) | (flat[:, 1].astype(np.uint32) << 8) | flat[:, 2]
    values, counts = np.unique(packed, return_counts=True)
    order = np.argsort(-counts)[:count]
    total = counts.sum()

    out = []
    for i in order:
        v = int(values[i])
        rgb = ((v >> 16) & 0xFF, (v >> 8) & 0xFF, v & 0xFF)
        out.append((rgb, float(counts[i]) / float(total)))
    return out
