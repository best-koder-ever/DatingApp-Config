"""Semantic Navigation Engine — state machine that drives the app.

Detects the current screen via uiautomator XML signatures, looks up the
appropriate action, executes it via ADB, captures a screenshot, and repeats.

Text-based navigation: taps elements by content-desc text, never pixel coords.
State-machine driven: survives screen reordering, additions, and removals.
"""

import json
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Callable

from adb_client import AdbClient
from element_finder import find_by_text, find_input_field, get_all_elements
from signatures import ScreenId, detect_screen


class ActionType(Enum):
    TAP_TEXT = auto()      # Tap element matching text
    INPUT_TEXT = auto()    # Type text into focused field
    SWIPE_LEFT = auto()    # Swipe left (pass)
    SWIPE_RIGHT = auto()   # Swipe right (like)
    PRESS_BACK = auto()    # Press back button
    WAIT = auto()          # Wait N seconds
    TAP_COORD = auto()     # Tap specific coordinates (fallback)
    SKIP = auto()          # Skip this screen (no action needed)
    TAP_TAB = auto()       # Tap a bottom nav tab by text


@dataclass
class Action:
    action_type: ActionType
    value: str = ""       # Text to find/type, or seconds to wait
    description: str = "" # Human-readable description of what this does


@dataclass
class StepResult:
    screen: ScreenId
    action: Action | None
    screenshot_path: str = ""
    xml_path: str = ""
    success: bool = True
    error: str = ""
    duration_ms: int = 0


@dataclass
class UseCaseResult:
    name: str
    steps: list[StepResult] = field(default_factory=list)
    success: bool = True
    error: str = ""
    duration_ms: int = 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "success": self.success,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "steps": [
                {
                    "screen": s.screen.name,
                    "action": s.action.description if s.action else "none",
                    "success": s.success,
                    "error": s.error,
                    "screenshot": s.screenshot_path,
                    "duration_ms": s.duration_ms,
                }
                for s in self.steps
            ],
        }


