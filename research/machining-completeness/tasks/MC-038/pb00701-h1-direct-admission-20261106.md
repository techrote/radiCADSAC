# MC-038 / PB-007-01 — frozen-source direct-admission boundary for the oriented H1 angular-drift theorem

**Date:** 6 November 2026 UTC. **Status:** new bounded, source-pinned negative direct-applicability finding; independent corrected-head admission pending. **Evidence class:** `DETERMINISTIC_MODEL`, not native geometry, independent oracle, or actual engineering STEP. **Parent:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). **Coordination:** [#324/6691020045](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6691020045).

## Precise falsifiable claim and scope

**Named still-open obligations:** PB-007-01; PO-04, PO-05 and PO-08 (and the dependent PB-007-02/03/04 and PO-02/07).

**Proposed route under challenge:** `DIRECT_UNMODIFIED_PR439_H1_ANGULAR_DRIFT_ADMISSION_CLOSES_FROZEN_UNRESOLVED_CASES`. Suppose the exact grammar of Draft [PR #439](https://github.com/techrote/radiCADSAC/pull/439) at literal candidate head `e3264629c967189f5b843bbb7e73b80df2f3c56c` is used **without any source transformation, new analytic theorem, grammar expansion, or owner-to-consumer integration** on the 121 frozen v54 originals. Necessary conditions are source `RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE`, source parameter `source-time-t` on exactly [0,1] or [0,2], phase turns offset zero and rate 1/8, only H1 cosine/sine with clamped exact piecewise degree-0/1 rational B-splines continuous at the actual knot, and optionally an identically zero H0 cosine.

**Falsifier:** a fourth source satisfying all these necessary structural conditions; an additional historical unresolved original satisfying them; an incorrect source/row hash or pinned corpus; or a missing historical V2 prior proof. The executable enumerates all 121 rather than selecting congenial cases.

**Result:** exactly 3/121 are structurally eligible; 118/121 fail at least one necessary precondition. Of the historical 50 unresolved cases, **48/50 fail the exact direct-admission grammar**. The other two already have independently registered complete source-specific V2 witnesses. Thus the current *unmodified direct route* cannot by itself establish a **new historical closure**. A new generic owner/consumer implementation, accepted expanded grammar, or justified source transformation might still succeed. **This does not refute #439's admitted theorem, general analytic-event decidability or PB-007 mathematical possibility.**

## Exact source custody and historical classifications

Read the immutable corpus `pb00701-finite-owner-corpus-v54.json` at Git blob `5841c331579489b25caef38cd412bdbf286f9134`, and independently registered V2 sources at Git blob `e52d3baf3692a011cf86234eeaa992ef407d99fd`. All 121 original case IDs, 50 prior V2 source and row SHA-256 identities, source origin and evidence classes are verified. The audit never runs or overwrites the frozen v54 owner or substitutes synthetic examples.

| Structurally eligible original | Original source SHA-256 | Historical v54 state | V2 prior signed witness |
|---|---|---|---|
| `harvested:verify_pb00701_v10:f8b83299bd55` | `6389858fc59830420a9094a4b335055a5b2a2c4232562f0146bd3899bc2480fa` | CERTIFIED | Not part of historical 50 |
| `harvested:verify_pb00701_v9:4e7b85fa122a` | `a83ca0cd16c7822e6525f8f2d2df26a54f45b99807cadebc67f31fc49b066c10` | BLOCKED, historical V43 route | COMPLETE_SOURCE_SPECIFIC |
| `composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail0` | `4d1ef1cbecceeb4a43b4e30fd37327fa204164cc9ce25dfe4f1744a052cebcc2` | Missing exact ordered owner premise | COMPLETE_SOURCE_SPECIFIC |

The two historical unresolved originals have their **original** physical phase turns `t/8`. The harvested case is source-time [0,1] without a true internal knot; the composite has source-time [0,2] and physical knot at t=1. Their event/sign conclusions precede #439 in accepted source-specific V2 and the V9 ratio-prefix composition. This structural census does not recompute roots, multiplicities, tangencies, extrema or signs; those are separate exact mathematical proof responsibilities.

### Disjoint first necessary refusal counts

| First admission outcome (ordered structural gate) | Cases |
|---|---:|
| Exact structural candidates | 3 |
| Wrong original phase offset/rate | 91 |
| Wrong original time, bounds or grammar | 24 |
| Harmonic inventory incompatible with H1-only rule | 1 |
| Extra unsupported original spec field | 1 |
| Nonzero H0 or incompatible H0 structure | 1 |
| **Total frozen population** | **121** |

Examples include `harvested:verify_pb00701_v9:1a5fd052a155` (no cosine H1), `harvested:v19:951efe10f570` (additional `parameter_projection` field), and `composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail100` (nonzero H0 tail). These are **structural refusals only**; no mathematical impossibility of an alternative solver is inferred.

## Reproduction, bounds and adversarial controls

Run from repository root:

~~~sh
python3 research/machining-completeness/tasks/MC-038/pb00701_h1_direct_admission_20261106.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract --self-test
python3 tools/validate_machining_completeness.py
~~~

The first command reads **at most 400,001 bytes from each of two pinned originals**, authenticates Git blob IDs, verifies all 121 unique IDs, the exact 20/30 historical refusal split, and all 50 V2 source/row hash and evidence-level bindings. The structural checks use bounded exact rational equalities on the clamped control records, not numerical sampling. Five mutation controls independently challenge a known accepted source's phase, harmonic, knot, additional field and H0 amplitude; each must refuse. On-disk adversarial receipt controls also require typed refusal of duplicate raw JSON keys, ten-thousand-deep nesting, 5,000-digit integers, oversized inputs, nonfinite/float tokens and invalid UTF-8, while retaining a positive escaped-string control. A wrong receipt or false gate promotion cannot pass canonical machine-receipt equality. Identity-zero, tangency, near-coincident roots, endpoint zero and full sign/multiplicity claims are **not** decided by this checker, so no synthetic root tests or numerical scans are counted as proof. Resource refusal is never a zero-event conclusion.

## Matched before/after result and gate nonpromotion

| Fixed original-source census | Before | After | Delta |
|---|---:|---:|---:|
| Frozen original v54 cases | 121 | 121 | 0 |
| Historical uncertified route cases | 20 | 20 | 0 |
| Historical missing ordered premises | 30 | 30 | **0** |
| Existing complete V2 source witnesses | 50 | 50 | 0 |

**Newly resolved source IDs:** none. **REQUIRED PB/PO discharges:** zero. The new C is **only** the falsification of the literal, untransformed direct-admission route to the 48 excluded historical sources. The two structurally eligible historical originals remain blocked under the old owner labels despite their older source-specific V2 proof and the new candidate #439 theorem.

No #439 implementation, branch or PR metadata is modified. Separate #397 retains exclusive main integration. The frozen v54/V2 artifacts, current-authority, task/proof/programme registries, current-state ledger, 26 supported machining operations, source semantics, durable body states, journal, topology, native/STEP and production authorization remain unchanged. PB-007-01/02/03/04 and PO-02/04/05/07/08 **OPEN**; MC-B and MC-1 **NOT_ESTABLISHED**.

**Critical-path dependency unlocked:** #439's author/integrator can now distinguish a sound but narrow oriented-H1 result from broad historical ordered-premise closure. The next mathematical target is a reusable event/sign transfer theorem for the still-excluded nonstationary, sine-bearing, multiharmonic and endpoint/identity/tangency source grammars, with a concrete frozen original source accepted through a new generic owner-to-consumer route rather than another preexisting V2 witness.

**Acceptance boundary:** same-session source review and literal-head CI do not replace distinct-session mathematical/admission review. Leave the research Draft until that check; no main merge while #397 retains custody.
