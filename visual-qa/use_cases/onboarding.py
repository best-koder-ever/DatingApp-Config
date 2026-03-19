"""Use Case 1: Onboarding — 17 wizard screens.

Navigates through the entire registration/onboarding wizard from Welcome
to Notification Permission. Fills in test data and advances through each step.
"""

from navigator import Action, ActionType
from signatures import ScreenId

# Actions to perform on each wizard screen.
# State machine: when screen X is detected, execute these actions in order.
ONBOARDING_FLOW: dict[ScreenId, list[Action]] = {
    ScreenId.WELCOME: [
        Action(ActionType.TAP_TEXT, "get started", "Tap Get Started"),
    ],
    ScreenId.PHONE_ENTRY: [
        Action(ActionType.INPUT_TEXT, "0701234567", "Enter phone number"),
        Action(ActionType.TAP_TEXT, "continue", "Tap Continue"),
    ],
    ScreenId.SMS_CODE: [
        # In dev mode, skip verification or enter test code
        Action(ActionType.INPUT_TEXT, "123456", "Enter verification code"),
        Action(ActionType.WAIT, "3", "Wait for verification"),
    ],
    ScreenId.COMMUNITY_GUIDELINES: [
        Action(ActionType.TAP_TEXT, "agree", "Accept community guidelines"),
    ],
    ScreenId.FIRST_NAME: [
        Action(ActionType.INPUT_TEXT, "TestUser", "Enter first name"),
        Action(ActionType.TAP_TEXT, "next", "Tap Next"),
    ],
    ScreenId.BIRTHDAY: [
        # Birthday has dropdowns — tap Next (pre-filled or tap a date)
        Action(ActionType.TAP_TEXT, "next", "Tap Next on birthday"),
    ],
    ScreenId.GENDER: [
        Action(ActionType.TAP_TEXT, "man", "Select Man"),
        Action(ActionType.TAP_TEXT, "next", "Tap Next"),
    ],
    ScreenId.ORIENTATION: [
        Action(ActionType.TAP_TEXT, "straight", "Select Straight"),
        Action(ActionType.TAP_TEXT, "next", "Tap Next"),
    ],
    ScreenId.MATCH_PREFERENCES: [
        Action(ActionType.TAP_TEXT, "women", "Select Women"),
        Action(ActionType.TAP_TEXT, "next", "Tap Next"),
    ],
    ScreenId.AGE_RANGE: [
        # Age range has sliders — just tap Next with defaults
        Action(ActionType.TAP_TEXT, "next", "Tap Next on age range"),
    ],
    ScreenId.RELATIONSHIP_GOALS: [
        Action(ActionType.TAP_TEXT, "long-term", "Select Long-term relationship"),
        Action(ActionType.TAP_TEXT, "next", "Tap Next"),
    ],
    ScreenId.LIFESTYLE: [
        Action(ActionType.TAP_TEXT, "skip", "Skip lifestyle"),
    ],
    ScreenId.INTERESTS: [
        Action(ActionType.TAP_TEXT, "skip", "Skip interests"),
    ],
    ScreenId.ABOUT_ME: [
        Action(ActionType.TAP_TEXT, "skip", "Skip about me"),
    ],
    ScreenId.PHOTOS: [
        Action(ActionType.TAP_TEXT, "skip photos", "Skip photos"),
    ],
    ScreenId.LOCATION_PERMISSION: [
        Action(ActionType.TAP_TEXT, "not now", "Skip location for now"),
    ],
    ScreenId.NOTIFICATION_PERMISSION: [
        Action(ActionType.TAP_TEXT, "not now", "Skip notifications for now"),
    ],
    ScreenId.ONBOARDING_COMPLETE: [
        Action(ActionType.TAP_TEXT, "skip for now", "Skip auth error"),
    ],
}

# Flow is complete when we reach the Discover screen (main app)
ONBOARDING_TERMINAL_SCREENS = {
    ScreenId.DISCOVER,
    ScreenId.ONBOARDING_COMPLETE,  # Also terminal if backend is down
}
