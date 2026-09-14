#!/usr/bin/env python3
"""capture-app -- record a phone app's flow in one start/stop.

    capture-app start --label tinder-onboarding
    ... use the phone: register, swipe, whatever ...
    capture-app stop
    capture-app analyse            # regenerate the report, no phone needed

`start` detaches a background runner so the terminal stays free while you use the phone, and so
`stop` can reach it from a different shell. The two talk through `state.json` in the run folder.

Analysis is a separate command on purpose: iterating on the report should never mean recording
the flow again.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from capture_core import (  # noqa: E402
    CaptureError,
    CaptureSession,
    RunPaths,
    device_info,
    list_devices,
    require_device,
    screencap,
)
from screen_change import load_image  # noqa: E402

DEFAULT_ROOT = Path(__file__).resolve().parents[2] / "runs" / "app-capture"
STATE_NAME = "state.json"


# ── helpers ────────────────────────────────────────────────────────────────────


# A run is identified by its manifest, NOT its state file. state.json is transient -- it only
# exists while a capture is live -- whereas manifest.json is the durable record of what was
# captured. Keying "is this a run?" off the transient file meant `analyse` refused to open any
# run whose state had been cleaned up, which is every finished run.
RUN_MARKER = "manifest.json"


def find_run(root: Path, wanted: str | None) -> Path:
    """Locate a run directory: by explicit path, by name fragment, or the most recent."""
    if wanted:
        p = Path(wanted)
        if p.is_dir() and (p / RUN_MARKER).exists():
            return p
        matches = sorted([d for d in root.glob(f"*{wanted}*") if (d / RUN_MARKER).exists()])
        if not matches:
            raise CaptureError(f"No run matching {wanted!r} under {root}")
        return matches[-1]

    runs = sorted(d for d in root.glob("*") if (d / RUN_MARKER).exists())
    if not runs:
        raise CaptureError(f"No runs found under {root}. Start one with: capture-app start")
    return runs[-1]


def read_state(run_dir: Path) -> dict:
    try:
        return json.loads((run_dir / STATE_NAME).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def active_runs(root: Path) -> list[Path]:
    """Runs whose recorded process is still alive. Guards against double-starting."""
    out = []
    for d in sorted(root.glob("*")):
        st = read_state(d)
        pid = st.get("pid")
        if st.get("status") == "running" and isinstance(pid, int):
            try:
                os.kill(pid, 0)  # signal 0 = liveness probe only
                out.append(d)
            except OSError:
                pass
    return out


def _human(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m}m{s:02d}s" if m else f"{s}s"


# ── commands ───────────────────────────────────────────────────────────────────


def cmd_devices(args) -> int:
    devices = list_devices()
    if not devices:
        print("No device in ADB mode.")
        print("  Plug the phone in with USB debugging ON and accept the prompt on the phone.")
        print("  `adb devices` must list it as 'device' -- 'unauthorized' or 'offline' will not work.")
        return 1
    for serial in devices:
        try:
            info = device_info(serial)
            print(f"  {serial}  {info.model or 'unknown'}  {info.width}x{info.height}  "
                  f"density {info.density_physical}"
                  f"{f' (override {info.density_override})' if info.density_override else ''}  "
                  f"SDK {info.sdk}")
        except CaptureError as exc:
            print(f"  {serial}  (could not query: {exc})")
    return 0


def cmd_status(args) -> int:
    root = Path(args.root)
    running = active_runs(root)
    if not running:
        print("No capture running.")
        latest = sorted(d for d in root.glob("*") if (d / RUN_MARKER).exists())
        if latest:
            st = read_state(latest[-1])
            print(f"  last run: {latest[-1].name}  ({st.get('screens', 0)} screens, {st.get('status')})")
        return 0
    for d in running:
        st = read_state(d)
        elapsed = time.monotonic() - st.get("started_at", time.monotonic())
        print(f"  RUNNING  {d.name}")
        print(f"    pid      {st.get('pid')}")
        print(f"    elapsed  {_human(elapsed)}")
        print(f"    screens  {st.get('screens', 0)}")
    return 0


def cmd_start(args) -> int:
    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)

    running = active_runs(root)
    if running:
        print(f"A capture is already running: {running[-1].name}", file=sys.stderr)
        print("Stop it first: capture-app stop", file=sys.stderr)
        return 1

    serial = require_device(args.device)
    info = device_info(serial)
    paths = RunPaths(root, args.label or info.model or serial).create()

    print(f"Recording from {info.model or serial} ({serial})")
    print(f"  screen    {info.width}x{info.height}")
    print(f"  density   {info.effective_density}"
          + (f" (override; physical {info.density_physical})" if info.density_override else ""))
    print(f"  run dir   {paths.dir}")

    if not args.yes:
        print()
        print("  A registration flow will put real email addresses, phone numbers and passwords")
        print("  on screen, and they will be saved in this run's screenshots. Everything stays")
        print("  on this machine. Redaction is applied at analyse time.")
    print()

    # Detach so the terminal is free while the phone is used, and so `stop` can find it.
    log = paths.dir / "capture.log"
    with open(log, "wb") as lf:
        proc = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "_run",
             "--run-dir", str(paths.dir),
             "--device", serial,
             "--poll-interval", str(args.poll_interval),
             "--threshold", str(args.threshold)],
            stdout=lf, stderr=lf, stdin=subprocess.DEVNULL, start_new_session=True,
        )

    # Wait for the runner to publish state so a failure to start is reported here, not silently.
    for _ in range(40):
        st = read_state(paths.dir)
        if st.get("status") == "running":
            print(f"Capture started (pid {st.get('pid')}).")
            print("  Use the phone normally, then run:  capture-app stop")
            return 0
        if proc.poll() is not None:
            detail = log.read_text(encoding="utf-8", errors="replace").strip()
            print("Capture failed to start.", file=sys.stderr)
            print(detail or "(no output)", file=sys.stderr)
            return 1
        time.sleep(0.25)

    print("Capture did not report ready in time. Check capture.log in the run dir.", file=sys.stderr)
    return 1


def cmd_stop(args) -> int:
    root = Path(args.root)
    running = active_runs(root)
    if not running:
        print("No capture running.")
        return 0

    run_dir = running[-1]
    st = read_state(run_dir)
    pid = st.get("pid")
    print(f"Stopping capture in {run_dir.name} (pid {pid})...")

    try:
        os.kill(pid, signal.SIGINT)
    except OSError as exc:
        print(f"  could not signal pid {pid}: {exc}", file=sys.stderr)
        return 1

    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if read_state(run_dir).get("status") != "running":
            break
        time.sleep(0.5)

    manifest = run_dir / "manifest.json"
    screens = 0
    if manifest.exists():
        try:
            screens = len(json.loads(manifest.read_text(encoding="utf-8")).get("screens", []))
        except ValueError:
            pass

    video = run_dir / "video.mkv"
    print("Capture stopped.")
    print(f"  screens  {screens}")
    print(f"  video    {video} ({video.stat().st_size // 1024} KB)" if video.exists()
          else "  video    (none)")
    print(f"  run dir  {run_dir}")
    print()
    print("  Next:  capture-app analyse " + run_dir.name)
    return 0


def cmd_run(args) -> int:
    """The detached worker. Not meant to be run by hand."""
    run_dir = Path(args.run_dir)
    paths = RunPaths.attach(run_dir)

    session = CaptureSession(
        device=device_info(args.device),
        paths=paths,
        poll_interval=args.poll_interval,
        threshold=args.threshold,
    )

    stopping = {"flag": False}

    def on_signal(signum, frame):  # noqa: ARG001
        stopping["flag"] = True

    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    session.started_at = time.monotonic()

    def announce(rec) -> None:
        label = rec.labels[0][:44] if rec.labels else "(no labels)"
        print(f"  [{rec.t_ms:>7}ms] screen {rec.index:>3}  {label}", flush=True)

    session._write_manifest(status="running")
    session._write_state(status="running")
    session._running = True

    if session.record_video:
        session._recorder = subprocess.Popen(
            session._scrcpy_command(), stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, start_new_session=True,
        )

    while not stopping["flag"]:
        try:
            image = load_image(screencap(session.device.serial))
            verdict = session.watcher.observe(image)
            if verdict.changed:
                announce(session._capture(image, delta=verdict.delta))
        except CaptureError:
            pass
        time.sleep(session.poll_interval)

    if session._recorder and session._recorder.poll() is None:
        try:
            os.killpg(os.getpgid(session._recorder.pid), signal.SIGINT)
            session._recorder.wait(timeout=15)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            session._recorder.kill()

    session._write_manifest(status="complete")
    session._write_state(status="stopped")
    print("  recorder stopped", flush=True)
    return 0


def cmd_analyse(args) -> int:
    root = Path(args.root)
    run_dir = find_run(root, args.run)
    try:
        from analysis.report import analyse_run
    except ImportError as exc:
        print(f"Analysis module unavailable: {exc}", file=sys.stderr)
        return 1

    report = analyse_run(run_dir)
    print(f"Analysed {run_dir.name}")
    for line in report.summary_lines():
        print(f"  {line}")
    print(f"\n  report: {run_dir / 'report.md'}")
    return 0


# ── entry point ────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="capture-app",
        description="Record a phone app's flow: start, use the app, stop.",
    )
    p.add_argument("--root", default=str(DEFAULT_ROOT), help="where run folders live")
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("devices", help="list usable devices")
    d.set_defaults(func=cmd_devices)

    st = sub.add_parser("status", help="is a capture running?")
    st.set_defaults(func=cmd_status)

    s = sub.add_parser("start", help="begin a capture")
    s.add_argument("--label", help="name for the run folder, e.g. tinder-onboarding")
    s.add_argument("--device", help="adb serial (default: the only device)")
    s.add_argument("--poll-interval", type=float, default=0.5,
                   help="seconds between screencap polls (default 0.5)")
    s.add_argument("--threshold", type=float, default=0.035,
                   help="change sensitivity; measured same-screen churn is ~0.004 and a real "
                        "navigation starts ~0.095, so 0.035 sits in the gap")
    s.add_argument("--yes", action="store_true", help="skip the PII notice")
    s.set_defaults(func=cmd_start)

    sp = sub.add_parser("stop", help="finish the running capture")
    sp.set_defaults(func=cmd_stop)

    a = sub.add_parser("analyse", help="(re)generate the report for a finished run")
    a.add_argument("run", nargs="?", help="run name, folder or path (default: most recent)")
    a.set_defaults(func=cmd_analyse)

    r = sub.add_parser("_run", help=argparse.SUPPRESS)
    r.add_argument("--run-dir", required=True)
    r.add_argument("--device", required=True)
    r.add_argument("--poll-interval", type=float, default=0.5)
    r.add_argument("--threshold", type=float, default=0.035)
    r.set_defaults(func=cmd_run)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except CaptureError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
