"""B1-E6: bounded primitive-JSON receipt admission; research-only.

Trust boundary: never invoke a caller-defined equality hook while checking a
submitted certificate. This validates *shape*, not source provenance/signatures.
"""
from __future__ import annotations

from certificate_algebra import Refusal

MAX_RECEIPT_NODES = 131072
MAX_RECEIPT_DEPTH = 32
MAX_RECEIPT_STRING = 4096
MAX_RECEIPT_INT_BITS = 4096


def _primitive(value, depth: int, budget: list[int]) -> None:
    budget[0] -= 1
    if budget[0] < 0 or depth > MAX_RECEIPT_DEPTH:
        raise Refusal("receipt structure exceeds verification budget")
    t = type(value)
    if t is dict:
        # Validate all keys BEFORE looking up a single key. No custom __hash__
        # or __eq__ can then execute inside a dict lookup or comparison.
        if any(type(k) is not str or len(k) > MAX_RECEIPT_STRING for k in value):
            raise Refusal("nonprimitive or oversized receipt key")
        for child in value.values():
            _primitive(child, depth + 1, budget)
    elif t is list:
        for child in value:
            _primitive(child, depth + 1, budget)
    elif t is str:
        if len(value) > MAX_RECEIPT_STRING:
            raise Refusal("oversized receipt string")
    elif t is int:
        if value.bit_length() > MAX_RECEIPT_INT_BITS:
            raise Refusal("oversized receipt integer")
    elif t is bool or value is None:
        return
    else:
        raise Refusal("nonprimitive receipt value or Python subclass")


def _same(a, b) -> bool:
    # Both trees have been audited; only builtin, type-identical operations occur.
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return (len(a) == len(b) and a.keys() == b.keys()
                and all(_same(a[k], b[k]) for k in a))
    if type(a) is list:
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    return a == b


def validate(value: object) -> None:
    """Reject nonprimitive or oversized source/receipt input before parsing.

    Safe as a local import from certificate_algebra: no admission function is
    invoked while Python imports either module. This is a resource-bounded
    shape check, not source authentication or a mathematical proof.
    """
    _primitive(value, 0, [MAX_RECEIPT_NODES])


def admit(expected: dict, proposed: dict) -> None:
    """Replay equality only for exact builtin JSON trees; otherwise NONTRUTH.

    No caller-supplied comparator, truthiness, coercion, digest or object
    serialization participates. Independent source-pin custody is still needed.
    """
    validate(expected)
    validate(proposed)
    if type(expected) is not dict or type(proposed) is not dict or not _same(expected, proposed):
        raise Refusal("missing, stale, forged, or noncanonical primitive receipt")
