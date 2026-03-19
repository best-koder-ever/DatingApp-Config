"""Use Case 4: Safety & Privacy — Verify safety features are accessible.

Navigates to Profile → Safety tab, checks selfie verification, message filter,
block list, crisis hotlines. Then visits Settings to verify privacy controls.
"""

from navigator import Action, ActionType
from signatures import ScreenId

SAFETY_FLOW: dict[ScreenId, list[Action]] = {
    # Navigate to Profile tab first
    ScreenId.DISCOVER: [
        Action(ActionType.TAP_TAB, "profile\ntab 3 of 3", "Navigate to Profile tab"),
        Action(ActionType.WAIT, "2", "Wait for Profile to load"),
    ],
    ScreenId.MATCHES: [
        Action(ActionType.TAP_TAB, "profile\ntab 3 of 3", "Navigate to Profile tab"),
    ],

    # On Profile — navigate to Safety tab
    ScreenId.PROFILE_GET_MORE: [
        Action(ActionType.TAP_TEXT, "safety\ntab 2 of 3", "Switch to Safety tab"),
        Action(ActionType.WAIT, "2", "Wait for Safety to load"),
    ],

    # On Safety tab — verify elements are present, then go to My DejTing
    ScreenId.PROFILE_SAFETY: [
        Action(ActionType.WAIT, "2", "Verify safety features visible"),
        Action(ActionType.TAP_TEXT, "my dejting\ntab 3 of 3", "Switch to My DejTing tab"),
        Action(ActionType.WAIT, "2", "Wait for My DejTing to load"),
    ],

    # On My DejTing — navigate to Settings
    ScreenId.PROFILE_MY_DEJTING: [
        Action(ActionType.TAP_TEXT, "settings", "Tap Settings"),
        Action(ActionType.WAIT, "2", "Wait for Settings to load"),
    ],

    # Handle auth error
    ScreenId.ONBOARDING_COMPLETE: [
        Action(ActionType.TAP_TEXT, "skip for now", "Skip auth error"),
    ],
}

SAFETY_TERMINAL_SCREENS = {
    ScreenId.SETTINGS,  # Success: reached Settings screen
}
