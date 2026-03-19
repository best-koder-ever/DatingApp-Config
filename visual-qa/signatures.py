"""Screen signature detection from uiautomator XML dumps.

Detects which app screen is currently displayed by matching content-desc
text patterns in the UI hierarchy XML. Text-based (not coordinate-based),
so it survives layout changes and screen reordering.
"""

import re
from enum import Enum, auto
from xml.etree import ElementTree


class ScreenId(Enum):
    # Onboarding wizard screens (17)
    WELCOME = auto()
    PHONE_ENTRY = auto()
    SMS_CODE = auto()
    COMMUNITY_GUIDELINES = auto()
    FIRST_NAME = auto()
    BIRTHDAY = auto()
    GENDER = auto()
    ORIENTATION = auto()
    MATCH_PREFERENCES = auto()
    AGE_RANGE = auto()
    RELATIONSHIP_GOALS = auto()
    LIFESTYLE = auto()
    INTERESTS = auto()
    ABOUT_ME = auto()
    PHOTOS = auto()
    LOCATION_PERMISSION = auto()
    NOTIFICATION_PERMISSION = auto()

    # Post-onboarding screens
    ONBOARDING_COMPLETE = auto()
    DISCOVER = auto()
    MATCHES = auto()
    MATCHES_MESSAGES = auto()
    PROFILE_GET_MORE = auto()
    PROFILE_SAFETY = auto()
    PROFILE_MY_DEJTING = auto()
    SETTINGS = auto()
    CHAT = auto()

    # Fallback
    UNKNOWN = auto()


