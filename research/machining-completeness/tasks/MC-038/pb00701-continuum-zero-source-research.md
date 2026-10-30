# MC-038 / PB-007-01 — exact closed original-source continuum-zero certificate

**Status: bounded DETERMINISTIC_MODEL research; 30 October 2026.** Parent: https://github.com/techrote/radiCADSAC/issues/100. Scoped preregistration: https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6532398994. Starting authoritative main d73dbd416e5228587e47ac49bec29914b9535246. This is not an MC-B gate or production authorization.

## Historical original source and missing semantics

The immutable V54 121-source corpus contains **harvested:verify_pb00701_v53:cb01c327d5f1** (original compact JSON SHA-256 a02ab8d83473f81d47b20c205083403babfc07059ca82303f1e6c92ab7481423). The original rational B-spline has a degree-zero H0 cosine control exactly 0, knots [0,1], no sine channel, shared original parameter v52-original-source on [0,1], affine phase turns t/4. V54 recorded the sole owner as DELEGATED_V6_CONSTANT_MODULATION, with BLOCKED reason TRIGONOMETRIC_IDENTITY_ZERO_REQUIRES_SEPARATE_SEMANTIC_HANDLING. The historical classification is unchanged.

The true physical function is zero at **every point in the closed original interval [0,1]**, not at finitely many isolated roots. The existing pinned affine-identity research (Git blob 9fd150e97bce84fdb3c4bad075c9938f4df9136c) already proves open-span identity for a broader exact original-source grammar, but explicitly lacks closed endpoint/knot and physical zero-set semantics. This research supplies the missing conservative closed-source/continuum branch and source-bound certificate.

## Conditional theorem and proof

Let F(t) be a finite rational B-spline-modulated trigonometric sum with one shared original source parameter t in [L,R] and globally rational affine phase alpha+beta*t. Let u_0=L < u_1 < ... < u_n=R be the complete finite ordered original source B-spline piece boundaries.

**Theorem.** If (1) the pinned exact original-source identity prover establishes F(t)=0 identically on **every open original piece** (u_i,u_{i+1}); (2) each original amplitude B-spline is fully clamped at its requested outer source endpoints L,R; and (3) every original cosine and sine amplitude channel has exactly equal **rational polynomial** left and right limits at each true interior source knot u_i; then F is continuous on all [L,R]. Its value on every closed source point equals its limiting value 0. Therefore the entire exact closed zero set is [L,R], an uncountable continuum because L<R.

The proof does not assume that independent channel continuity is necessary. An exact stationary cosine/sine cancellation can make the total physical function zero even when the individual channel amplitudes jump at a knot. Without a verified **individual-channel continuity** premise, this bounded theorem refuses rather than guessing; other mathematical approaches might later accept such a source. Endpoint clamping ensures the original B-spline values agree with the one-sided interior limits. The global affine phase is continuous. No numerical sampling establishes equality.

The exact identity checker uses exponential-polynomial independence for nonstationary rational phase and rational cyclotomic arithmetic for stationary phase (bounded order 256). Its original V7 B-spline lowerer and V6/event-engine source pins are checked before and after import. The new code separately reconstructs and compares each rational piece's amplitude values at original knot endpoints, without invoking historical owner selection, treating a source count as a zero-set theorem, or changing original source semantics.

**Bounded implementation grammar:** JSON-only original rational B-spline source records, 1–16 pieces, at most 12 active channels, degree at most 6, at most 128 controls per source spline, numerator/denominator bit limit 128, bounded source interval/affine phase, bounded lowered coefficient bit size and 64 KiB serialization. Unsupported sources or stationary cyclotomic order beyond the reviewed budget produce a typed nontruth BLOCKED or RESOURCE_REFUSAL, not an identity/no-root verdict. The theorem itself is conditional; finite resource limits do not decide undecidable/unproved cases.

## Typed continuum-zero source certificate

The new status COMPLETE_CLOSED_CONTINUUM_ZERO_SOURCE_RESEARCH contains an explicit CLOSED_CONTINUUM_ZERO_COMPONENT carrying the original closed source interval, full source SHA-256/parameter/phase/knot partition, exact per-piece identity proofs and per-channel knot continuity. It states every_closed_source_point_is_zero=true, cardinality=UNCOUNTABLY_INFINITE, isolated_finite_root_list_applicable=false, isolated_root_count=null, ordered_sign_cells_applicable=false. The null isolated count is **not** zero roots; the isolated-event grammar is inapplicable.

