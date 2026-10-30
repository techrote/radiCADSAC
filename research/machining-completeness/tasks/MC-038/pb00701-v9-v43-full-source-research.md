# MC-038 / PB-007-01 — complete original V9/V43 frozen-source crossing theorem

**Status:** bounded DETERMINISTIC_MODEL mathematical result, 30 October 2026. Parent: [issue #100](https://github.com/techrote/radiCADSAC/issues/100). Original manual lane claim / falsification preregistration: [#324 comment 6531114353](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6531114353). Authoritative starting main: 5f0ef452a663f3b14ad185947d566ae4800ca062. No production or native campaign authorization.

## Exact original source and historical blocker

The immutable 121-case v54 source corpus (Git blob 5841c331579489b25caef38cd412bdbf286f9134) contains the exact case:

    composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail100

Canonical original source SHA-256: cc13a39582060e763c573f2665b3ea3b6dfe8b76a6cb0fb77a7b0ec90cf6253a.

The first original source span [0,1] was historically certified by PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO; the second [1,2] was BLOCKED by PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF, reason CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED. Whole-source historical v54 disposition: BLOCKED. The previous [V43 refusal-cone report](pb00701-v43-refusal-cone-probe.md) proved positivity of the second piece, explicitly **not** a complete root and sign theorem for the original two-span source.

The original source parameter is source-time-t over [0,2], and its exact global phase in turns is t/8. Fully clamped B-spline source channels are:

| Channel | Degree | Knot sequence | Piecewise Bernstein controls |
|---|---:|---|---|
| Cosine H0 | 1 | 0,0,1,1,2,2 | [0,0] / [0,100] |
| Cosine H1 | 1 | 0,0,1,1,2,2 | [-1/2,1/2] / [1/2,1/2] |
| Sine H1 | 0 | 0,1,2 | [1] / [1] |

Independent exact clamped Bernstein lowering, without running historical route selection or trusting a caller-asserted physical function, produces these literal **original source functions**, retaining the original phase:

    F(t)=(t-1/2)*cos(pi*t/4)+sin(pi*t/4),                0<=t<=1
    F(t)=100*(t-1)+(1/2)*cos(pi*t/4)+sin(pi*t/4),        1<=t<=2

Channel values agree at the true source knot t=1. Therefore F(1)=3*sqrt(2)/4>0: the knot is **nonzero**, not a duplicated physical zero, orientation cut or synthetic sample.

## Complete first-span proof

Let theta=pi*t/4, 0<=t<=1. Then 0<=theta<=pi/4, and cos(theta)>=sin(theta)>=0, with cos(theta)>0. The physical source derivative is

    F'(t) = cos(theta) + (pi/4)*(cos(theta)-(t-1/2)*sin(theta)).

Since t-1/2 <=1/2 and sin(theta)<=cos(theta),

    cos(theta)-(t-1/2)*sin(theta) >= (1/2)*cos(theta)>0.

Hence F'(t)>0 on the **entire closed first span**, independently of a finite scan or iteration cap.

To locate the unique root in a strict **rational original-source bracket**, use classical exact constants 3<pi<22/7 and 0<z<pi/2 implies sin z<z, cos z>1-z^2/2, and tan z>z.

- At t=1/4: F(1/4)=cos(pi/16)*(tan(pi/16)-1/4). Because pi/16<11/56 and tan z<z/(1-z^2/2), exact rational upper bound

      tan(pi/16) < (11/56)/(1-(11/56)^2/2) = 1232/6151 < 1/4.

  Thus F(1/4)<0.
- At t=1/3: F(1/3)=cos(pi/12)*(tan(pi/12)-1/6). Since tan(pi/12)>pi/12>1/4>1/6, F(1/3)>0.

By the intermediate-value theorem, strictly positive derivative and these exact opposite-sign witnesses, there is **exactly one simple physical root in (1/4,1/3)**, crossing NEGATIVE to POSITIVE. Its identity is the unique original-source root within that rational isolator, **not** a fabricated rational/algebraic coordinate. F(0)=-1/2, and there are no endpoint roots on the first span.

## Complete historically refused V43 tail

For 1<=t<=2, theta=pi*t/4 lies in [pi/4,pi/2]. Here cos(theta)>=0 and sin(theta)>=sqrt(2)/2>1/2; also 100(t-1)>=0. Thus

    F(t)>1/2   for EVERY t in [1,2].

The original second span is therefore strictly positive and root-free; F(2)=101. The true physical knot at t=1 is continuous and strictly nonzero. The complete **whole-source** root census is one simple strictly interior crossing; original span-open root counts [1,0]; no true source-knot or exterior root; maximal sign cells (-,+).

This is a source-specific exact mathematical argument. It does not prove the historical V43 generic closed-handoff certificate or a general algorithm for nonmonotone polynomial-trigonometric functions.

## Evidence binding, falsification and reproducibility

The deterministic source-bound verifier checks the entire immutable v54 corpus Git blob, its independently pinned post-v54 121-case/21-mutant audit (blob 12c6efeb667a954ffc5a7e27849ae815d466580a), the MC-002 26-operation domain (blob 23de82f5240a72509f7afe4acd5948b65bc4ff13) and current production-disabled authority (blob fa0233323a0804d8a5d3eb7cd892a274a6173fab). It demands all exact original B-spline knots, degrees, controls, harmonic inventory, phase, source parameter, SHA-256 and V9/V43 historical statuses, with no unreviewed fields. No V54 source or owner is mutated.

Adversarial tests reject forged historical owner/refusal/case/origin, altered source controls/knot/phase/interval, noncanonical/binary scalars, unexpected harmonics, changing the first source from a simple crossing into another shape, false root/bracket/sign/count/authority claims, identity-zero continuum surrogates and oversized/malformed reports. A changed source is a **refusal of this exact-source theorem**, not a purported new mathematical truth. Synthetic tangencies, very-close roots and other analytic sources are NOT claimed solved. Resource limits are nontruth.

Reproduce from repository root:

    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v9_v43_full_source.py --contract --self-test
    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_frontier.py --contract --self-test
    python3 tools/validate_machining_completeness.py --self-test

Required publication: literal final PR-head focused and mc1-static CI; direct mathematical/source review; expected-head-protected merge; identical reviewed and landed Git tree; actual postmerge focused/static CI. AI-assisted owner-account COMMENTED source review is not separate-account/human approval.

## Historical before/after and mandatory nonclaims

The immutable v54 result still has **121 source cases, 20 source-route BLOCKED, 30 missing ordered-span-premise BLOCKED**, with 71 previously certified cases. This result adds one new complete original-source mathematical root/order/multiplicity/sign witness for a distinct historically V43-refused source. **Only in this one-new-witness overlay**, historic route-refusals lacking this precise independently replayable proof change from 20 to 19; ordered-premise count stays 30 and denominator stays 121. This is NOT an exhaustive aggregate of all earlier post-v54 source research (#323/#326 and many others), nor a change to historical v54 dispositions or a MC-B numerator.

PB-007-01 remains globally OPEN (general noncommon-factor/nonmonotone event completeness, identity-zero and cross-chart order), PB-007-02 coupled semantics OPEN, PB-007-03 source codec OPEN_PROPAGATED and PB-007-04 topology OPEN_PROPAGATED. Relevant PO-02/04/05/07/08 remain open. MC-B and MC-1 remain NOT_ESTABLISHED; production_authorized=false. Native material/topology, conventional usable B-rep/STEP, journal, all 26 domain operations, machining source/phase/provenance, durable bodies/lineage and typed UNCERTIFIED/resource refusals are unchanged.

**Next proof frontier:** source-attested generic V43/combined original-span witness-consumption and independent completeness transfer, with actual historical nonmonotone and tangential falsifiers, rather than another synthetic field-only result.
