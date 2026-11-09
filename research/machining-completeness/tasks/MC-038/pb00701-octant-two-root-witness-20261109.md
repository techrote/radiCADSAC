# MC-038 / PB-007-01 — exact two-simple-root witness inside one phase octant

**9 November 2026. Research only; deterministic mathematical model, not an original-source, machining, native or STEP qualification.** Repository authority: [MC-1](../../../../docs/machining-completeness/00-PROGRAMME.md), [DR-0026](../../../../docs/decisions/DR-0026-machining-completeness-programme.md), [MC-038 issue #100](https://github.com/techrote/radiCADSAC/issues/100). This leaf was developed from accepted main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9` under [#324 source claim](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6730025256). #397 retains exclusive main integration. No edits to #445/#446 or frozen V54/V2 evidence.

## Question and prior gap

[PR #445](https://github.com/techrote/radiCADSAC/pull/445) proves a restricted constant-H0/H1 signed-event transfer but deliberately refuses when two roots occur inside one open eighth-turn phase cell without separate rational isolators. We address **that specific refusal with a supplied rational witness**, not the entire source-time event-decision problem.

For `h,C,S,u,r ∈ Q`, with `r != 0`, `C²+S² > 0`, define

`F(t) = h + C*cos(2*pi*(u+r*t)) + S*sin(2*pi*(u+r*t))`.

Assume rational `a < p < b`, the phase endpoints `u+ra,u+rb` are integer multiples of 1/8 turn, and `|r|*(b-a)=1/8`. This is a **single exact open octant**, not a claim about a B-spline source knot. If independently certified strict endpoint values have common sign `sigma` and the rational pivot value has sign `-sigma`, two simple physical roots with rational, disjoint isolating intervals exist.

Falsifiers: a claimed sign interval contains zero; the source exceeds the exact octant; the source is stationary/zero harmonic; a supposed third root or a double root is compatible with the hypotheses; the committed tests/contract do not verify the receipt or misclassify the original motivating witness.

## Mathematical construction and completeness *within the restricted cell*

For any real `t` the derivative is

`F'(t) = 2*pi*r*(-C*sin(theta) + S*cos(theta))`, where `theta=2*pi*(u+rt)`.

Because `(C,S) != (0,0)`, neighboring zeros of `F'` are separated by **pi** in `theta`, whereas the admitted cell spans only **pi/4**. There can therefore be at most one stationary point in the open cell, including negative `r`. Strict signs `F(a)=sigma`, `F(p)=-sigma`, `F(b)=sigma` give roots separately in `(a,p)` and `(p,b)` by IVT. Three distinct roots would force at least two distinct stationary points by Rolle, contradiction. A multiple one of the two roots would likewise force an extra stationary point between distinct roots, contradiction. Thus **exactly two simple ordered roots**, with three maximal signed regions `[sigma,-sigma,sigma]` *on the admitted span*. This is a proof, not a dense numerical sample or subdivision heuristic.

## Exact rational sign arithmetic and receipt

The executable [source](pb00701_octant_two_root_witness_20261109.py) uses Python integer-rational `Fraction`, with no floating-point proof step. The Machin identity

`pi = 16*atan(1/5)-4*atan(1/239)`

and 28 alternating terms per arctangent yield rational strict lower/upper bounds for pi using the first omitted term. Reduce source phase modulo one turn to `[-1/2,1/2]`. Using midpoint pi, angle error is bounded by `|phase|*(pi_upper-pi_lower)`. The first 26 sine/cosine Taylor terms are rational and have Lagrange remainder bounds `4^53/53!` and `4^52/52!` respectively, since `|theta|<pi<4`. The 1-Lipschitz sine/cosine bounds propagate angular uncertainty. Coefficient-weighted rational intervals strictly enclose F, then are rounded **outwards** onto a 2^-40 rational grid for compact, auditable receipt fields. Signs are accepted *only* when the full unrounded enclosures prove strict positivity or negativity **and the outward-rounded receipt retains a strictly nonzero bound**; otherwise `DYADIC_RECEIPT_NOT_STRICT` refuses. This additional test prevents receipt compression from advertising a sign that an independent reader cannot verify from the serialized interval.

Inputs must be genuine int/Fraction (no floats or booleans), each numerator and denominator <=512 bits. Derived source-phase values beyond the input budget and undecidable sign intervals explicitly raise `RefusedNontruth`: not zero, not complete and not a proof of impossibility. Exact limits 28/25 are fixed: near enough to zeros, a real nonzero sign may also fail closed.

The returned source-spec SHA-256 binds canonical textual values of h,C,S,u,r,a,p,b; it is **not** the SHA of an original frozen B-spline source. The receipt explicitly records both strict rational root brackets, root orders, three signed regions, point intervals, zero new historical closures, zero required PB/PO discharges, and `NOT_ESTABLISHED` MC-B/MC-1. There is no claimed source knot, global event coverage or native semantics.

## Reproducible prospective positive challenge

Take `h=199/200`, `C=-3/5`, `S=-4/5`, `u=1/8`, `r=1/8`, `a=0`, `p=1/4`, `b=1`. This is #445's previously refused *same-octant double-root* type, with exact strict signs `POSITIVE,NEGATIVE,POSITIVE`. The certificate establishes exactly one simple zero in `(0,1/4)` and one in `(1/4,1)`. No algebraic or rational root **coordinate** is invented.

An adversary with a true value of magnitude `2^-100` is also refused because the outward 2^-40 receipt would erase its strict sign. An opposite-sign mirror tests `NEGATIVE,POSITIVE,NEGATIVE`; reversed `r` tests source-time order; adding an integer to `u` tests periodic reduction. Eleven tests also include wrong-cell widths, insufficient pivot, exact node zero, stationary/zero harmonic, non-rational values, and input bit-budget refusals.

## Commands and validation

From repository root:

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701_octant_two_root_witness_20261109.py --self-test
python3 research/machining-completeness/tasks/MC-038/pb00701_octant_two_root_witness_20261109.py --contract
python3 research/machining-completeness/tasks/MC-038/pb00701_octant_two_root_witness_20261109.py --demo
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py
```

Dedicated exact-head CI checks the new ten methods/contract, full historical V54/V2 50-source producing replay, and repository-wide static rules. This is a **prospective constructive positive restricted C**, not a discharge of PB-007-01/02/03/04 or PO-02/04/05/07/08.

## Negative findings and boundary to the next engineer

The previous unmodified #445 classifier cannot assert two separately bracketed roots solely from endpoints. The **new additional rational pivot is an explicit premise**, not automatically discovered for every possible source; it is therefore not a complete analytic-event decision procedure. Fixed interval precision can refuse arbitrarily close nonzero cases. The new certificate is task-local and has not been wired into #445 or a generic original-source composer. The rational pivot must be independently certified for each source; no frozen V54 source was modified or newly closed.

Historical baseline remains **121 original sources / 20 prior route refusals / 30 missing ordered premises / 50 existing complete source-specific witnesses**, all deltas zero. Evidence class: DETERMINISTIC_MODEL only. MC-B and MC-1 remain NOT_ESTABLISHED. Original 26-operation grammar, machine/journal/body/topology invariants, native geometry, engineering STEP and production authorization are unchanged.

**Downstream candidate:** an owner-approved generic rational-pivot search/refinement that terminates on every strict same-octant two-root case, plus authenticated B-spline cell/knot composition, independent review and #397-controlled integration. Do not infer that those extensions have already been proved.
