# MC-038 / PB-007-01 — original-source V6 tail100 touching-knot closure

**Date:** 30 October 2026. **Evidence:** bounded DETERMINISTIC_MODEL exact-source mathematical research. **Parent:** [#100](https://github.com/techrote/radiCADSAC/issues/100). **Preregistration:** [comment #6523853415](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6523853415). **Starting main:** c1867b0ea60d49ba7cd7f75588d93c760fef9eba. This is a research result, NOT general PB-007-01 acceptance, a V27 routing fix, or native engineering geometry.

## Hypothesis and original-source identity

The frozen 121-case V54 source archive (Git blob 5841c331579489b25caef38cd412bdbf286f9134) records **composite:DELEGATED_V6_CONSTANT_MODULATION:tail100** as historical BLOCKED: first original B-spline span V6 DELEGATED_V6_CONSTANT_MODULATION CERTIFIED, second span V27 rational phase-sector partition BLOCKED with exact reason V27_CHILD_NOT_CERTIFIED.

The original source JSON is uniquely pinned by SHA-256 f6a0eb06c66af415fbb8abdfe62f9b36a2a2bf154e535d83307a80228e044ad5 (canonical sorted compact JSON). Parameter source is source-time-t in [0,2]; phase turns equal t/4. The original fully clamped H0 cosine B-spline has degree 1, knots [0,0,1,1,2,2], controls [0,0,0,100]; the degree-0 H1 cosine B-spline has knots [0,1,2], controls [1,1]; there is **no sine channel**. The independent replay checks the exact full source field/degree/knot/control identity, not a substitute curve or sampled approximation.

Unlike the already checked frozen tail0 source from #307/#308, tail100 has a rising H0 ramp after its true source knot. The question is whether a separate full-original-source mathematical certificate can settle *this* historic V27-refused source, without accepting V27 generally.

## Closed-source theorem

Original clamped-Bernstein lowering implies, in the **same source coordinate** t:

- on 0 <= t <= 1: F(t) = cos(pi*t/2);
- on 1 <= t <= 2: F(t) = 100*(t-1) + cos(pi*t/2).

There is no source-coordinate rephasing, normalization, or substituted chart. At t=1 the two values equal zero: F(1-) = F(1+) = cos(pi/2) = 0. This is **one real source knot**, not two independent endpoint events and not an artificial orientation proof cut.

For 0 <= t < 1, theta = pi*t/2 lies in [0,pi/2); hence F(t)>0, while the left first derivative at the knot equals -pi/2, nonzero.

For t=1+x, 0<x<=1, the exact identity cos(pi/2+pi*x/2)=-sin(pi*x/2) gives

    F(1+x) = 100*x - sin(pi*x/2).
    0 <= sin(pi*x/2) <= pi*x/2 < 2*x  (using 0<pi<4).
    Therefore F(1+x) > 98*x > 0.

Its right first derivative at x=0 is 100-pi/2 > 98 > 0. Thus the knot is an isolated first-order zero *on each side* with positive interior signs on both sides: one **TOUCHING** physical event at t=1, no additional open-span roots, exact exteriors F(0)=1 and F(2)=99, and maximal physical signs (+,+). No globally smooth multiplicity is assigned because the source has different one-sided derivatives. The proof uses exact source polynomial coefficients and standard classical trigonometric inequalities; it does not use binary trigonometric evaluation, root scanning, a stopping-cap result, or an assumed V27 route count.

For the fixed phase and H1 grammar, the argument generalizes to a rational H0 second-span ramp slope A>2 by the strict bound F(1+x)>(A-2)x. The research adapter admits ONLY the pinned original A=100 source. A proposed indiscriminate proof for all positive slopes is **falsified**: A=1/2 has F(2)=A-1=-1/2, so its tail cannot be uniformly positive. Even A<=2 is a *refusal of this sufficient bound*, not proof of a root or nonmonotonicity for that parameter.

## Adversarial and provenance verification

The additional identity-zero mutation control refuses a continuum-zero original source instead of claiming it has one isolated event. A synthetic extremely close rational margin above A=2 challenges the strict slope bound without interpreting a resource limit as a truth value.

The machine report and executable replay independently check the 121-case post-v54 census against the original three Git-blobs (corpus 5841c..., owner inventory 8649c..., coverage 600ba...), the pinned audit verifier 12c6efeb..., MC-002 26-operation contract blob 23de82f..., and current authority blob fa0233... (no production, MC-1 NOT_ESTABLISHED). They reject forged source IDs/producing origin, original interval/phase, knot vectors, harmonics, polynomial controls, appended annotation or noncanonical rational, historical owner/refusal/status, changed source SHA-256, machine-reported zero order/sign/census/gate, and positive-ramp overgeneralization. Synthetic rational slopes and a negative endpoint are *adversarial controls*, not independently added cases to the historical corpus.

Reproduce on the full repository:

    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v6_tail100_knot.py --contract --self-test
    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_frontier.py --contract --self-test
    python3 tools/validate_machining_completeness.py --self-test

Requires exact PR-head focused CI, mc1-static, source/maths review, expected-head-protected merge, and merged-main source-matched checks. A source-level argument review is not a distinct human GitHub approval.

## Baseline versus newly demonstrated source-specific evidence

The frozen 121 source statuses remain byte-for-byte unchanged: **20 historical v54 BLOCKED**, **30 historical missing-ordered-premise BLOCKED**, **40 one-span**, **26 V54 finite-source**, **5 V53 preserved**. This result adds exactly **one separately evidenced source-specific full physical zero/sign theorem** within the historical 20 route-refused sources. After this bounded source-specific result is independently qualified, the *supplemental mathematical-evidence-only* view is:

| Classification | Historical v54 | Supplemental research not yet integrated |
|---|---:|---:|
| Uncertified route cases without this source-specific physical proof | 20 | 19 |
| Missing ordered-span-premise cases without a general integrated proof | 30 | 30 |
| Total original source cases | 121 | 121 |

The derived 19 is **only a one-claim overlay**: historical v54's 20 minus exactly the *single new* tail100 source witness. Other independently scoped post-v54 research may also provide source-specific evidence; this record **does not** attempt to compute an exhaustive current cross-research backlog or de-duplicate other witnesses. It is **not** a changed v54 result, generic V27 admission, MC-B numerator or proof of general source grammar. The historically refused V27 route remains refused; the published new proof is an independent source-specific theorem. The one-case delta can be withdrawn if source identity, trigonometric proof, or admission checks fail. Raw v54 baseline and failed historical evidence must remain intact.

## Scope / downstream implications

This source-level example demonstrates that a historical V27 child refusal can coexist with a complete independent physical root/sign solution. It supplies a falsification target for future V27 complete-root and source-knot adapters. It does not solve V27 for arbitrary source controls, all V6 charts, general nonmonotone/identity-zero analytic roots, endpoint multiplicities for other source knots, PB-007-02/03/04, or PO-02/04/05/07/08. MC-B/MC-1 remain NOT_ESTABLISHED; all 26 domain operations, journal/source/phase/provenance, durable material/body/lineage, refusal/UNCERTIFIED, native output and usable conventional STEP requirements are protected. No native campaign/paid computation or production creation is authorized.

**Next action:** independently adapt a certified source-root witness to the real V27 child-consumption interface and challenge it on the remaining four V27 child refusals; do not reclassify a historical route merely because one original source admits an independent argument.
