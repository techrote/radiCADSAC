"""Research-only CPython same-host B1 full re-proof vs incremental proof reuse.
Run from this B1 core directory. Never infer native/STEP speed from this.
"""
import gc, hashlib, json, statistics, time, tracemalloc
from fractions import Fraction as Q
from certificate_algebra import Piece, EvidenceMeter, replace, events, _state
from experiment import snapshot

PIECES = tuple(Piece(Q(i), Q(i+1), (Q(1),)) for i in range(32))

def arm(mode):
    meter = EvidenceMeter()
    s = snapshot(PIECES, meter)
    steps = []
    for k in range(64):
        index = k % 32
        c = (Q(1), Q(k+1,16), -Q(k+1,16))
        start = time.perf_counter_ns()
        if mode == "A":
            generation = s.generation
            pieces = list(s.pieces)
            old = pieces[index]
            pieces[index] = Piece(old.left, old.right, c)
            fully_verified = snapshot(tuple(pieces), meter)
            s = _state(fully_verified.pieces, fully_verified.certs, generation+1)
        else:
            s = replace(s, index, c, meter)
        assert events(s) == {"identity_intervals":[], "isolated_points":[]}
        _ = s.hash
        steps.append(time.perf_counter_ns()-start)
    return {"hash":s.hash, "leaf":meter.full_leaf_checks,
            "seam":meter.seam_checks, "wall_ns":sum(steps),
            "p95_ns":sorted(steps)[int(.95*(len(steps)-1))]}

def main():
    for _ in range(2):
        a, b = arm("A"), arm("B")
        assert a["hash"] == b["hash"]
    pairs = []
    for _ in range(6):
        row = []
        for mode in ("A","B","B","A"):
            gc.collect()
            sample = arm(mode)
            sample["mode"] = mode
            row.append(sample)
        assert len({x["hash"] for x in row}) == 1
        assert row[0]["leaf"] == 2080 and row[1]["leaf"] == 96
        pairs.append(row)
    peaks = {}
    for mode in ("A","B"):
        gc.collect()
        tracemalloc.start()
        arm(mode)
        retained, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peaks[mode] = {"peak_bytes":peak,"retained_bytes":retained}
    a = [x for row in pairs for x in row if x["mode"]=="A"]
    b = [x for row in pairs for x in row if x["mode"]=="B"]
    print(json.dumps({
        "evidence_class":"PYTHON_MICROBENCH_NOT_NATIVE",
        "warmups":2,"profiles":6,"order":["A","B","B","A"],
        "pieces":32,"updates":64,
        "exact_snapshot_hash_parity":len({x["hash"] for row in pairs for x in row})==1,
        "A_wall_median_ms":statistics.median(x["wall_ns"] for x in a)/1e6,
        "B_wall_median_ms":statistics.median(x["wall_ns"] for x in b)/1e6,
        "A_to_B_runtime_ratio":statistics.median(x["wall_ns"] for x in a)/statistics.median(x["wall_ns"] for x in b),
        "A_leaf_checks":a[0]["leaf"],"B_leaf_checks":b[0]["leaf"],
        "A_p95_median_us":statistics.median(x["p95_ns"] for x in a)/1e3,
        "B_p95_median_us":statistics.median(x["p95_ns"] for x in b)/1e3,
        "separate_tracemalloc":peaks,"samples":pairs},sort_keys=True,indent=2))

if __name__=="__main__":
    main()
