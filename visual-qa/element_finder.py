"""Find UI elements in uiautomator XML by text content.

Parses the XML hierarchy and locates elements by matching content-desc
or text attributes. Returns center coordinates for ADB tap commands.
Text-based — never hardcoded pixel coordinates.
"""

import re
from xml.etree import ElementTree


def _parse_bounds(bounds_str: str) -> tuple[int, int, int, int] | None:
    """Parse bounds string '[left,top][right,bottom]' → (left, top, right, bottom)."""
    m = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds_str)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))


def _center(bounds: tuple[int, int, int, int]) -> tuple[int, int]:
    """Calculate center point of a bounds rectangle."""
    left, top, right, bottom = bounds
    return (left + right) // 2, (top + bottom) // 2


def find_by_text(xml_string: str, text: str, clickable_only: bool = False) -> tuple[int, int] | None:
    """Find element whose content-desc or text contains the given string.

    Returns center (x, y) of the first matching element, or None.
    Case-insensitive matching.
    """
    try:
        root = ElementTree.fromstring(xml_string)
    except ElementTree.ParseError:
        return None

    text_lower = text.lower()
    for elem in root.iter("node"):
        if clickable_only and elem.get("clickable") != "true":
            continue
        content_desc = (elem.get("content-desc") or "").lower()
        elem_text = (elem.get("text") or "").lower()
        if text_lower in content_desc or text_lower in elem_text:
            bounds = _parse_bounds(elem.get("bounds", ""))
            if bounds:
                return _center(bounds)
    return None


def find_all_by_text(xml_string: str, text: str) -> list[tuple[int, int]]:
    """Find ALL elements matching text. Returns list of (x, y) centers."""
    try:
        root = ElementTree.fromstring(xml_string)
    except ElementTree.ParseError:
        return []

    results = []
    text_lower = text.lower()
    for elem in root.iter("node"):
        content_desc = (elem.get("content-desc") or "").lower()
        elem_text = (elem.get("text") or "").lower()
        if text_lower in content_desc or text_lower in elem_text:
            bounds = _parse_bounds(elem.get("bounds", ""))
            if bounds:
                results.append(_center(bounds))
    return results


def find_clickable_by_text(xml_string: str, text: str) -> tuple[int, int] | None:
    """Find a clickable element by text. Shorthand for find_by_text(..., clickable_only=True)."""
    return find_by_text(xml_string, text, clickable_only=True)


def find_input_field(xml_string: str) -> tuple[int, int] | None:
    """Find the first focused EditText or text input field."""
    try:
        root = ElementTree.fromstring(xml_string)
    except ElementTree.ParseError:
        return None

    # First try focused EditText
    for elem in root.iter("node"):
        if elem.get("class", "").endswith("EditText") and elem.get("focused") == "true":
            bounds = _parse_bounds(elem.get("bounds", ""))
            if bounds:
                return _center(bounds)

    # Then any EditText
    for elem in root.iter("node"):
        if elem.get("class", "").endswith("EditText"):
            bounds = _parse_bounds(elem.get("bounds", ""))
            if bounds:
                return _center(bounds)

    return None


def find_by_class(xml_string: str, class_name: str) -> list[tuple[int, int]]:
    """Find all elements of a given class. Returns list of (x, y) centers."""
    try:
        root = ElementTree.fromstring(xml_string)
    except ElementTree.ParseError:
        return []

    results = []
    for elem in root.iter("node"):
        if class_name in (elem.get("class") or ""):
            bounds = _parse_bounds(elem.get("bounds", ""))
            if bounds:
                results.append(_center(bounds))
    return results


def get_all_elements(xml_string: str) -> list[dict]:
    """Get all elements with their properties. Useful for debugging."""
    try:
        root = ElementTree.fromstring(xml_string)
    except ElementTree.ParseError:
        return []

    elements = []
    for elem in root.iter("node"):
        desc = elem.get("content-desc", "")
        text = elem.get("text", "")
        if not desc and not text:
            continue
        bounds = _parse_bounds(elem.get("bounds", ""))
        if bounds:
            cx, cy = _center(bounds)
            elements.append({
                "content_desc": desc,
                "text": text,
                "class": elem.get("class", ""),
                "clickable": elem.get("clickable") == "true",
                "bounds": bounds,
                "center": (cx, cy),
            })
    return elements
