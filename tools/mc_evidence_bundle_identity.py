#!/usr/bin/env python3
"""Additive, prospective MC evidence identity checks.

MC-009's original programme verifier is a frozen, content-pinned research
artifact. This guard invokes it unchanged, then strengthens two *local*
bindings. It does not resolve external references, validate STEP geometry,
or grant any MC-1 gate/production authority.
"""
from __future__ import annotations

import argparse
import copy

import mc_evidence_verifier as frozen


def verify_bundle(fixture: dict, result: dict, verdict: dict, *,
                  claim: dict | None = None, outcome: dict | None = None) -> None:
    """Enforce the frozen MC-009 contract and additional local identity guards."""
    frozen.verify_bundle(fixture, result, verdict, claim=claim, outcome=outcome)
    # Optional only when neither side asserts an exported engineering file.
    if verdict["expected"].get("exported_file_digest") != result.get("exported_file_digest"):
        frozen.fail("exported-file identity omitted or mismatched in verdict")

    if claim is not None:
        actual_digest = frozen.object_digest(result)
        for ref in claim["evidence_refs"]:
            # External result identities cannot be verified from this one bundle.
            if (ref["kind"] == "bound-result"
                    and ref["identity"] == result["attempt_id"]
                    and ref["digest"] != actual_digest):
                frozen.fail("current-attempt claim bound-result digest mismatch")


def self_test() -> None:
    base = frozen.sample()
    verify_bundle(*base[:3], claim=base[3], outcome=base[4])

    def negative(name: str, mutation) -> None:
        f, r, v, c, o = copy.deepcopy(base)
        mutation(f, r, v, c, o)
        # Demonstrate that the frozen verifier really does permit this input;
        # this proof-of-gap is deliberate, not a reason to rewrite its pin.
        frozen.verify_bundle(f, r, v, claim=c, outcome=o)
        try:
            verify_bundle(f, r, v, claim=c, outcome=o)
        except frozen.EvidenceError:
            return
        raise AssertionError(f"additive guard accepted {name}")

    negative("verdict omitted an existing STEP export digest",
             lambda f, r, v, c, o: v["expected"].pop("exported_file_digest"))
    negative("accepted claim attributes an unrelated hash to current attempt",
             lambda f, r, v, c, o: c["evidence_refs"][0].__setitem__(
                 "digest", frozen._d("other-attempt")))

    # A truly non-exporting intermediate attempt may omit both export digests,
    # provided the verdict and current-attempt claim bind its modified result.
    f, r, v, c, o = copy.deepcopy(base)
    del r["exported_file_digest"]
    del v["expected"]["exported_file_digest"]
    v["result_digest"] = frozen.object_digest(r)
    c["evidence_refs"][0]["digest"] = frozen.object_digest(r)
    verify_bundle(f, r, v, claim=c, outcome=o)

    # A separate evidence kind is valid; this local check does not pretend
    # to resolve the contents of another artifact.
    f, r, v, c, o = copy.deepcopy(base)
    c["evidence_refs"].append({
        "kind": "research-note",
        "identity": "independent-note",
        "digest": frozen._d("note"),
    })
    verify_bundle(f, r, v, claim=c, outcome=o)
    print("MC additive evidence export/claim identity self-test passed")


def main() -> int:
    ap = argparse.ArgumentParser(description="Additive MC evidence identity guard")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--fixture")
    ap.add_argument("--result")
    ap.add_argument("--verdict")
    ap.add_argument("--claim")
    ap.add_argument("--outcome")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not (args.fixture and args.result and args.verdict):
        ap.error("--fixture, --result and --verdict required unless --self-test")
    verify_bundle(
        frozen.load(args.fixture), frozen.load(args.result), frozen.load(args.verdict),
        claim=frozen.load(args.claim) if args.claim else None,
        outcome=frozen.load(args.outcome) if args.outcome else None,
    )
    print("MC additive evidence identity verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