# Each signature is a list of (pattern, weight) tuples.
# A screen matches if its total weighted score is highest among all candidates.
# Patterns are matched case-insensitively against all content-desc values.
SIGNATURES: dict[ScreenId, list[tuple[str, float]]] = {
    ScreenId.WELCOME: [
        ("welcome to dejting", 5.0),
        ("create account", 3.0),
        ("log in", 2.0),
        ("get started", 3.0),
    ],
    ScreenId.PHONE_ENTRY: [
        ("phone number", 5.0),
        ("country code", 3.0),
        ("enter your phone", 4.0),
        ("continue", 1.0),
    ],
    ScreenId.SMS_CODE: [
        ("verification code", 5.0),
        ("sms code", 5.0),
        ("enter the code", 4.0),
        ("resend", 2.0),
        ("digit", 1.0),
    ],
    ScreenId.COMMUNITY_GUIDELINES: [
        ("community guidelines", 5.0),
        ("house rules", 5.0),
        ("be yourself", 3.0),
        ("play it cool", 3.0),
        ("stay safe", 3.0),
        ("be proactive", 3.0),
    ],
    ScreenId.FIRST_NAME: [
        ("first name", 5.0),
        ("what's your name", 5.0),
        ("your name", 3.0),
    ],
    ScreenId.BIRTHDAY: [
        ("birthday", 5.0),
        ("date of birth", 5.0),
        ("when were you born", 4.0),
        ("year", 1.0),
        ("month", 1.0),
    ],
    ScreenId.GENDER: [
        ("what's your\ngender", 10.0),
        ("gender", 3.0),
        ("man", 2.0),
        ("woman", 2.0),
        ("show my gender", 4.0),
    ],
    ScreenId.ORIENTATION: [
        ("sexual\norientation", 10.0),
        ("orientation", 3.0),
        ("straight", 3.0),
        ("gay", 2.0),
        ("lesbian", 2.0),
        ("bisexual", 2.0),
        ("asexual", 2.0),
        ("show my orientation", 3.0),
    ],
    ScreenId.MATCH_PREFERENCES: [
        ("interested in", 5.0),
        ("show me", 4.0),
        ("men", 2.0),
        ("women", 2.0),
        ("everyone", 2.0),
        ("who would you like to date", 5.0),
    ],
    ScreenId.AGE_RANGE: [
        ("age range", 5.0),
        ("age preference", 5.0),
        ("18", 1.0),
        ("slider", 1.0),
    ],
    ScreenId.RELATIONSHIP_GOALS: [
        ("relationship", 3.0),
        ("looking for", 4.0),
        ("long-term", 2.0),
        ("casual", 2.0),
        ("friendship", 2.0),
        ("marriage", 2.0),
    ],
    ScreenId.LIFESTYLE: [
        ("lifestyle habits", 10.0),
        ("lifestyle", 3.0),
        ("smoke", 3.0),
        ("exercise", 3.0),
        ("pets", 3.0),
        ("how often do you smoke", 4.0),
        ("65%", 2.0),
    ],
    ScreenId.INTERESTS: [
        ("interests", 4.0),
        ("outdoors", 3.0),
        ("adventure", 2.0),
        ("values", 2.0),
        ("causes", 2.0),
        ("0/10", 2.0),
        ("/10", 1.0),
    ],
    ScreenId.ABOUT_ME: [
        ("what else makes\nyou, you", 10.0),
        ("about me", 4.0),
        ("communication style", 5.0),
        ("love language", 5.0),
        ("authenticity attracts", 4.0),
        ("76%", 2.0),
    ],
    ScreenId.PHOTOS: [
        ("add photos", 10.0),
        ("add at least 2 photos", 8.0),
        ("profile photo", 3.0),
        ("/6 photos", 4.0),
        ("skip photos", 3.0),
        ("82%", 2.0),
    ],
    ScreenId.LOCATION_PERMISSION: [
        ("enable location", 10.0),
        ("we use your location", 5.0),
        ("skip location", 5.0),
        ("potential matches nearby", 4.0),
        ("88%", 2.0),
    ],
    ScreenId.NOTIFICATION_PERMISSION: [
        ("enable notifications", 10.0),
        ("never miss a match", 8.0),
        ("skip", 1.0),
        ("94%", 2.0),
    ],
    ScreenId.ONBOARDING_COMPLETE: [
        ("something went wrong", 5.0),
        ("not authenticated", 5.0),
        ("try again", 3.0),
        ("skip for now", 3.0),
        ("100%", 2.0),
    ],
    ScreenId.DISCOVER: [
        ("discover\ntab 1 of 3", 10.0),
        ("you've seen everyone", 5.0),
        ("check back later", 3.0),
        ("refresh", 2.0),
    ],
    ScreenId.MATCHES: [
        ("matches\ntab 2 of 3", 5.0),
        ("new matches\ntab 1 of 2", 8.0),
        ("no matches yet", 4.0),
        ("keep swiping", 3.0),
        ("auth required", 2.0),
    ],
    ScreenId.MATCHES_MESSAGES: [
        ("messages\ntab 2 of 2", 10.0),
        ("no conversations yet", 5.0),
    ],
    ScreenId.PROFILE_GET_MORE: [
        ("get more\ntab 1 of 3", 10.0),
        ("dejting plus", 8.0),
        ("unlimited sparks", 4.0),
        ("spotlight", 3.0),
        ("upgrade", 3.0),
    ],
    ScreenId.PROFILE_SAFETY: [
        ("safety\ntab 2 of 3", 10.0),
        ("selfie verification", 4.0),
        ("message filter", 3.0),
        ("block list", 3.0),
        ("crisis hotline", 3.0),
    ],
    ScreenId.PROFILE_MY_DEJTING: [
        ("my dejting\ntab 3 of 3", 10.0),
        ("voice prompt", 4.0),
        ("dating tips", 3.0),
        ("help centre", 3.0),
        ("fresh start", 3.0),
    ],
    ScreenId.SETTINGS: [
        ("settings", 5.0),
        ("account", 3.0),
        ("discovery settings", 4.0),
        ("notifications", 2.0),
        ("profile display", 3.0),
        ("logout", 3.0),
        ("distance preference", 3.0),
    ],
    ScreenId.CHAT: [
        ("type a message", 5.0),
        ("send", 2.0),
        ("message", 2.0),
    ],
}


def extract_content_descs(xml_string: str) -> list[str]:
    """Extract all non-empty content-desc values from uiautomator XML."""
    try:
        root = ElementTree.fromstring(xml_string)
    except ElementTree.ParseError:
        return []
    descs = []
    for elem in root.iter():
        desc = elem.get("content-desc", "")
        if desc:
            # uiautomator encodes newlines as &#10; — ElementTree decodes them
            descs.append(desc)
    return descs


def detect_screen(xml_string: str) -> tuple[ScreenId, float]:
    """Detect which screen the XML hierarchy represents.

    Returns (ScreenId, confidence_score). Higher score = more confident.
    Returns (UNKNOWN, 0.0) if no signature matches above threshold.
    """
    descs = extract_content_descs(xml_string)
    if not descs:
        return ScreenId.UNKNOWN, 0.0

    all_text = "\n".join(descs).lower()

    scores: dict[ScreenId, float] = {}
    for screen_id, patterns in SIGNATURES.items():
        score = 0.0
        for pattern, weight in patterns:
            if pattern.lower() in all_text:
                score += weight
        if score > 0:
            scores[screen_id] = score

    if not scores:
        return ScreenId.UNKNOWN, 0.0

    best = max(scores, key=scores.get)
    return best, scores[best]


def detect_screen_from_file(xml_path: str) -> tuple[ScreenId, float]:
    """Convenience: detect screen from an XML file path."""
    with open(xml_path, "r", encoding="utf-8") as f:
        return detect_screen(f.read())