**Decisive negative C (restricted representation):** Any consumer restricted to a **finite exhaustive list of isolated roots** cannot represent the complete zero set of this admitted original source. [L,R] contains uncountably many distinct real points, whereas a finite list contains only finitely many. The consumer must adopt a separate continuum-zero result type or refuse without truth value. This is **not** a general impossibility proof for analytic root solving, or a claim that the full mixed zero-set problem is decided.

## Source-bound positive and falsification controls

Positive original-source proof: the exact frozen H0-zero source and its unchanged historical refusal; moving-phase zero C0/C1 channels; an exactly continuous two-piece H0-zero source with true knot at t=1 and closed zero set [0,2]; stationary H1 cosine/sine coefficients +1/-1 cancelling at rational phase 1/8 turn.

Negative controls: turn on a nonzero phase rate for the stationary cancellation; original H0 linear crossing, order-two tangency and single endpoint zero (none may be a continuum); fully open-span identity but **discontinuous individual amplitude channels** at the source knot (conservative refusal); zero/nonzero split across knot; nonclamped/extended B-spline endpoint support; altered degree/controls/knots, fake source ID/phase, noncanonical float/rational, sin-harmonic zero, excessive harmonics/order/depth/bytes and forged proof/gate fields. A finite-list cardinality test constructs a rational point in (0,1) outside any proposed finite root list. Resource exhaustion does not assert a mathematical falsehood.

## Disjoint integration with the already qualified five finite-event sources

The read-only five-source event consumer from merged PR #331 (Git code blob a8aedb83772984831d5aa5c3b9b8d1cead04c345, source-bound machine report blob 4c619ee7011fa2d7a65f3391ff95cd8e7eecf3b0) is replayed with its original historical source custody and mathematical checks. It proves full finite event sets for five distinct *other* historical original source IDs. The continuum-zero historical identity source is disjoint and has an entirely different zero-set type. No root is ever deduplicated across different manufacturing source records.

The immutable original V54 corpus Git blob 5841c331579489b25caef38cd412bdbf286f9134 still has 121 cases, 20 route refusals, 30 missing ordered premises and identical historical statuses. Six selected distinct sources now have replayable bounded mathematical **complete zero-set** witnesses: five finite and one continuum. The exact **six-only overlay** is 20 → 14 remaining historical route-refused IDs outside these SIX specifically selected proofs; 30 → 30 missing ordered premises; 121 → 121 original denominator. The other 14 IDs are retained individually in the machine report. This is **not** an exhaustive current post-V54 mathematical research inventory, **not** accepted legacy V6/V27/V43 routing, and **not** a general PB-007-01 theorem. Other earlier research may independently address some of those 14 source cases.

## Reproduction, qualification and remaining proof frontier

Exact source and adversarial replay:

    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_continuum_zero_source.py --contract --self-test
    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_affine_identity_frontier.py --contract --self-test
    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_five_source_evidence_replay.py --contract --self-test
    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_frontier.py --contract --self-test

Literal PR-head focused CI, mc1-static, exact-source direct review, corrected-head checks, expected-head-protected merge, synthetic/reviewed/landed tree equality and independently successful merged-main CI are acceptance conditions. AI-assisted owner-account COMMENTED review is not separately authenticated independent personnel approval.

**Protected global boundary:** PB-007-01/02/03/04 and required PO-02/04/05/07/08 remain OPEN or OPEN_PROPAGATED; MC-B and MC-1 remain NOT_ESTABLISHED and production_authorized=false. No native material/topology/B-rep/STEP or paid campaign, no 26-operation domain narrowing, no source/phase/provenance/canonical-journal/material/body/lineage/refusal/UNCERTIFIED semantic change.

**Next high-value generalization:** a source-bound **mixed finite-event and continuum-zero** segmentation theorem, including genuine discontinuous source knots and event boundary equality, with a terminating checker for its stated grammar. Never represent a zero interval using an arbitrary numerical scan or a fake isolated root.
