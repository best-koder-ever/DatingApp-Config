"""Parse and query Android `uiautomator dump` XML.

The dump is the accessibility tree, not pixels: every node carries the label a screen reader
would speak, the role, and the exact hit rectangle. That is what makes "tap the thing called
X" reliable where screenshot matching is not.

Geometry note: uiautomator reports device pixels. Converting to dp requires the *effective*
density, which is not always `wm density`'s physical value -- this device reports physical 450
with an override of 480, and the override is what the UI is actually laid out in. Always pass
the override when you have it.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Iterator

# uiautomator escapes newlines and friends as numeric entities, which ElementTree leaves in the
# raw attribute text; `&#10;` shows up verbatim in content-desc otherwise.
_ENTITY = re.compile(r"&#(\d+);|&#x([0-9a-fA-F]+);")
_BOUNDS = re.compile(r"\[(-?\d+),(-?\d+)\]\[(-?\d+),(-?\d+)\]")


def _unescape(value: str) -> str:
    def sub(m: re.Match[str]) -> str:
        code = int(m.group(1)) if m.group(1) else int(m.group(2), 16)
        return chr(code)

    return _ENTITY.sub(sub, value)


@dataclass
class Node:
    """One accessibility node."""

    index: int
    cls: str
    text: str
    desc: str
    resource_id: str
    bounds: tuple[int, int, int, int]  # left, top, right, bottom (device px)
    clickable: bool
    enabled: bool
    focusable: bool
    scrollable: bool
    checkable: bool
    checked: bool
    selected: bool
    is_password: bool
    hint: str
    depth: int
    children: list["Node"] = field(default_factory=list)

    # -- identity ---------------------------------------------------------------

    @property
    def label(self) -> str:
        """The best human-readable name: spoken description first, then text.

        content-desc wins because that is the string the app author chose for assistive
        technology, and it is frequently the only label an icon-only control has.
        """
        return self.desc or self.text

    @property
    def rect(self) -> tuple[int, int, int, int]:
        return self.bounds

    @property
    def width(self) -> int:
        return self.bounds[2] - self.bounds[0]

    @property
    def height(self) -> int:
        return self.bounds[3] - self.bounds[1]

    @property
    def area(self) -> int:
        return max(0, self.width) * max(0, self.height)

    @property
    def center(self) -> tuple[int, int]:
        left, top, right, bottom = self.bounds
        return ((left + right) // 2, (top + bottom) // 2)

    def is_editable(self) -> bool:
        return "EditText" in self.cls or self.is_password or bool(self.hint)

    # -- dp --------------------------------------------------------------------

    def size_dp(self, density: int) -> tuple[float, float]:
        """(width, height) in dp. `density` is the *override* value, not the physical one."""
        scale = density / 160.0
        return (self.width / scale, self.height / scale)

    def min_side_dp(self, density: int) -> float:
        w, h = self.size_dp(density)
        return min(w, h)

    def is_on_screen(self, screen_px: tuple[int, int]) -> bool:
        """False for nodes parked entirely outside the viewport (off-screen list rows)."""
        sw, sh = screen_px
        left, top, right, bottom = self.bounds
        return right > 0 and bottom > 0 and left < sw and top < sh


class UiTree:
    """A parsed dump, with the queries the capturer actually needs."""

    def __init__(self, root: Node, screen_px: tuple[int, int]):
        self.root = root
        self.screen_px = screen_px
        self._nodes: list[Node] = list(self._walk(root))

    # -- construction ----------------------------------------------------------

    @classmethod
    def parse(cls, xml_text: str, screen_px: tuple[int, int] = (1080, 2340)) -> "UiTree":
        root_el = ET.fromstring(xml_text)
        root = cls._build(root_el, depth=0, counter=iter(range(10_000)))
        return cls(root, screen_px)

    @classmethod
    def _build(cls, el: ET.Element, depth: int, counter: Iterator[int]) -> Node:
        # uiautomator writes a bare <hierarchy> wrapper when dumping the whole screen.
        if el.tag == "hierarchy":
            children = [cls._build(c, depth, counter) for c in el]
            synthetic = Node(
                index=-1, cls="hierarchy", text="", desc="", resource_id="",
                bounds=(0, 0, 0, 0), clickable=False, enabled=True, focusable=False,
                scrollable=False, checkable=False, checked=False, selected=False,
                is_password=False, hint="", depth=0, children=children,
            )
            return synthetic

        a = el.attrib
        m = _BOUNDS.match(a.get("bounds", ""))
        bounds = tuple(int(g) for g in m.groups()) if m else (0, 0, 0, 0)  # type: ignore[assignment]

        node = Node(
            index=int(a.get("index", -1)),
            cls=a.get("class", ""),
            text=_unescape(a.get("text", "")),
            desc=_unescape(a.get("content-desc", "")),
            resource_id=a.get("resource-id", ""),
            bounds=bounds,  # type: ignore[arg-type]
            clickable=a.get("clickable") == "true",
            enabled=a.get("enabled", "true") == "true",
            focusable=a.get("focusable") == "true",
            scrollable=a.get("scrollable") == "true",
            checkable=a.get("checkable") == "true",
            checked=a.get("checked") == "true",
            selected=a.get("selected") == "true",
            is_password=a.get("password") == "true",
            hint=_unescape(a.get("hint", "")),
            depth=depth,
        )
        node.children = [cls._build(c, depth + 1, counter) for c in el]
        return node

    @staticmethod
    def _walk(node: Node) -> Iterator[Node]:
        yield node
        for child in node.children:
            yield from UiTree._walk(child)

    # -- queries ---------------------------------------------------------------

    @property
    def nodes(self) -> list[Node]:
        """Every node, including the synthetic root."""
        return self._nodes

    def meaningful(self, screen_px: tuple[int, int] | None = None) -> list[Node]:
        """Nodes that carry information: a label, or a clickable/editable role, or real text.

        Filters out the mass of unlabelled `android.view.View` layout wrappers that Flutter
        emits, which are pure noise for both analysis and tapping.
        """
        sp = screen_px or self.screen_px
        out = []
        for n in self._nodes:
            if n.cls == "hierarchy":
                continue
            if n.area == 0:
                continue
            if not n.is_on_screen(sp):
                continue
            if n.label or n.clickable or n.scrollable or n.is_editable():
                out.append(n)
        return out

    def clickable(self, screen_px: tuple[int, int] | None = None) -> list[Node]:
        return [n for n in self.meaningful(screen_px) if n.clickable and n.enabled]

    def text_nodes(self, screen_px: tuple[int, int] | None = None) -> list[Node]:
        """Nodes with visible text, ignoring ones that are also buttons (labels, not copy)."""
        return [n for n in self.meaningful(screen_px) if n.text and not n.clickable]

    def editable(self) -> list[Node]:
        return [n for n in self._nodes if n.is_editable() and n.area > 0]

    def find(self, needle: str, exact: bool = False, case_sensitive: bool = False) -> Node | None:
        """Best node whose label matches. The primitive behind tapping by name.

        Deliberately NOT "first in document order". A Flutter screen typically publishes a
        full-viewport wrapper early -- `content-desc="screen:community"` on a [0,0][1080,2340]
        node -- and a naive substring scan returns that before the actual tab labelled
        "Community". Tapping its centre hits the middle of the screen rather than the tab.

        So rank candidates: exact beats prefix beats substring, a clickable node beats a
        non-clickable one, and a smaller node beats a larger one (it is the more specific
        target). Lowest score wins.
        """
        target = needle if case_sensitive else needle.lower()
        best: tuple[tuple[int, int, int], Node] | None = None

        for n in self._nodes:
            if n.area == 0:
                continue
            hay = n.label if case_sensitive else n.label.lower()
            if hay == target:
                base = 0
            elif exact:
                continue
            elif hay.startswith(target):
                base = 1
            elif target in hay:
                base = 2
            else:
                continue

            score = (base, 0 if n.clickable else 1, n.area)
            if best is None or score < best[0]:
                best = (score, n)

        return best[1] if best else None

    def find_control(self, needle: str, **kw) -> Node | None:
        """Like `find`, but only considers controls a user could actually act on.

        Use this when the intent is "tap it" rather than "read it".
        """
        node = self.find(needle, **kw)
        if node is not None and (node.clickable or node.is_editable()):
            return node
        # Fall back to scanning clickable nodes only, in case the best label match was an
        # inert wrapper that merely mentions the same words.
        for n in self.clickable():
            hay = n.label if kw.get("case_sensitive") else n.label.lower()
            if needle in hay:
                return n
        return node

    def find_all(self, needle: str, case_sensitive: bool = False) -> list[Node]:
        target = needle if case_sensitive else needle.lower()
        out = []
        for n in self._nodes:
            hay = n.label if case_sensitive else n.label.lower()
            if target in hay and n.area > 0:
                out.append(n)
        return out

    # -- summary ---------------------------------------------------------------

    def headings(self, density: int = 480, limit: int = 6) -> list[Node]:
        """Largest text nodes, top-down. A decent proxy for "what this screen is called".

        Size is inferred from rect height because the tree carries no font metrics -- the
        accessibility layer genuinely does not expose type size or weight.
        """
        candidates = [n for n in self.meaningful() if n.text]
        candidates.sort(key=lambda n: (-n.height, n.bounds[1]))
        return candidates[:limit]

    def counts(self) -> dict[str, int]:
        return {
            "nodes": sum(1 for n in self._nodes if n.cls != "hierarchy"),
            "labeled": sum(1 for n in self._nodes if n.label),
            "clickable": sum(1 for n in self._nodes if n.clickable),
            "editable": len(self.editable()),
            "password_fields": sum(1 for n in self._nodes if n.is_password),
        }
