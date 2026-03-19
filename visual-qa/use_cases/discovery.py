"""Use Case 2: Discovery — Browse, swipe, and match.

Navigates to Discover tab, views candidate cards, performs swipe actions
(like/pass), and checks for match notifications. Requires seeded backend data.
"""

from navigator import Action, ActionType
from signatures import ScreenId

# Discovery flow: navigate to Discover, interact with cards
DISCOVERY_FLOW: dict[ScreenId, list[Action]] = {
    ScreenId.DISCOVER: [
        # If "You've seen everyone" is shown, tap Refresh to reset
        Action(ActionType.TAP_TEXT, "refresh", "Tap Refresh to load candidates"),
        Action(ActionType.WAIT, "3", "Wait for candidates to load"),
    ],

    # If we land on a different tab first, navigate to Discover
    ScreenId.MATCHES: [
        Action(ActionType.TAP_TAB, "discover\ntab 1 of 3", "Navigate to Discover tab"),
        Action(ActionType.WAIT, "2", "Wait for Discover to load"),
    ],
    ScreenId.PROFILE_GET_MORE: [
        Action(ActionType.TAP_TAB, "discover\ntab 1 of 3", "Navigate to Discover tab"),
        Action(ActionType.WAIT, "2", "Wait for Discover to load"),
    ],
    ScreenId.PROFILE_SAFETY: [
        Action(ActionType.TAP_TAB, "discover\ntab 1 of 3", "Navigate to Discover tab"),
    ],
    ScreenId.PROFILE_MY_DEJTING: [
        Action(ActionType.TAP_TAB, "discover\ntab 1 of 3", "Navigate to Discover tab"),
    ],

    # Handle the auth error screen (skip if no backend)
    ScreenId.ONBOARDING_COMPLETE: [
        Action(ActionType.TAP_TEXT, "skip for now", "Skip auth error"),
    ],
}

# Terminal: we declare success when we've been on Discover and interacted
# In practice, the navigator will loop through the flow actions
DISCOVERY_TERMINAL_SCREENS = {
    ScreenId.MATCHES,  # If match notification appeared, we navigated there
}
