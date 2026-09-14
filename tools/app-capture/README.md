# app-capture

Record a phone app's flow in one start/stop, then get an analysis of it.

```bash
./capture_app.py start --label tinder-onboarding
#   ... use the phone: register, swipe, browse ...
./capture_app.py stop
./capture_app.py analyse
```

## Why it captures three things at once

Each layer is blind in a different direction, and they cover each other:

| layer | how | uniquely gives | blind to |
|---|---|---|---|
| video | `scrcpy --record` | motion, transitions, feel | any structure |
| screenshot | `adb exec-out screencap` | colour, type, imagery, overlap | labels, bounds |
| tree | `uiautomator dump` | exact copy, roles, bounds, flags | colour, imagery, motion |

The unlock is pairing the last two: **crop each node's rect out of the screenshot** and you recover
the fill colour, the real contrast ratio and the type size — none of which the accessibility tree
can express. `analysis/report.py` does exactly that.

## Design decisions worth knowing

**scrcpy, not `screenrecord`.** scrcpy records video *and* the phone's microphone into one file,
so narration shares a clock with the picture and needs no alignment step. `screenrecord` is
video-only — it cannot capture audio at all.

**Dumps are change-triggered, not polled.** `uiautomator dump` costs ~1–2s; `screencap` is cheap.
So screenshots are polled and the tree is only dumped once the screen has *settled* somewhere new.
Measured on real captures: same-screen churn tops out at ~0.004 and a real navigation starts at
~0.095, so the default threshold of 0.035 sits in the gap.

**The transition poll is deliberately skipped.** Capturing the instant the picture jumps is what
makes `uiautomator` fail with "could not get idle state". `ScreenWatcher` waits for the screen to
stop moving before dumping.

**`analyse` never needs the phone.** Runs are self-contained folders, so the report can be
regenerated and retuned long after the device is gone. Iterating on analysis must never mean
recording the flow again.

**Density uses the override, not the physical value.** The target device reports 450 physical with
a 480 override, and every dp figure derived from `bounds` depends on using the override. Getting
this wrong silently skews every touch-target finding.

## Commands

| command | what |
|---|---|
| `devices` | list usable devices with geometry and density |
| `start --label NAME` | begin capturing (detaches, so the terminal stays free) |
| `status` | is a capture running, for how long, how many screens |
| `stop` | finish and summarise |
| `analyse [run]` | (re)generate `report.md` and `analysis.json` |

Useful flags: `--threshold` (change sensitivity), `--poll-interval`, `--root` (where runs live).

## What the report contains

Per screen: inferred title, exact copy inventory, palette with shares, sampled text/background
colour per control, WCAG contrast, touch-target sizes in dp, inferred spacing grid, and issues.

Issue classes detected:

- **touch target** below 44dp
- **contrast** below WCAG AA (4.5:1)
- **occlusion** — two controls whose hit rectangles overlap by more than 60% of the smaller one.
  This is the bug class a tree dump reports as *healthy*: both nodes exist, are clickable, and have
  valid bounds. Only geometry reveals one is painted over the other.
- **possible PII** — password fields and email/phone-shaped text

## Limitations

- **`FLAG_SECURE` apps cannot be captured at all.** Banking and DRM apps capture as one flat
  colour; `start` detects this and aborts rather than leaving a folder of black frames.
- **The tree cannot see images.** An `ImageView` with no `contentDescription` is a bare rectangle.
  For a photo-led product this is the biggest blind spot — screenshots cover it, but you lose
  element-level structure for the imagery.
- **Motion is only in the video.** Neither stills nor the tree can show animation, which is where a
  lot of onboarding craft lives. Frame-extract the video for that.
- **PII is flagged, not removed.** The screenshots keep whatever was on screen, including anything
  typed into a registration form. Redaction is applied at analyse time, not capture time.
- **XML only.** No Flutter scaffold is generated; reconstructing layout from bounds is approximate
  and would produce a misleading result.

## Tests

```bash
python3 -m unittest discover -s tests
```

Fixtures in `fixtures/` are real dumps from a 1080x2340 device, so the expected values — notably
the centre of "Dev Sign In" at `(228, 1998)` — are the coordinates that were actually tapped.
Screen-change thresholds are pinned to measured values rather than picked by feel.
