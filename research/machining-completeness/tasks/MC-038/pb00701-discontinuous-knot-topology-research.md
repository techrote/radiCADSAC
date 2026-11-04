# MC-038 / PB-007-01 — discontinuous source-knot point membership and sign-transfer falsification

**Scope:** bounded, independently reproducible mathematical **negative result C**, pending CI/review qualification. **Evidence class:** `DETERMINISTIC_MODEL`, not native geometry, material/lineage, independent STEP, or production. **Issue:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). **Preregistration:** [#100 comment 6624723818](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6624723818); [coordination #324 comment 6624723114](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6624723114). The initial preselection main `5c6df327...` was superseded by disjoint #365 merge; the branch was created from new verified `main=316cf64b87a54a9f2cb6e8ab5e633eff14827dca`. No existing proof/registry/ledger writes.

## Named obligation, hypotheses and original source

PB-007-01, category-3 source-bound exact ordered physical zero/sign-event transfer, with downstream PO-04/05/08. Two shortcuts are falsified:

1. Promote an original degree-zero B-spline **OPEN** span's identity-zero proof into a **closed** zero interval at a true discontinuous original knot, without checking the actual knot-point value.
2. Infer all ordered sign transitions from zero-set locations alone, without considering exact one-sided source limits and the true point policy at discontinuities.

The actual proposed original B-spline source has grammar `RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE`, parameter `source-time-t` on `[0,2]`, original phase turns `beta(t)=t/16`, one H1 cosine channel with degree `0`, knots `[0,1,2]`, controls `[0,1]`, no sine channels. Canonical JSON source SHA-256 is `4860a921cea8332762d2db3f5aaeafa286593b230299f44d07ffc3a9bbcbd136`. The original source is **prospective**, not any of the frozen v54 121 identities.

The exact original degree-zero Cox–de Boor definition uses `N(i,0,t)=1` iff `knot[i] <= t < knot[i+1]`; hence its two original open-piece amplitudes are **0** on `(0,1)` and **1** on `(1,2)`. An **explicit** right-continuous internal-knot point policy (and terminal clamping at `2`) gives amplitude 1 at `t=1`. An alternative left-internal point completion keeps **the same exact open-piece evidence** but sets amplitude 0 at `t=1`; it is labeled **counterfactual**, not asserted to be the accepted canonical source convention.

The global rational phase on the full original source lies in `[0,1/8]`, strictly inside `(-1/4,1/4)`. Elementary exact trigonometric sector mathematics implies `cos(2*pi*beta(t))=cos(pi*t/8)>0` everywhere on the closed source. Therefore physical zeros depend **only** on exact amplitude zeros:

- **Right-internal policy:** physical `F(t)=0` for `0<=t<1`; `F(t)=cos(pi*t/8)>0` for `1<=t<=2`. **Zero set `[0,1)`** and one positive sign component `[1,2]`.
- **Left-internal counterfactual:** same open pieces but `F(1)=0`; **zero set `[0,1]`** and one positive component `(1,2]`.

A zero set `[0,1)` is not relatively closed inside `[0,2]`: for every positive integer `n`, `x_n=1-2^-n` is a zero, while `x_n` converges to nonzero `t=1`. Any finite union of closed zero components and finite isolated points must be closed. Hence a **closed-only finite zero-set grammar cannot express this particular right-internal original source**; the consumer must admit half-open components, explicitly bind knot-point semantics, or return nontruth/refusal. No continuous extension may be silently assumed.

## Distinct exact sign-jump falsifier

Keep **the same original knots, source parameter and affine phase** but change only the original amplitude controls to `[1,-1]`. The complete physical zero set is **empty**, because cosine is strictly positive throughout and both amplitudes are nonzero. Nevertheless, the left physical germ is positive and the right germ negative; at `t=1` the right-internal physical point is negative. The sign jump is a **discontinuity without a zero**, not an odd root/crossing and not a fabricated global root multiplicity. A zero-set-only ordered physical sign-transfer adapter is therefore insufficient for this admitted mathematical family. Source SHA-256: `97c4d80e91b4bee8a018d97ea7c1b3b8e7c3765cd37a7e4590f3caef98a4fb51`.

## Positive bounded companion theorem, proof and cost

The executable's admitted subgrammar requires exactly one H1 cosine original degree-zero clamped two-span source, canonical exact rational `L<K<R`, two exact rational controls, an affine rational phase whose **two source exterior phase turns are each strictly within** `(-1/4,1/4)`, and the separately explicit right-internal or counterfactual left-internal point policy. All other harmonic/sine/degree/source-parameter grammars refuse. Exact affine interpolation proves the phase stays in the positive cosine sector on both entire spans, even with nonzero/negative phase rate. Each original open piece is identically zero iff its exact control is zero; otherwise its sign equals the exact rational control's sign. The selected knot point policy, not the open-piece proof, determines inclusion at `K`. If both controls vanish, zero components combine into `[L,R]`; if only one vanishes, the proper boundary flag is retained. Opposite nonzero signs create distinct sign cells at a genuine discontinuity even when the zero set is empty. No smooth multiplicity is synthesized.

Termination follows from a fixed two-control/three-knot rational grammar, constant-size sign/identity decisions, two exact phase endpoint inequalities, and finite representation construction. No subdivision, root sampling, numerical pi estimate, geometric epsilon, timeout, or resource exhaustion is truth authority. Canonical rational input is bounded to 160 bits, derived phase terms to 512 bits, source bytes to 16 KiB and report bytes to 64 KiB; exhaustion causes only `RESOURCE_REFUSAL`. Phase touching `±1/4` is **refused**, not claimed root-free. Repeated/tangential isolated roots and arbitrarily close roots are outside this constant-signed subgrammar; the tests deliberately challenge extremely small exact nonzero controls `±2^-120` rather than relabeling them identity-zero.

A source-bound report includes the original canonical SHA, phase/knot/parameter, explicit internal point policy, both one-sided relations and signs, the actual source-knot point sign, all maximal zero and sign components with **both endpoint closure flags**, and literal false gate/capability claims. Any mutated source, point policy, closure flag, sign, zero count, source SHA or gate flag fails exact recomputation.

## Historical census, custody and reproduction

The verifier checks pinned Git blob identities for all **121 frozen original cases** from `pb00701-finite-owner-corpus-v54.json` (blob `5841c331579489b25caef38cd412bdbf286f9134`) and **50 accepted supplemental source-specific witnesses** from `pb00701-post-v54-evidence-reconciliation-v2.json` (blob `e52d3baf3692a011cf86234eeaa992ef407d99fd`). It checks case IDs against the exact frozen 20 route-refused and 30 missing-ordered sets, every original source spec SHA-256, historical owner/provenance/disposition and registered complete evidence class. This checks identity/census; the existing post-v54 workflow remains the independent full producer replay and must not be represented as run unless it actually runs.

| Same pinned historical cohort | Before | After | Delta |
|---|---:|---:|---:|
| All frozen original sources | 121 | 121 | 0 |
| Original route refusals | 20 | 20 | 0 |
| Missing ordered premises | 30 | 30 | 0 |
| Complete supplemental original-source evidence | 50 | 50 | 0 |
| Newly resolved historical IDs | 0 | 0 | 0 |

**Reproduce in checkout:**

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701_discontinuous_knot_topology.py --contract
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_discontinuous_knot_topology.py --contract --self-test
```

**Nonclaims:** This prospective example does **not** change frozen v54 dispositions, reduce the 50-source historical denominator, solve the general analytic event theorem, establish a policy for all source codecs, accept any PB-007-01/02/03/04 or PO-02/04/05/07/08 obligation, establish MC-B/MC-1, authorize native work/production, or weaken the 26-operation machining domain, source/uncertainty, canonical journal, bodies/lineage, usable engineering STEP, or independent consumer qualification. The counterfactual left policy is not a claim that canonical Cox–de Boor chooses the left span.

**Next critical dependency:** a reviewed PB-007 original-source semantics policy must define discontinuous *point values* (internal and terminal), separate true knots from analytic partition cuts, and make exact half-open zero components and nonzero sign jumps first-class checked evidence. A generic moving-phase multi-span proof would then combine independently established finite roots, continuum components, one-sided orders/signs and real knot point membership; merely adding more synthetic arithmetic cannot close PB-007.
