"""A1 research-only bounded comparison for recomputed certificate receipts.

Exact built-in type checks prevent Python subclass equality and bool/int aliases.
No network authentication, source ancestry, or native consumer authority claimed.
"""

MAX_NODES = 8192
MAX_DEPTH = 32
MAX_CONTAINER = 4096
MAX_TEXT = 65536
MAX_INTEGER_BITS = 4096


def _admissible(value, budget, depth):
    budget[0] += 1
    if budget[0] > MAX_NODES or depth > MAX_DEPTH:
        return False
    t = type(value)
    if t is str:
        return len(value) <= MAX_TEXT
    if t is int:
        return value.bit_length() <= MAX_INTEGER_BITS
    if t is bool or value is None:
        return True
    if t is list or t is tuple:
        return len(value) <= MAX_CONTAINER and all(
            _admissible(v, budget, depth + 1) for v in value)
    if t is dict:
        return len(value) <= MAX_CONTAINER and all(
            type(k) is str and len(k) <= 256 and
            _admissible(v, budget, depth + 1) for k, v in value.items())
    return False


def strict_equal(expected, offered):
    """No polymorphic equality until every input has exact primitive types.

    Dict key sets are compared only after rejecting non-built-in key types.
    Both graphs are depth/node bounded before recursive comparison.
    """
    if not (_admissible(expected, [0], 0) and _admissible(offered, [0], 0)):
        return False

    def equal(a, b):
        if type(a) is not type(b):
            return False
        t = type(a)
        if t is dict:
            return len(a) == len(b) and a.keys() == b.keys() and all(
                equal(a[k], b[k]) for k in a)
        if t is list or t is tuple:
            return len(a) == len(b) and all(equal(x, y) for x, y in zip(a, b))
        return a == b

    return equal(expected, offered)
