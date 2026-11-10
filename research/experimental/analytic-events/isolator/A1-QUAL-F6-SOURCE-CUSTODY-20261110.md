# A1-QUAL-003 — F6 source-analysis/digest custody correction (10 November 2026)

**Research only — Draft/HOLD.** Exclusive A1 source lease [#324 comment 6770879344](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6770879344). Base PR #470 `c2f318215678951961f372866087e425a34e0609`, accepted main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. No native/STEP/production/MC-038 edits.

## Actual negative result, prior published F6

At original `projective_h2_atlas.py` Git blob `9c7a07617f98e7f01c63439a1c71fc970c2ec336`, F6 `read(doc)` parsed all fields from a mutable exact Python `dict` and only afterward called `json.dumps(doc)` to hash. A deterministic `sys.settrace` mutation at actual digest entry changed `S2=-1/4` to `S2=0/1`. The real `certify` constructed four order-one CROSS events but bound them to the all-zero source hash `d2393a48a68d2ab95570481356e6f874f035c57a7b64d3aa33a084d23ef67cfb`. Running real `verify` with the same source interleaving returned **True** for that inconsistent event receipt. Static all-zero source correctly refused it. The exact original parent-imported adversary exited 1: `AssertionError: F6 SOURCE/HASH TOCTOU`. This is a research in-process source-custody failure, **not** an original physical B-spline exploit or a refutation of the Cayley/Sturm mathematics. Earlier A3 F7 analogous finding and its negative evidence remain retained.

## Narrow repair and bounds

F6 now requires a flat built-in `dict` with literal string keys; calls `dict.copy()` once before any coefficient token parsing, then derives both the exact rational projective events and source SHA-256 from that one copied mapping. No mutable nested values are admitted by `token`. A new original test exercises honest four-event, static all-zero, forged source-hash, simulated digest-boundary mutation through the actual parent `read/certify/verify` and captured-source parity. This is **in-call internal consistency only**. It does not prove an atomic external writer fence, authenticated NURBS/B-spline ancestry, or source-state lifetime/rollback custody.

## Verification and reproducibility

- Original fixed-head `c2f318215678951961f372866087e425a34e0609`: complete published candidate suite **97/97 PASS**, yet direct F6 interleaving **FAIL (false receipt accepted)**, source/test blobs `9c7a07617f98e7f01c63439a1c71fc970c2ec336` / `eba2c7ddc434ba2dde1acef25c000cab560d9cb7`.
- Local corrected candidate: **98/98 PASS** in CPython 3.13.5 with actual parent imports; new F6 source/test Git blobs `ce90449291bbdd28eea9ea0f800a0fa5650768ee` / `5adadce0713a506416eb517e282839a2bce033db`. The F6 digest-boundary negative control is part of that 98-method suite.
- Other corrected F1/F7 hostile-receipt and A3 F7 interleaving controls remain required at the newly published exact commit; local candidate full suite includes their authored tests.
- Reproduction: `cd research/experimental/analytic-events/isolator && python3 -m unittest discover -s . -p 'test_*.py' -v && python3 challenge_sympy.py`. Reconfirm exact literal Git SHA and blobs before claiming independent admission.

## Qualification matrix

| Gate | Disposition |
|---|---|
| Conditional bounded H2 Cayley/Sturm theorem | Preserved, not expanded or reproved |
| Local candidate complete Python tests | **98/98 PASS** (must re-run against exact published commit) |
| A3 independent second-source same-head execution | **PENDING** |
| Physical B-spline ancestry and external snapshot custody | **UNVERIFIED** |
| Arbitrary knots, transcendental roots, unrestricted H2/tangencies | **NOT_ESTABLISHED** |
| MC-B/MC-1 | **NOT_ESTABLISHED**, `production_authorized=false` |

No 121/20/30/50 census, 26 operations, historical source/evidence or MC authority changed. The research result must not be merged or treated as native geometry acceptance without A3 review.
