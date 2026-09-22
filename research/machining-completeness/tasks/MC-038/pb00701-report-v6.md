# PB-007-01 follow-up v6 — exact rational-turn endpoint isolation

Issue: #170  
Parent integration gate: MC-038 / #100  
Source baseline: `fc11c30529c08db1524a99354843c174210a9797`  
Disposition: **exact rational-turn endpoint extension established for the constant-coefficient trig branch; PB-007-01 remains OPEN**  
Native/paid execution: **none**

## Purpose

The v3 PB-007-01 follow-up established an exact tangent-half/Sturm route for constant-coefficient rational trigonometric polynomials only when source-window endpoints were cardinal quarter turns whose tangent-half coordinates were themselves rational. It deliberately left arbitrary rational-turn endpoints and broader polynomial/B-spline-modulated phase predicates open.

This v6 addendum removes the first of those two restrictions without rewriting v3. The historical v3 model, artifact, report and verifier remain pinned byte-for-byte. The new construction admits arbitrary finite exact rational turns on one pole-free tangent-half branch and treats their tangent-half coordinates as exact real algebraic numbers rather than decimal approximations.

## Exact endpoint construction

For an exact rational source turn `t = p/q`, with `p/q` reduced modulo the tangent period into `(-1/2, 1/2)`, define `x = tan(pi*t)`. Expanding

`(1 + i x)^q`

shows that every finite such tangent value is a real root of the exact integer polynomial

`S_q(x) = Im((1 + i x)^q) = sum_{j odd} C(q,j)(-1)^((j-1)/2)x^j`.

On the principal tangent branch the positive roots are ordered exactly as `tan(k*pi/q)`, `0 < k < q/2`. The source numerator therefore selects the required root without a floating approximation. `pb00701_rational_turn_model.py` isolates that root by rational Sturm bisection using the reviewed MC-032 polynomial machinery. Negative turns are handled by odd symmetry and whole-turn-equivalent encodings reduce to the same principal source turn. The pole at half a turn remains an explicit blocker.

The isolated algebraic endpoint is stored as its exact defining polynomial plus a rational interval containing exactly one real root. The interval is evidence for root selection; it is not an epsilon substitute for the endpoint.

## Equality, sign and multiplicity at an algebraic endpoint

The event predicate remains the exact rational polynomial numerator obtained from the v3 tangent-half reduction. For an event polynomial `P` and algebraic endpoint `alpha` defined by `S_q`:

- `P(alpha) = 0` is decided exactly by `gcd(P, S_q)` together with the unique-root isolating interval;
- when equality is false, the isolating interval is refined with exact rational Sturm bisection until `P` has no root in the interval and both rational boundary values have the same nonzero sign;
- multiplicity is obtained by applying the same exact endpoint decision to successive derivatives of `P`;
- one-sided signs use the parity of the first nonzero derivative, exactly matching the rational-endpoint MC-032 convention.

This gives exact endpoint simple-crossing, odd-multiple-crossing and even-multiplicity-tangency classification without binary floating point or tolerance authority.

## Open-window root counting

MC-032's Sturm sequence is reused. Each Sturm polynomial is evaluated at the algebraic source endpoints through the exact one-sided endpoint-sign procedure above. The variation difference therefore counts roots strictly inside the source window while excluding an exact endpoint root. This matters for machining event partitioning: equality at a source boundary and an interior critical event are not interchangeable.

The adversarial controls include a non-cardinal simple root at turn `1/6`, an even-multiplicity tangency at the same turn, a hidden interior root between non-cardinal endpoints, exact endpoint exclusion from the open-root count, negative and whole-turn-equivalent encodings, pole crossing, inverted/empty intervals, source-parameter mismatch, binary-float authority, forged direct tangent-half coordinates, and resource-refusal laundering.

## Remaining PB-007-01 boundary

The v6 result is a real constructive advance but does not close PB-007-01. The endpoint algebraic-number problem is no longer the blocker for finite constant-coefficient rational trigonometric polynomials. The admitted MC-003/MC-007/MC-022 grammar is broader: exact rational B-splines and polynomial path/feed pieces can be coupled to trigonometric spindle phase. The resulting event predicates are not, in general, reduced by this work to the constant-coefficient trigonometric-polynomial case.

No unconditional finite exact decision construction for every required tangential, multiple-root or singular event in that broader coupled grammar is established here. No unproved transcendence conjecture, epsilon sign, finite sampling, refinement cap, timeout or resource refusal is promoted to correctness authority. This is not an impossibility theorem; it is the precise residual constructive boundary.

Therefore `PB-007-01`, PO-04, PO-05 and PO-08 remain **OPEN**. `PB-007-02` remains **OPEN** and still depends on the unresolved general PB-007-01 event authority. `PB-007-03` remains OPEN, `PB-007-04` remains OPEN_PROPAGATED, and MC-B / MC-1 remain `NOT_ESTABLISHED`.

## Protected semantics

The frozen denominator remains exactly 26 admitted operations. Historical source/audio/provenance and Genesis evidence are untouched. Canonical-journal meaning, exact shared time/path/phase correlation, source uncertainty, positive-volume material, holder/access semantics, durable body/lineage identity and conventional STEP output semantics remain unchanged. `BLOCKED`, `UNCERTIFIED`, `RESOURCE_REFUSAL`, timeout and refinement exhaustion are not success.

No native, paid, production or expensive campaign is authorized or run by this follow-up.

## Verification

The new evidence is checked independently while retaining the entire v3 check:

```text
python3 research/machining-completeness/tasks/MC-038/verify_pb00701.py --contract
python3 research/machining-completeness/tasks/MC-038/verify_pb00701.py --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v6.py --contract
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v6.py --self-test
python3 research/machining-completeness/tasks/MC-038/verify.py --contract
python3 research/machining-completeness/tasks/MC-038/verify.py --self-test
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

`mc1-static` must pass on the exact PR head before merge and independently on the exact merged `main` SHA afterward.

## Next repair path

The highest-priority remaining pre-gate work is still PB-007-01, but now specifically the polynomial/B-spline-modulated and generally coupled analytic-event grammar. A later pass must either establish another unconditional exact finite subroute or record the theorem boundary more sharply. MC-B must not be retried merely because rational-turn endpoints are now exact.
