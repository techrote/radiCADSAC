# MC-038 / PB-007-01 — frozen V44 whole-source positive derivative

**Research status:** bounded deterministic-model candidate, 30 October 2026. **Parent:** [MC-038 / #100](https://github.com/techrote/radiCADSAC/issues/100). **Preregistration:** [#6515693808](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6515693808). **Selected base:** main a216ce4ffef88716feca80fc4b0806f7e29afa95, following source-matched merged-main qualification of [PR #313](https://github.com/techrote/radiCADSAC/pull/313). This memo is not an MC-B gate decision and does not itself assert any CI or merged-main validation.

## Purpose and exact frozen source

This leaf establishes a **strict positive physical first derivative on the entire original closed rational source interval** for one frozen V44 degree-2 trigonometric B-spline case. It is a different proof structure from PR #310's complete physical root partition and PR #313's strict root-bracket refinement, though it shares the reviewed #296 trigonometric enclosure engine and is **not an independent trig oracle**.

The sole source is harvested:verify_pb00701_v44:ffaea08e30c9 from the immutable historical v54 corpus; original canonical source SHA-256 d3b3a90024ea283dfd96811b8fc2b66ceff621b3b48defc44c77f85557adbba2. The original parameter is t in [0,1], with phase turns -1/8 + t/16. The exact source-lowered polynomials (in increasing powers of t) are:

| h | C_h(t) | S_h(t) |
|---|---|---|
| 1 | -3/2 + t + 2t^2 | -1/2 - t + 2t^2 |
| 2 | 1/100000000 | 0 |

The actual source is regenerated from the pinned original rational B-spline by the unchanged #310 source-lowering and complete-root producer; these written coefficients are separately checked against the regenerated span. A caller cannot supply substitute polynomials, phase, bounds or alleged root facts.

## Proof target and falsification criterion

Define the physical function on its *original source coordinate*:

F(t) = sum over h of [C_h(t) cos(2*pi*h*(-1/8+t/16)) + S_h(t) sin(2*pi*h*(-1/8+t/16))].

**Falsifiable hypothesis:** a fixed 16-cell exact rational partition of [0,1] suffices to prove **F'(t)>0 for every t in the closed original source**, using a global rational second-derivative magnitude bound and independently verified rational midpoint derivative enclosures. Refuse if even one closed cell cannot establish a strictly positive lower bound; do not interpret insufficient enclosures as a mathematical counterexample or infer a zero.

### Analytic global bound

Let k_h = 2*pi*h/16, theta_h(t) = 2*pi*h*(-1/8+t/16). Exact differentiation gives

F''_h(t) =
[C''_h(t) + 2*k_h*S'_h(t) - k_h^2*C_h(t)] cos(theta_h(t))
+ [S''_h(t) - 2*k_h*C'_h(t) - k_h^2*S_h(t)] sin(theta_h(t)).

For all t in [0,1], |sin| and |cos| are at most 1, and the independently pinned rational pi enclosure proves 0 < 2*pi < 44/7. Therefore |F''(t)| is at most

M2 = sum_h (||C''_h||_1 + ||S''_h||_1
+ 2*(44/7)*|h/16|*(||C'_h||_1+||S'_h||_1)
+ ((44/7)*|h/16|)^2*(||C_h||_1+||S_h||_1)),

where the coefficient L1 norm bounds a polynomial on [0,1]. The implementation independently reconstructs this bound from **all** source channels and checks equality with the #296 interval engine's stored m2. For the pinned source it is the exact rational

**M2 = 335000000121 / 19600000000**, approximately 17.09184.

No selected amplitude, sine channel, harmonic-zero channel or higher-harmonic term can silently drop from the expression.

### Finite closed-cell derivative proof

For dyadic closed cell I_i = [i/N,(i+1)/N], m_i=(2i+1)/(2N), and radius r=1/(2N), the mean-value theorem gives

F'(t) >= lower(F'(m_i)) - M2*r, for every t in I_i.

The unchanged pinned #296 Span.evaluate(midpoint, first_derivative=True) returns **exact rational outward enclosures** derived from Machin pi bounds and certified sine/cosine Taylor remainders; no IEEE numerical sample proves a sign. Each returned rational interval is *further rounded outward* on an exact 2^-32 rational grid to keep a finite audit-size record. This does not narrow the interval or lose soundness. The verifier recomputes the exact unrounded enclosure and checks both outward-rounded bounds, exact midpoint, exact drift and strict lower margin.

All 16 closed cells must have **strictly positive** lower derivative bounds, with exact neighboring endpoints and complete [0,1] coverage. The **minimum of the 16 rational lower bounds** is a source-wide *uniform* positive derivative lower bound. The 32-cell alternative is also checked. An 8-cell coarse cover is a deliberately preserved **negative proof attempt**: its global m2 drift overwhelms some midpoint lower bounds, so the classifier returns BLOCKED rather than pretending derivative positivity or mathematical nonmonotonicity. No adaptive fallback, hidden numerical sample or inference from finite endpoint signs can fill a failed cell.

### Consequences actually proved

1. With independently checked strict physical endpoint signs F(0)<0<F(1), source continuity and F'(t)>0 everywhere, IVT proves **exactly one simple physical root** on the original source, independently *in proof structure* of the #310 interval root-cover argument (but not independent of its trig enclosure arithmetic). The actual complete #310 root witness and #311 proof-cell atlas are regenerated and checked, rather than overwritten.
2. Four exact source proof cells are delimited by five exactly ordered original-source endpoints (including one irrational orientation proof cut); #311 complete source replay preserves their physical open-root counts [0,1,0,0] and signs. For each such closed child normalized by t=a+(b-a)u, exact cut order proves b-a>0. Hence dF/du = F'(t)*(b-a) > 0 **on the complete closed child**. This inherits a physical derivative theorem without evaluating cos/sin at an irrational endpoint and without treating a proof cut as a physical event.
3. This **does not** construct the versioned V45 Q(alpha) child analytic chart, does not decide all historical V41/V47 event/derivative premises or integrate an admissible v54 route, and does not extend to other frozen cases or a general timed/trigonometric zero algorithm. The global derivative theorem is strict for this one original source, not a universal method for all stationary or multi-harmonic curves.

## Source custody, report validation and refusal

The new model directly pins predecessor PR #313's Git blob 3adb5630b929b051153e43b423a6ad2e7893dc5f. Its transitive #311/#310 custody verifies the original v54 corpus blob 5841c331579489b25caef38cd412bdbf286f9134, #296 trig engine blob 2320f92efe4316d865a89f6d848737e2c000ca4d, #306 B-spline/cut-order chain, original 26-operation domain and production_authorized=false authority. No historical source or result changes.

The prove(cells=16, supplied_atlas=None) function returns a finite fully source-bound proof report. Allowed canonical Python integer budgets are only 8, 16 or 32; booleans, strings, floats and other counts refuse. Every submitted atlas is verified by complete pinned producer replay. validate_report bounds untrusted nesting and node count *before* JSON serialization, caps the serialized report, regenerates the **entire** source/cell report and rejects any forged bound, sign, cut or capability flag. It emits only BLOCKED or RESOURCE_REFUSAL nontruth upon failure; no partial successful proof.

The adversarial tests challenge source/phase/coefficient drift, pins, coarse-cover failure, exact cell and outward-rounding arithmetic, complete coverage, algebraic proof-child inheritance, forged reports, cyclic/deep/oversized inputs, insufficient-resource refusal and route/nonproduction flags.

Reproduce on the precise checked-out repository head:

    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v44_global_derivative.py --contract --self-test

The dedicated literal-head GitHub Actions workflow plus mc1-static, anchored source review, protected merge, matched Git trees and actual merged-main CI are required before treating the proof as a **qualified research increment**. This document deliberately does not preclaim those outcomes.

## Retained first-head qualification failure and correction (30 October 2026)

First PR #314 literal head `f88cdf9763a97a1d7eed079d166dad6f9ce885b8` ran focused [#41008821431](https://github.com/techrote/radiCADSAC/actions/runs/41008821431): **FAILED** (14 tests passed, one adversarial report-resource test errored). The standalone exact 16-cell proof contract succeeded, including four inherited proof children and strict global derivative lower bound `3402574703095661/10276044800000000`. However, a malicious deeply nested report raised the pinned predecessor model's `predecessor.ResourceRefusal` during the *pre-JSON structural cap*. The new `validate_report` previously caught only its own `ResourceRefusal`, so the test received a raw exception rather than required `RESOURCE_REFUSAL` nontruth. This was an API refusal-custody defect, **not** evidence of a false mathematical proof. The isolated correction adds `predecessor.ResourceRefusal` to the report-validation typed resource handler, retaining both this failure and its cause. Subsequent final-head CI, review and merged-main checks must be separately confirmed; no result is inferred from this failing run.

## Remaining theorem, production and historical boundary

Historical frozen v54 stays BLOCKED; MC-038/PB-007-01 and relevant PO obligations stay OPEN; **MC-B and MC-1 remain NOT_ESTABLISHED**. A frozen whole-source derivative proof does not deliver general Q(alpha) child source/derivative certificates or resolve all 16 missing owner families, other nested V27/V41 routes, tangencies or identity-zero sources.

No native material, topology, durable body/lineage, conventional engineering B-rep/STEP output, independent consumer, user-visible MSAC, paid/native campaign or production repository is authorized. The full **26-operation** lathe/mill denominator, source audio/provenance, canonical journal, exact path/time/phase, cutter/holder, unbounded admissible finite histories, resource refusal and UNCERTIFIED semantics are unchanged.

**Next bounded acceptance question:** determine whether this independently reconstructed source-wide derivative certificate can be consumed by a *source-bound, versioned exact-algebraic proof-child handoff* that preserves the original historical route's full precedence, proof-cuts/endpoint truth and witness replay, rather than silently upgrading the old V44/V47 claim. Any wider theorem needs separately scoped source-family correctness and termination evidence.
