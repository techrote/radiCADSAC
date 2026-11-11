"""B1 deterministic proof-work accounting, NOT a wall-clock performance claim."""
import json
from fractions import Fraction as Q
from certificate_algebra import (
    Certificate, EvidenceMeter, Piece, bernstein, kind, events,
    replace, verify_base,
)


def snapshot(ps, meter):
    cs = [Certificate(p.hash, kind(bernstein(p)), bernstein(p)).record() for p in ps]
    return verify_base([p.source() for p in ps], cs, meter)


def run():
    ps = tuple(Piece(Q(i), Q(i+1), (Q(1),)) for i in range(32))
    incremental = EvidenceMeter()
    naive = EvidenceMeter()
    s = snapshot(ps, incremental)
    original = snapshot(ps, naive)
    assert original.pieces == s.pieces and events(original) == events(s)
    for k in range(64):
        i = k % 32
        c = Q(k+1,16)
        s = replace(s, i, (Q(1), c, -c), incremental)
        ref = snapshot(s.pieces, naive)
        assert ref.pieces == s.pieces and events(ref) == events(s)
    return {
        "evidence_class": "DETERMINISTIC_MODEL",
        "workload": {"pieces":32,"local_updates":64,"unchanged_other_pieces":True},
        "full_leaf_checks": {"naive_recheck_every_epoch":naive.full_leaf_checks,
                             "incremental_verified_proof_chain":incremental.full_leaf_checks},
        "ratio_proof_leaf_recomputations_only": str(Q(naive.full_leaf_checks, incremental.full_leaf_checks)),
        "incremental_seam_checks": incremental.seam_checks,
        "full_scan_seam_checks": naive.seam_checks,
        "incremental_transform_checks": incremental.transform_checks,
        "final_source_hash":s.hash,
        "final_zero_set":events(s),
        "not_measured":["wall clock", "native tick", "total hashing/memory overhead", "physics correctness", "STEP"]
    }


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
