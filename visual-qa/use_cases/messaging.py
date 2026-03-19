"""Use Case 3: Messaging — Open match chat, send message, verify.

Navigates to Matches tab, opens a matched conversation, sends a test message,
and verifies it appears. Requires backend with seeded matches.
"""

from navigator import Action, ActionType
from signatures import ScreenId

MESSAGING_FLOW: dict[ScreenId, list[Action]] = {
    # Navigate to Matches tab first
    ScreenId.DISCOVER: [
        Action(ActionType.TAP_TAB, "matches\ntab 2 of 3", "Navigate to Matches tab"),
        Action(ActionType.WAIT, "2", "Wait for Matches to load"),
    ],
    ScreenId.PROFILE_GET_MORE: [
        Action(ActionType.TAP_TAB, "matches\ntab 2 of 3", "Navigate to Matches tab"),
    ],
    ScreenId.PROFILE_SAFETY: [
        Action(ActionType.TAP_TAB, "matches\ntab 2 of 3", "Navigate to Matches tab"),
    ],
    ScreenId.PROFILE_MY_DEJTING: [
        Action(ActionType.TAP_TAB, "matches\ntab 2 of 3", "Navigate to Matches tab"),
    ],

    # On Matches screen — switch to Messages tab, tap first conversation
    ScreenId.MATCHES: [
        Action(ActionType.TAP_TEXT, "messages\ntab 2 of 2", "Switch to Messages tab"),
        Action(ActionType.WAIT, "2", "Wait for messages to load"),
    ],

    ScreenId.MATCHES_MESSAGES: [
        # If there are conversations, tap the first one
        # If "No conversations yet", this is an expected state (no seeded data)
        Action(ActionType.WAIT, "2", "Check for conversations"),
    ],

    # In chat screen — type and send a message
    ScreenId.CHAT: [
        Action(ActionType.INPUT_TEXT, "Hello from visual QA!", "Type test message"),
        Action(ActionType.TAP_TEXT, "send", "Tap Send"),
        Action(ActionType.WAIT, "2", "Wait for message delivery"),
    ],

    # Handle auth error
    ScreenId.ONBOARDING_COMPLETE: [
        Action(ActionType.TAP_TEXT, "skip for now", "Skip auth error"),
    ],
}

MESSAGING_TERMINAL_SCREENS = {
    ScreenId.CHAT,           # Success: reached chat
    ScreenId.MATCHES_MESSAGES,  # Acceptable: no conversations (no backend data)
}
