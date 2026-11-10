"""B5 research-only crash-window indistinguishability for cross-owner effects.

Standalone finite model; NOT the CyberSand World, Rapier or solver runtime.
Run: python3 external_effect_custody_probe.py
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from json import dumps

PARENT_B3 = "2622a1204748d3630affa7f08e8ebb51dbb8fbe8"
PARENT_MODEL_BLOB = "e8176a1a2a63fdd3edc1b097cf47647a20ff34bf"


@dataclass(frozen=True)
class NativeView:
    epoch: int
    continuation: int
    water: int
    pending_token: str
    accepted_tokens: tuple[str, ...] = ()

    def digest(self) -> str:
        return sha256(dumps(self.__dict__, sort_keys=True).encode()).hexdigest()


@dataclass(frozen=True)
class History:
    native: NativeView
    external_count: int = 0
    external_tokens: tuple[str, ...] = ()


def recover_native(h: History) -> History:
    """Restore native precommit image, revoking old token by serial advance.

    External effects are not restored; this is a hypothetical crash model.
    """
    return replace(h, native=replace(
        h.native, continuation=h.native.continuation + 1))


def external_apply_unfenced(h: History) -> History:
    """Non-idempotent external effect, without a durable native ACK."""
    return replace(h, external_count=h.external_count + 1)


def external_apply_idempotent(h: History, token: str) -> History:
    """Hypothetical separately trusted, persistent external token ledger."""
    if token in h.external_tokens:
        return h
    return replace(h, external_count=h.external_count + 1,
                   external_tokens=(*h.external_tokens, token))


def recover_native_only(h: History, action: str) -> History:
    if action == "SPAWN":
        return external_apply_unfenced(h)
    if action in ("SKIP", "UNKNOWN"):
        return h  # UNKNOWN is safe refusal, not completed handoff
    raise ValueError(action)


def main() -> None:
    cases = 0
    for i in range(1, 97):
        token = f"handoff-{i}"
        n = NativeView(epoch=3, continuation=7+i, water=i*256,
                       pending_token=token)
        # Crash before vs after external effect, in both cases before native ACK.
        before = recover_native(History(n))
        after = recover_native(external_apply_unfenced(History(n)))
        assert before.native == after.native
        assert before.native.digest() == after.native.digest()
        assert (before.external_count, after.external_count) == (0, 1)
        assert before.native.continuation == 8+i
        # A policy using only native evidence takes the SAME action in each.
        # No total answer can make both external-effect counts exactly one.
        for action in ("SPAWN", "SKIP"):
            a, b = recover_native_only(before, action), recover_native_only(after, action)
            assert (a.external_count, b.external_count) in ((1, 2), (0, 1))
            assert not (a.external_count == 1 and b.external_count == 1)
            cases += 1
        assert recover_native_only(before, "UNKNOWN").external_count == 0
        # Conditional positive: independently durable external idempotency.
        a = recover_native(History(n))
        b = recover_native(external_apply_idempotent(History(n), token))
        assert external_apply_idempotent(a, token).external_count == 1
        assert external_apply_idempotent(b, token).external_count == 1
        # Negative: a lost ledger with surviving external effects duplicates.
        lost_ledger = replace(b, external_tokens=())
        assert external_apply_idempotent(lost_ledger, token).external_count == 2
    print(f"PASS: {cases} native-only noncompletion/double-effect controls")
    print("PASS: 96 persistent-external-ledger recovery controls")
    print("PASS: 96 lost-ledger negative controls; NO native/runtime claim")


if __name__ == "__main__":
    main()
