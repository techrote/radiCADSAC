# B1-E4 — Typed rational C0 quotient: complete zeros from a closed-nonzero divisor

**10 November 2026 · DETERMINISTIC_MODEL · speculative A/B research · Draft / HOLD**

## Question, scope, falsifier

Can exact B1 certificates for a rational-polynomial C0 numerator `N`, plus an endpoint-complete strictly nonzero denominator `D`, prove the entire signed zero set of a **newly typed rational expression** `N/D` without pretending the quotient has a polynomial Bernstein vector?

[Preregistered B1-E4 #324 lease](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6758087818) identifies decisive falsifiers: missing zeros at introduced partition knots; accepted denominator zero on a genuine seam; wrong CROSS/TOUCH/continuum or sided signs under negative division/time reversal; forged parent, event, pin or stale generation; and resource refusal classified as truth.

This deliberately extends the **represented expression class**, not the frozen V12/V6 originals or general H0/H1/H2 root isolation.

## Typed grammar and provenance

Each input is a complete, independently rechecked `b1-snapshot-v1` **base** record: finitely many ordered contiguous C0 rational power-basis polynomial pieces on the *same closed rational interval*, each with an exact `POS`, `NEG`, or `ZERO` Bernstein weak-cone receipt. Existing B1 source constraints apply (degree ≤24, 1024-bit rational input cap, up to 512 input leaves); union-of-breakpoints refinement is capped at 128 leaves. All arithmetic is exact `Fraction`.

Both parent snapshot hashes must be supplied as independently held exact 64-hex SHA-256 content pins. A user-provided hash **is not a producer signature or proof of physical B-spline provenance**. External custody must bind the actual source. Changes to source/knots/parameters, a journal edit, material update, restore or rollback invalidate the consumer receipt unless new complete parent pins are trusted and replayed.

The implementation reuses existing [B1-E3 `_parent` and `_refine`](https://github.com/techrote/radiCADSAC/pull/473), which replay leaves/seams and exact de Casteljau split at the sorted union of rational breakpoints. It then invokes B1-E2 `_closed` on the *already verified/refined* denominator: every piece must have strict same-signed nonzero values on both closed endpoints within B1's weak sign cone. Weak POS with a zero endpoint is **not** closed-nonzero. Mixed-sign Bernstein coefficients return typed `UNKNOWN/Refusal` even where the underlying polynomial happens to be positive.

The result is a separate `b1-rational-quotient-v1` receipt with source pins, generations, full ordered knots, aligned exact source hashes, denominator strict sign, exact zero continua, signed isolated events, piecewise open signs and canonical expression digest. It is explicitly `RATIONAL_C0_NOT_BERNSTEIN_POLYNOMIAL`; it must **never** be fed back into B1's polynomial certificate consumer or relabelled as A1/A2/MC-038 physical-source evidence. `verify` reconstructs it from original parents and refuses any changed field or optional externally held quotient expression hash.

## Closure law and proof — infinite rational family

Let `I=[a,b]` with rational endpoints, `N,D:I→Q` be C0 piecewise rational-polynomial functions with B1-verified complete weak-cone partitions, and let B1-E2 verify either `D(t)>0` for **all** `t∈I` or `D(t)<0` for **all** `t∈I`, including every source and introduced knot. Then the quotient `R=N/D` is defined and continuous on all `I`; it has **exactly** the numerator's complete zero set, including maximal identity-zero intervals and isolated endpoints. On each open cell `sign(R)=sign(N)*sign(D)`. Every isolated CROSS, TOUCH or BOUNDARY class is preserved, while its sided signs are multiplied by the single denominator sign. A previously proved finite local analytic numerator zero order `m` is preserved wherever `D` is analytic and nonzero (conditional: this verifier does not compute multiplicity).

**Proof.** The reused exact B1 splitting is pointwise value preserving. On each refined closed piece `D` never vanishes, so `N/D=0 ⇔ N=0` pointwise, including genuine and artificial knots. By continuity and connectedness, D's sign cannot change. Multiplication of both sided signs by one constant cannot change CROSS/T0UCH equality or difference. The usual quotient-continuity theorem supplies global C0. An analytic nonvanishing reciprocal is a unit in the local analytic ring, preserving established order. All statements apply to infinitely many rational coefficients/breakpoints under the explicitly bounded source grammar.

This is elementary rational-function algebra and classical Bernstein/de Casteljau mathematics, **not a new zero-isolation theorem**. Existing source-critical context: [#462 B-spline knot insertion and rational-affine covariance](https://github.com/techrote/radiCADSAC/pull/462), [#453 bounded event partition](https://github.com/techrote/radiCADSAC/pull/453), [A2 continuum alias](https://github.com/techrote/radiCADSAC/pull/471), and B1-E2/E3 in [#473](https://github.com/techrote/radiCADSAC/pull/473). Source codec admission, knot provenance and phase units are *not* inherited from #462.

## Reproducible bounded computation and negative evidence

At the exact published PR head:

```sh
cd research/experimental/certificate-algebra/core
python3 -m unittest -v test_rational_quotient.py
```

Infinite example family: `N(t)=t-α`, `D(t)=σ(γ+(t-β)^2)` for rational `0<α,β<1`, `α≠β`, `γ>0`, `σ=±1`. Numerator is split at `α` and denominator at different `β`. The 9 authored methods check 36 rational parameter tuples, independent rational point evaluations/signs, tangency, identity-zero continuum, negative-time side reversal, genuine denominator seam zero refusal, source/local-germ alias, mismatched domain and malformed or altered event/source pins. A *mathematically positive* quadratic with mixed-sign Bernstein control is conservatively refused, demonstrating an admission **limit**, not a false result.

**Prepublication local evidence:** 9/9 test methods PASS on a separately implemented **source-compatible reconstructed** version of existing parent APIs. New source/tests syntax-compiled. This is **not exact published-parent-module execution**. Exact original B1 module replay, published blob equality, applicable hosted checks and independent A3/B5 review are still pending. Neither model correctness nor integration is accepted on the basis of this shadow alone.

### Certificate work accounting, not runtime performance

For `α=1/2, β=1/3, γ=1`, two two-leaf parents yield three aligned leaves. The derivation counts 4 parent full-leaf verifications, 2 existing exact split transformations and 3 quotient sign/identity transformations. Direct re-proof of both aligned polynomial partitions would need 6 leaf Bernstein conversions (plus seam checks). Only **2 leaf conversions are avoided**, and 5 differently priced transformations are added. This is **not** a speedup measurement; short instances may incur **net overhead**. Quotient output itself is not a polynomial, so no imaginary quotient Bernstein-proof comparison is permitted. No timing, allocations, native geometry, STEP, CyberSand tick, physical hash or production impact was measured.

## Review / open laws / integration boundary

**A3 request:** run the exact GitHub B1 parent module blobs; challenge source/interval/pin forgery, `[0,1/2,1]→[0,1/2,-1]` right Bernstein substitution despite the unchanged local knot first jet, nonzero-denominator seam, negative affine orientation, continuum and qualified proof scope. Require independent rational evaluations and complete event enumeration.

**B5 request:** review whether `RATIONAL_C0` is a sound separate consumer type, without treating caller-held hashes as native source custody. No auto-import of A1 signed-cell receipts, A2 sided multiplicity, #462 structural knot/controls, arbitrary Boolean topology, fluid simulation caching or real signed physical source semantics.

Unknown/non-admitted cases include arbitrary nonzero functions outside the Bernstein sign cone, H0/H1/H2 trigonometric quotients, denominator poles or removable-zero cancellation, discontinuous sources and nonlinear phase. If numerator and denominator both vanish at a knot, **refuse** rather than assume cancellation. Exact rational size and the 128-cell cap remain binding. New producer/invalidation, cross-lane verifier semantics, actual timing and full physical implementation are open.

**Authority unchanged:** 121 frozen originals, 20 historical route refusals, 30 absent ordered premises, 50 previously complete witnesses; **zero** new original closures; 26 machining operations. MC-B/MC-1 `NOT_ESTABLISHED`, `production_authorized=false`. No shared/programme/proof registry, MC-038, production or native source changes. **Draft / HOLD / DO NOT MERGE** pending independent source-level replay.