class Navigator:
    """State machine that navigates through app screens via ADB."""

    def __init__(
        self,
        adb: AdbClient,
        output_dir: str | Path = "/app/test-results",
        settle_time: float = 2.0,
        max_retries: int = 3,
    ):
        self.adb = adb
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.settle_time = settle_time
        self.max_retries = max_retries
        self._step_counter = 0

    def _capture(self, use_case: str, label: str) -> tuple[str, str]:
        """Capture screenshot + UI dump. Returns (screenshot_path, xml_path)."""
        self._step_counter += 1
        prefix = f"{self._step_counter:03d}-{use_case}-{label}"
        ss_path = str(self.output_dir / f"{prefix}.png")
        xml_path = str(self.output_dir / f"{prefix}.xml")

        try:
            self.adb.save_screenshot(ss_path)
        except Exception as e:
            ss_path = f"ERROR: {e}"

        try:
            xml = self.adb.ui_dump()
            Path(xml_path).write_text(xml, encoding="utf-8")
        except Exception as e:
            xml_path = f"ERROR: {e}"

        return ss_path, xml_path

    def detect_current_screen(self) -> tuple[ScreenId, str]:
        """Get current screen ID and raw XML."""
        xml = self.adb.ui_dump()
        screen_id, score = detect_screen(xml)
        return screen_id, xml

    def execute_action(self, action: Action, xml: str) -> bool:
        """Execute a single action. Returns True if action was performed."""
        if action.action_type == ActionType.TAP_TEXT:
            pos = find_by_text(xml, action.value)
            if pos:
                self.adb.tap(pos[0], pos[1])
                return True
            return False

        elif action.action_type == ActionType.INPUT_TEXT:
            pos = find_input_field(xml)
            if pos:
                self.adb.tap(pos[0], pos[1])
                time.sleep(0.3)
            self.adb.input_text(action.value)
            self.adb.hide_keyboard()
            return True

        elif action.action_type == ActionType.SWIPE_LEFT:
            self.adb.swipe_left()
            return True

        elif action.action_type == ActionType.SWIPE_RIGHT:
            self.adb.swipe_right()
            return True

        elif action.action_type == ActionType.PRESS_BACK:
            self.adb.press_back()
            return True

        elif action.action_type == ActionType.WAIT:
            time.sleep(float(action.value))
            return True

        elif action.action_type == ActionType.TAP_COORD:
            parts = action.value.split(",")
            self.adb.tap(int(parts[0]), int(parts[1]))
            return True

        elif action.action_type == ActionType.TAP_TAB:
            pos = find_by_text(xml, action.value)
            if pos:
                self.adb.tap(pos[0], pos[1])
                return True
            return False

        elif action.action_type == ActionType.SKIP:
            return True

        return False

    def run_flow(
        self,
        name: str,
        flow: dict[ScreenId, list[Action]],
        terminal_screens: set[ScreenId] | None = None,
        max_steps: int = 50,
    ) -> UseCaseResult:
        """Run a use case flow — state machine loop.

        Args:
            name: Use case name for reporting
            flow: Mapping of ScreenId → list of Actions to perform on that screen
            terminal_screens: Set of ScreenIds that indicate the flow is complete
            max_steps: Safety limit to prevent infinite loops
        """
        result = UseCaseResult(name=name)
        start_time = time.time()
        last_screen = None
        stuck_count = 0

        for step_num in range(max_steps):
            step_start = time.time()

            # Detect current screen
            try:
                screen_id, xml = self.detect_current_screen()
            except Exception as e:
                result.steps.append(StepResult(
                    screen=ScreenId.UNKNOWN, action=None,
                    success=False, error=f"UI dump failed: {e}"
                ))
                result.success = False
                result.error = f"UI dump failed at step {step_num}"
                break

            # Check if we're at a terminal screen
            if terminal_screens and screen_id in terminal_screens:
                ss_path, xml_path = self._capture(name, f"terminal-{screen_id.name}")
                result.steps.append(StepResult(
                    screen=screen_id, action=Action(ActionType.SKIP, description="Terminal screen reached"),
                    screenshot_path=ss_path, xml_path=xml_path,
                    duration_ms=int((time.time() - step_start) * 1000),
                ))
                break

            # Check if stuck
            if screen_id == last_screen:
                stuck_count += 1
                if stuck_count >= self.max_retries:
                    ss_path, xml_path = self._capture(name, f"stuck-{screen_id.name}")
                    result.steps.append(StepResult(
                        screen=screen_id, action=None,
                        screenshot_path=ss_path, xml_path=xml_path,
                        success=False, error=f"Stuck on {screen_id.name} for {stuck_count} iterations",
                        duration_ms=int((time.time() - step_start) * 1000),
                    ))
                    # Try pressing back as escape
                    self.adb.press_back()
                    time.sleep(self.settle_time)
                    stuck_count = 0
                    continue
            else:
                stuck_count = 0
            last_screen = screen_id

            # Look up actions for this screen
            actions = flow.get(screen_id)
            if not actions:
                # Unknown screen in this flow — capture and skip
                if screen_id == ScreenId.UNKNOWN:
                    ss_path, xml_path = self._capture(name, f"unknown-{step_num}")
                    result.steps.append(StepResult(
                        screen=screen_id, action=None,
                        screenshot_path=ss_path, xml_path=xml_path,
                        success=False, error="Unknown screen encountered",
                        duration_ms=int((time.time() - step_start) * 1000),
                    ))
                    time.sleep(self.settle_time)
                    continue
                # Known screen but not in this flow — skip it
                ss_path, xml_path = self._capture(name, f"skip-{screen_id.name}")
                result.steps.append(StepResult(
                    screen=screen_id,
                    action=Action(ActionType.SKIP, description=f"Screen {screen_id.name} not in flow"),
                    screenshot_path=ss_path, xml_path=xml_path,
                    duration_ms=int((time.time() - step_start) * 1000),
                ))
                time.sleep(self.settle_time)
                continue

            # Execute all actions for this screen
            for action in actions:
                ss_path, xml_path = self._capture(name, f"{screen_id.name}-{action.description}")
                ok = self.execute_action(action, xml)
                step_result = StepResult(
                    screen=screen_id, action=action,
                    screenshot_path=ss_path, xml_path=xml_path,
                    success=ok,
                    error="" if ok else f"Action failed: {action.description}",
                    duration_ms=int((time.time() - step_start) * 1000),
                )
                result.steps.append(step_result)
                if not ok:
                    result.success = False

                time.sleep(self.settle_time)
                # Re-dump XML after action for next action in same screen
                try:
                    xml = self.adb.ui_dump()
                except Exception:
                    pass

        result.duration_ms = int((time.time() - start_time) * 1000)
        # If we exited the loop without terminal, it's a timeout
        if not terminal_screens or (result.steps and result.steps[-1].screen not in (terminal_screens or set())):
            if not result.error:
                result.error = f"Flow did not reach terminal screen within {max_steps} steps"
                result.success = False

        return result
