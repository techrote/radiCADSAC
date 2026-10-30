# MC-038 / PB-007-01 — bounded variable-rank real multiquadratic embedding

**Date:** 30 October 2026. **Status:** proposed, independently falsifiable DETERMINISTIC_MODEL research; not an MC-B/MC-1 capability decision. **Owner:** [MC-038 / #100](https://github.com/techrote/radiCADSAC/issues/100). **Pre-registration:** [issue comment 6521493091](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6521493091). **Pinned baseline:** main f113c495a6b50ca8164a27a3593b901352c103bd (PR #319, independently checked fixed Q(√2,√3) source model). The original frozen V44 source is 'harvested:verify_pb00701_v44:ffaea08e30c9', SHA-256 d3b3a90024ea283dfd96811b8fc2b66ceff621b3b48defc44c77f85557adbba2. This note specifies the experiment; do not infer hosted validation from the initial content.

## Hypothesis and falsification

A bounded *family* of embedded real multiquadratic fields with 1–3 independent squarefree positive integer generators can be constructed and checked using exact rational arithmetic, without assuming the hard-coded four-dimensional field from PR #318. A field's basis coordinates and real embedding must be explicitly bound to an **ordered generator tuple**, and the system must refuse dependent quadratic generators, non-squarefree inputs, ambiguous sign enclosures, bit-budget exhaustion and forged certificates. A counterexample is any admitted field with an incorrect product/sign/inverse, a dependent field admitted as degree 2^n, or a forged sign accepted.

Scope is **degree 2, 4 or 8 only**: generator integers 2–10,000, squarefree, independent in rational square classes; at most three; exact fractions.Fraction coefficients, <=1024 input coefficient bits, <=8192 intermediate arithmetic bits. This is not a primitive-element constructor, arbitrary real algebraic field, general algebraic-compositum algorithm, transcendental endpoint zero decider or nonmonotone event isolator. Bounded refusal is not a solved physical case.

## Exact mathematics and embedding

Let d_0,...,d_(r-1) be squarefree positive integers, and S_i their prime-factor parity sets. Require the parity symmetric difference over **every nonempty subset** of S_i be nonempty. This is the explicit finite F_2 square-class rank check. It excludes, for example, (2,3,6), (6,10,15), duplicate (2,2) and non-squarefree (2,8) rather than silently quotienting basis elements.

By the multiquadratic extension theorem, independent square classes give degree 2^r and linearly independent monomial basis e_I=√(∏_{i∈I}d_i). Choose the all-positive real embedding. Products use **exact** e_I e_J = (∏_{i∈I∩J}d_i)e_(I XOR J), computed with integer and rational coefficients. Nonzero elements have rational-linear-multiplication matrices of full rank; exact Gauss–Jordan solves their inverses with verified identity. Every element belongs to exactly one ordered generator tuple. No floating-point comparisons are used.

To prove strict signs, use isqrt(D·2^(2b)) to bound each positive radical √D inside outward dyadic rational endpoints at precision b; multiply enclosure endpoints by signed rational coefficients. A strictly positive lower or strictly negative upper endpoint is a checkable sign witness; the precise rational lower/upper and bit precision are emitted. **Only an all-zero basis tuple is exact zero.** For any nonzero tuple, field linear independence and convergence of dyadic bounds imply *mathematical* eventual strict separation. This finite implementation is limited to precisions (8,16,32,64,128,256,512); an unresolved sign is a typed RESOURCE_REFUSAL, never zero. Sign-certificate validation independently reconstructs the canonical element and exact interval at the submitted precision, rejects changed sign/limits/identity, and supports an exact zero witness.

The field rank test uses bounded trial factorisation of the small generator inputs. It is **not** a general integer factorisation algorithm and does not assert scalable feasibility.

## Reproduction and source custody

Run the focused verifier at the literal submitted PR head:

    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_multiquadratic_embedding.py --contract --self-test
    python3 tools/validate_machining_completeness.py --self-test

The new verifier checks the previous independent arithmetic source Git blob 5e4148b608038fe11b7ed02ac0e45cd0e3421e51 and replays its full frozen original-source/owner pin and 625-vector challenge. It then rechecks **625 degree-four field signs** against the old separate nested-conjugation producer. The **new** degree-eight field Q(√2,√3,√5) receives all 64 basis products, 25 rational-coefficient inversions, signed interval witnesses and independent parser/certificate forgery controls. Tests cover rank-dependence rejection, mix-ups between differently ordered fields, zero inverse, exact zero witnesses, cancellation-adjacent strict signs and exhaustion. A passing rank-three test is not validation of physical source events in that larger field; no such source owner is claimed.

Initial offline preflight: all five source-independent test cases passed using a stub only for the unavailable GitHub transitive source import. They are **not** evidence of the source-bound sixth case. The exact-head hosted workflow is required before any integration decision. Retain failures and exact workflow source/runtime identity in #100.

## Implications and remaining obligations

- The bounded field grammar now separates **dependent square roots** from independent embedded fields; the prior fixed-field result is an independent regression oracle, not inherited general truth.
- A possible later child restriction consumer must source-bind an original exact polynomial/phase and prove its child endpoints lie in the chosen field. This experiment provides no such general adapter.
- An arbitrary V41/V47 real-algebraic cut may lie in a non-multiquadratic extension. It is explicitly unsupported here. Event coincidence and analytic source-zero equality at irrational phase remain unresolved, as does nonmonotone root isolation and certified termination for general admitted trajectories.
- Historical v54 stays BLOCKED; PB-007-01/MC-038 remain open; MC-B and MC-1 remain NOT_ESTABLISHED. No domain, corpus, proof registry, native output, engineering STEP, current authority or production authorization is changed. No native/paid permit is used.
