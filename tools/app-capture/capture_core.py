"""The capture session: record video while snapshotting screens as they change.

Design notes that are not obvious from reading the code:

* **scrcpy records video and the phone's microphone into one file.** That is why narration needs
  no separate alignment step -- audio and video share a clock because they came out of the same
  muxer. `screenrecord` cannot do this at all (it is video-only).

* **The heavy call is `uiautomator dump` (~1-2s); `screencap` is cheap.** So we poll screenshots
  and only dump when `ScreenWatcher` says the screen has settled somewhere new. Dumps then scale
  with navigation rather than with time spent reading.

* **Every artifact is stamped with milliseconds since `t0`**, and `t0` is taken immediately
  before the recorder starts. Without a shared origin the video, screenshots and tree dumps are
  just a pile of unrelated files.
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from screen_change import ScreenWatcher, is_blank, load_image
from ui_tree import UiTree

# Device-side scratch path. `uiautomator dump` can only write to a file, and it reuses the same
# path every call, so the result must be pulled off immediately or it is lost.
DEVICE_DUMP_PATH = "/sdcard/appcapture_ui.xml"


class CaptureError(RuntimeError):
    """Something the user has to fix (no device, blocked capture, wrong path)."""


# ── device plumbing ────────────────────────────────────────────────────────────


def adb(args: list[str], timeout: float = 30.0) -> bytes:
    exe = shutil.which("adb")
    if exe is None:
        raise CaptureError("adb is not on PATH")
    proc = subprocess.run([exe, *args], capture_output=True, timeout=timeout)
    if proc.returncode != 0:
        msg = proc.stderr.decode("utf-8", "replace").strip()
        raise CaptureError(f"adb {' '.join(args)} failed: {msg}")
    return proc.stdout


def list_devices() -> list[str]:
    out = adb(["devices"]).decode("utf-8", "replace")
    devices = []
    for line in out.splitlines()[1:]:
        parts = line.split()
        # "unauthorized" and "offline" are NOT usable; only "device" is.
        if len(parts) >= 2 and parts[1] == "device":
            devices.append(parts[0])
    return devices


def require_device(serial: str | None) -> str:
    devices = list_devices()
    if not devices:
        raise CaptureError(
            "No device in ADB mode. Plug the phone in with USB debugging ON and accept the "
            "'Allow USB debugging?' prompt. If it shows as MTP/charging only, that is the "
            "problem -- `adb devices` must list it as 'device', not 'unauthorized' or 'offline'."
        )
    if serial and serial not in devices:
        raise CaptureError(f"Device {serial!r} not connected. Available: {', '.join(devices)}")
    return serial or devices[0]


@dataclass
class DeviceInfo:
    serial: str
    width: int
    height: int
    density_physical: int
    density_override: int | None
    sdk: int
    model: str = ""

    @property
    def effective_density(self) -> int:
        """The override when present, else physical.

        This distinction is not academic: the target device reports 450 physical with a 480
        override, and every dp figure derived from `bounds` depends on using the override.
        """
        return self.density_override or self.density_physical


def device_info(serial: str) -> DeviceInfo:
    def sh(cmd: list[str]) -> str:
        return adb(["-s", serial, "shell", *cmd]).decode("utf-8", "replace")

    size_out = sh(["wm", "size"])
    width = height = 0
    for token in size_out.replace("Override size:", "Physical size:").split():
        if "x" in token and token[0].isdigit():
            w, _, h = token.partition("x")
            if w.isdigit() and h.isdigit():
                width, height = int(w), int(h)  # override size wins when both are printed
    if not width:
        raise CaptureError(f"Could not parse screen size from: {size_out!r}")

    dens_out = sh(["wm", "density"])
    physical = override = 0
    for line in dens_out.splitlines():
        val = line.split(":")[-1].strip()
        if not val.isdigit():
            continue
        if line.lower().startswith("physical"):
            physical = int(val)
        elif line.lower().startswith("override"):
            override = int(val)

    sdk_out = sh(["getprop", "ro.build.version.sdk"]).strip()
    model_out = sh(["getprop", "ro.product.model"]).strip()
    return DeviceInfo(
        serial=serial, width=width, height=height,
        density_physical=physical or 480, density_override=override or None,
        sdk=int(sdk_out) if sdk_out.isdigit() else 0, model=model_out,
    )


def screencap(serial: str) -> bytes:
    """Raw PNG bytes of the current screen."""
    return adb(["-s", serial, "exec-out", "screencap", "-p"], timeout=20)


def uiautomator_dump(serial: str, retries: int = 3) -> str | None:
    """Pull the accessibility tree as XML, or None if it would not settle.

    Retried because the dump fails with "could not get idle state" whenever the UI is still
    animating, which is common right after a navigation. A miss here is not fatal -- the next
    screen change will pick it up.
    """
    for attempt in range(retries):
        try:
            adb(["-s", serial, "shell", "uiautomator", "dump", DEVICE_DUMP_PATH], timeout=40)
            xml = adb(["-s", serial, "shell", "cat", DEVICE_DUMP_PATH], timeout=20)
            text = xml.decode("utf-8", "replace")
            if "<hierarchy" in text:
                return text
        except (CaptureError, subprocess.TimeoutExpired):
            pass
        time.sleep(0.4 * (attempt + 1))
    return None


# ── run layout ─────────────────────────────────────────────────────────────────


@dataclass
class ScreenRecord:
    """One captured screen: the picture, the tree, and when they were taken."""

    index: int
    t_ms: int
    png: str
    xml: str | None
    delta: float
    labels: list[str] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)


class RunPaths:
    """Everything for one session lives under a single directory.

    Self-contained on purpose: a run can be copied, archived or deleted without leaving strays,
    and `analyse` can be re-run against it long after the phone is gone.
    """

    def __init__(self, root: Path, label: str):
        stamp = time.strftime("%Y-%m-%d_%H%M%S")
        safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in label)[:40] or "run"
        self.dir = Path(root) / f"{stamp}-{safe}"
        self.screens = self.dir / "screens"
        self.crops = self.dir / "crops"
        self.video = self.dir / "video.mkv"
        self.manifest = self.dir / "manifest.json"
        self.state = self.dir / "state.json"

    def create(self) -> "RunPaths":
        self.dir.mkdir(parents=True, exist_ok=True)
        self.screens.mkdir(parents=True, exist_ok=True)
        self.crops.mkdir(parents=True, exist_ok=True)
        return self

    @classmethod
    def attach(cls, run_dir: Path) -> "RunPaths":
        """Bind to an existing run folder without minting a new timestamp.

        The detached `_run` worker is handed a directory that `start` already created; without
        this it would invent a second, empty one alongside.
        """
        obj = cls.__new__(cls)
        obj.dir = Path(run_dir)
        obj.screens = obj.dir / "screens"
        obj.crops = obj.dir / "crops"
        obj.video = obj.dir / "video.mkv"
        obj.manifest = obj.dir / "manifest.json"
        obj.state = obj.dir / "state.json"
        return obj.create()


# ── the session ────────────────────────────────────────────────────────────────


class CaptureSession:
    """Owns the recorder process, the polling loop and the manifest."""

    def __init__(
        self,
        device: DeviceInfo,
        paths: RunPaths,
        *,
        poll_interval: float = 0.5,
        threshold: float = 0.035,
        dump_trees: bool = True,
        record_video: bool = True,
        capture_mic: bool = True,
    ):
        self.device = device
        self.paths = paths
        self.poll_interval = poll_interval
        self.dump_trees = dump_trees
        self.record_video = record_video
        self.capture_mic = capture_mic
        self.watcher = ScreenWatcher(threshold=threshold)
        self.records: list[ScreenRecord] = []
        self.started_at = 0.0
        self._recorder: subprocess.Popen[bytes] | None = None
        self._running = False

    # -- time ----------------------------------------------------------------

    def t_ms(self) -> int:
        return int((time.monotonic() - self.started_at) * 1000)

    # -- recorder ------------------------------------------------------------

    def _scrcpy_command(self) -> list[str]:
        """scrcpy records video *and* the phone microphone into one file, sharing one clock.

        `--no-*-playback` keeps it headless: the user is holding the phone, so a mirror window on
        the laptop would be wasted pixels and a wasted decode.
        """
        exe = shutil.which("scrcpy")
        if exe is None:
            raise CaptureError("scrcpy is not on PATH -- it is what records video with audio")
        cmd = [
            exe, "-s", self.device.serial,
            "--no-video-playback", "--no-audio-playback",
            f"--record={self.paths.video}", "--record-format=mkv",
        ]
        if self.capture_mic:
            # The phone's own microphone: the user narrates into the phone they are already holding.
            cmd += ["--audio-source=mic", "--audio-codec=aac"]
        return cmd

    def start(self) -> None:
        self.paths.create()
        self.started_at = time.monotonic()

        # Confirm we can actually see the screen BEFORE recording for two minutes.
        first = screencap(self.device.serial)
        img = load_image(first)
        if is_blank(img):
            raise CaptureError(
                "The screen captured as one flat colour, which means this app has blocked screen "
                "capture (FLAG_SECURE). Nothing can be recorded or dumped for it -- banking and "
                "DRM apps behave this way. No run directory was kept."
            )

        if self.record_video:
            self._recorder = subprocess.Popen(
                self._scrcpy_command(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                start_new_session=True,  # own process group, so stop() can kill the whole tree
            )

        self._write_state(status="running")
        # The frame we just proved is visible is the first screen worth keeping.
        self._capture(img, delta=1.0, first=True)
        self._running = True

    def stop(self) -> Path:
        self._running = False
        if self._recorder and self._recorder.poll() is None:
            try:
                os.killpg(os.getpgid(self._recorder.pid), signal.SIGINT)
                self._recorder.wait(timeout=15)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                self._recorder.kill()
        self._write_manifest(status="complete")
        self._write_state(status="stopped")
        return self.paths.dir

    # -- capture -------------------------------------------------------------

    def _capture(self, image, delta: float, first: bool = False) -> ScreenRecord:
        index = len(self.records) + 1
        t = self.t_ms()
        png_path = self.paths.screens / f"{index:04d}.png"
        png_path.write_bytes(image_to_png_bytes(image))

        xml_path = None
        labels: list[str] = []
        counts: dict[str, int] = {}
        if self.dump_trees:
            xml_text = uiautomator_dump(self.device.serial)
            if xml_text:
                xml_path = self.paths.screens / f"{index:04d}.xml"
                xml_path.write_text(xml_text, encoding="utf-8")
                tree = UiTree.parse(xml_text, (self.device.width, self.device.height))
                labels = [n.label for n in tree.meaningful() if n.label][:40]
                counts = tree.counts()

        rec = ScreenRecord(
            index=index, t_ms=t,
            png=str(png_path.relative_to(self.paths.dir)),
            xml=str(xml_path.relative_to(self.paths.dir)) if xml_path else None,
            delta=round(delta, 5), labels=labels, counts=counts,
        )
        self.records.append(rec)
        self._write_manifest(status="running")
        self._write_state(status="running")
        return rec

    def poll_once(self) -> ScreenRecord | None:
        """One iteration. Returns a record only when a new screen was captured."""
        data = screencap(self.device.serial)
        image = load_image(data)
        verdict = self.watcher.observe(image)
        if not verdict.changed:
            return None
        return self._capture(image, delta=verdict.delta)

    def run_loop(self, max_seconds: float | None = None, on_screen=None) -> None:
        deadline = time.monotonic() + max_seconds if max_seconds else None
        while self._running:
            if deadline and time.monotonic() > deadline:
                break
            try:
                rec = self.poll_once()
                if rec and on_screen:
                    on_screen(rec)
            except CaptureError:
                # A transient adb hiccup should not end the recording.
                pass
            time.sleep(self.poll_interval)

    # -- persistence ---------------------------------------------------------

    def _write_manifest(self, status: str) -> None:
        payload = {
            "status": status,
            "device": asdict(self.device),
            "effective_density": self.device.effective_density,
            "video": self.paths.video.name if self.record_video else None,
            "audio": "phone-mic" if self.capture_mic else None,
            "screens": [asdict(r) for r in self.records],
        }
        self.paths.manifest.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def _write_state(self, status: str) -> None:
        """Written continuously so `status` and `stop` work from another shell."""
        self.paths.state.write_text(json.dumps({
            "status": status,
            "pid": os.getpid(),
            "started_at": self.started_at,
            "screens": len(self.records),
            "run_dir": str(self.paths.dir),
        }, indent=2), encoding="utf-8")


def image_to_png_bytes(image) -> bytes:
    import io

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()
