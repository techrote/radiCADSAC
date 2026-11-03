# Complete original V10/V11 sources from conditional ratio charts

**Recorded:** 3 November 2026. **Task:** [MC-038 / issue #100](https://github.com/techrote/radiCADSAC/issues/100). **Preregistration:** [scope reservation 6591720927](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6591720927) and [exact original IDs 6591724660](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6591724660). **Source baseline:** `e8108b98af35c4c4fd72a0cbf224a4b1aea0740c`. **Evidence class:** deterministic exact source-bound model research.

## Purpose and complete source results

This leaf proves the missing first-span ordered events for four frozen original sources and composes them with three freshly replayed historical tail producers. It establishes complete event and sign views on the original closed interval [0,2], including original exterior endpoints and the true source knot at 1.

The selected original owner IDs are:

- `PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO`;
- `PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO`.

Each full case ID is `composite:` followed by the owner ID and either `:tail0` or `:tail100`. Their exact original source and complete-row hashes, controls, phase, historical observations and fresh tail receipts are retained in the [machine report](pb00701-ratio-prefix-composition.json).

| Original source | First-span roots | Tail roots | Closed-source roots | Maximal physical signs |
| --- | ---: | ---: | ---: | --- |
| V10 tail0 | 4 | 4 | 8 | −,+,−,+,−,+,−,+,− |
| V10 tail100 | 4 | 1 | 5 | −,+,−,+,−,+ |
| V11 tail0 | 4 | 4 | 8 | +,−,+,−,+,−,+,−,+ |
| V11 tail100 | 4 | 0 | 4 | +,−,+,−,+ |

Every physical root is simple and lies strictly inside one original source piece. All four true source knots are continuous and nonzero. All eight exterior endpoints are nonzero. There is no continuum-zero component. Chart poles and bracket boundaries are proof cuts, not physical zero events.

The original historical classifications remain correct descriptions of the older proof scopes. The frozen V54 census remains **121 original sources / 20 route refusals / 30 missing ordered premises**. This leaf does not modify those original owner/refusal observations. Registration as accepted complete evidence is a subsequent integration action after independent review and qualification.

## Original source identities and exact lowering

All four sources use `source-time-t` on [0,2] with actual original piece boundaries [0,1,2]. Each amplitude is a fully clamped two-span rational B-spline. The checker verifies the degree, complete knot vector, control count, exact rational values and equality of the two sided values at the original knot before using a channel.

The V10 first span is

`F(t) = cos(theta) + (1/2-t)*sin(theta)`, with `theta=4*pi*t-pi`.

Its phase turns are `-1/2+2*t`; its cosine coefficient is one and its sine coefficient has Bernstein controls `[1/2,-1/2]`. On the second span the sine coefficient is the constant `-1/2`, while the harmonic-zero term is `k*(t-1)` for k=0 or 100.

The V11 first span is

`F(t) = A(t)*cos(theta) + sin(theta)`, with `A(t)=t^2-t+1/8` and `theta=4*pi*t`.

Its phase turns are `2*t`. The quadratic cosine coefficient has Bernstein controls `[1/8,-3/8,1/8]`; exact power-basis reconstruction gives `[1/8,-1,1]`. On the second span that coefficient is the constant `1/8`, the sine coefficient stays one and the harmonic-zero term is again `k*(t-1)`.

The conditional lemmas accept bounded Bernstein amplitudes beyond these four frozen rows. The frozen wrapper separately binds the full source and complete provenance row. Thus a successful synthetic conditional lemma cannot be substituted for an accepted original-source receipt.

Bernstein basis functions are nonnegative and sum to one on a unit interval. A derivative control hull therefore supplies a bound on the derivative throughout the original span. The implementation checks derivative control identities against exact power-basis differentiation, and every rational sign witness against both Bernstein and power-basis evaluation. The only numerical constant used by the chart derivative bounds is the classical strict inequality `pi>3`.

## Cotangent lemma: four V10 prefix crossings

Consider `F=cos(theta)+B(t)*sin(theta)` with the stated original V10 phase. The sufficient checker requires an exactly zero harmonic-zero prefix, a unit cosine coefficient and a Bernstein derivative upper bound `u=max(B' controls)<12`.

The four open charts have endpoints

`0, 1/4, 1/2, 3/4, 1`.

The sine is nonzero inside each chart. Dividing there gives

`H(t)=cot(theta)+B(t)`, with `H'=B'-4*pi*csc(theta)^2 < u-12 < 0`.

The polynomial amplitude has finite sided limits, while cotangent decreases from positive infinity to negative infinity over each chart. Consequently each chart contains exactly one zero. At a zero, `F'=sin(theta)*H'` is nonzero, proving analytic order one. At the chart poles the original source is cosine, with exact values `−1,+1,−1,+1,−1`, so division has not lost or invented a physical zero.

For the original amplitude, `B'=-1` and therefore `H'<-13`. Exact quadrant evaluations give these strict brackets:

| Root order in the prefix | Open bracket | Exact boundary values of F |
| --- | --- | --- |
| 0 | (1/8,1/4) | (−3/8,1) |
| 1 | (3/8,1/2) | (1/8,−1) |
| 2 | (1/2,5/8) | (−1,1/8) |
| 3 | (3/4,7/8) | (1,−3/8) |

Each bracket is contained in its unique chart. Adjacent isolating intervals may share a proved nonzero boundary point; their roots are still strictly ordered because the intervals are open. The complete prefix sign sequence is `−,+,−,+,−`.

## Tangent lemma: four V11 prefix crossings and an empty initial chart

Consider `F=A(t)*cos(theta)+sin(theta)` with the stated original V11 phase. The sufficient checker requires an exactly zero harmonic-zero prefix, a unit sine coefficient, positive `A(0)` and `A(1)`, and a Bernstein derivative lower bound `l=min(A' controls)>=-12`.

The cosine poles are

`1/8, 3/8, 5/8, 7/8`.

On each chart, where cosine is nonzero,

`H(t)=A(t)+tan(theta)`, with `H'=A'+4*pi*sec(theta)^2 > l+12 >= 0`.

The derivative is strictly positive even when the displayed rational bound is zero, since `pi>3` is strict. The initial truncated chart [0,1/8) has positive left value `H(0)=A(0)` and increasing H, so it contains no zero. Each of the three complete middle charts goes from negative infinity to positive infinity and contains exactly one zero. On the final chart (7/8,1], H starts at negative infinity and ends at `A(1)>0`, so it contains exactly one zero.

The original source values at all four cosine poles are the nonzero sine values `+1,-1,+1,-1`. At each interior zero, `F'=cos(theta)*H'` is nonzero. The original amplitude derivative controls are `[-1,1]`, giving `H'>11`.

| Root order in the prefix | Open bracket | Exact boundary values of F |
| --- | --- | --- |
| 0 | (1/4,3/8) | (1/16,−1) |
| 1 | (1/2,5/8) | (−1/8,1) |
| 2 | (3/4,7/8) | (1/16,−1) |
| 3 | (7/8,1) | (−1,1/8) |

The complete prefix sign sequence is `+,−,+,−,+`. The initial empty chart is part of the completeness argument; it is not omitted because the four expected roots have already been found elsewhere.

## Falsification controls: why the derivative and endpoint premises matter

The tests contain mathematical counterexamples rather than only changed report strings.

For the cotangent chart, choose `B=20*(t-1/8)`. At t=1/8, H=0 and `H'=20-4*pi>20-88/7>0`. Exact independent sign witnesses are `H(1/16)=-1/4` and `H(3/16)=1/4`, using cotangent values +1 and −1 at the corresponding angles. Its first-chart limits are positive infinity at 0 and negative infinity at 1/4. Continuity forces another zero on each side of the middle zero: at least three zeros occur in one chart. The derivative-control check rejects this source before applying the one-root chart theorem.

For the tangent chart, choose `A=40*(t-1/2)^2-5/2`. Its Bernstein controls are `[15/2,-25/2,15/2]`, so both exterior A values are positive. At t=1/4, H=0 and `H'=-20+4*pi<-20+88/7<0`. Exact independent sign witnesses are `H(3/16)=13/32` and `H(5/16)=-3/32`, using tangent values −1 and +1. Yet the containing full tangent chart (1/8,3/8) has limits negative infinity and positive infinity. Again, an additional zero exists on each side of the middle root. Positive A endpoints alone do not justify the one-root-per-chart conclusion; the derivative lower bound must be checked.

Finally, `A=t-1/2` has strictly positive H' but negative initial A and positive final A. Both truncated charts contain a root, as do the three middle charts, giving five prefix roots. The positive-initial-endpoint premise refuses this different chart-count shape.

The helpers also accept genuine nonfrozen positive controls. `B=1+11*t` satisfies the decreasing cotangent condition, while constant `A=1/8` satisfies the increasing tangent condition with different strict brackets. `A=20-12*t` exercises the strict `pi>3` margin at derivative lower bound −12. These controls demonstrate conditional reasoning beyond the selected identifiers.

An exact zero at a midpoint selected as a bracket sign witness is deliberately refused with a separate-branch reason. It is neither rounded away nor classified as root-free. The four frozen originals have strictly nonzero chosen sign witnesses, so this limitation does not remove any part of their complete proofs.

## Fresh tail replay and original-interval composition

The model executes the original mathematical code and `contract()` entry points of three pinned producers:

| Producer | Original tail result reused |
| --- | --- |
| [V10 tail0 four crossings](verify_pb00701_v43_v10_tail0_crossings.py) | Four simple crossings, with strict brackets (17/16,9/8), (21/16,11/8), (25/16,13/8), (29/16,15/8). |
| [V10 ramp crossing](verify_pb00701_v43_v10_tail_crossing.py) | One simple crossing in (1,101/100), with derivative strictly greater than 568/7. |
| [V11 tail contrast](verify_pb00701_v43_v11_tail_contrast.py) | Tail0 has four simple crossings in the retained strict brackets; tail100 is positive and root-free, with derivative strictly greater than 601/7. |

The old V11 tail0 brackets are (19/16,159/128), (23/16,191/128), (27/16,223/128) and (31/16,255/128). Each fresh selected tail result must match its pinned canonical digest before normalization. Source identities, [1,2] scope, ordered root intervals, multiplicities and endpoint signs are retained; a successful legacy report is not reinterpreted as a prefix or whole-source proof.

The new code independently evaluates the actual original source endpoints:

| Original source | F(0) | F(1) from both pieces | F(2) |
| --- | --- | --- | --- |
| V10 tail0 | −1 | −1 | −1 |
| V10 tail100 | −1 | −1 | 99 |
| V11 tail0 | 1/8 | 1/8 | 1/8 |
| V11 tail100 | 1/8 | 1/8 | 801/8 |

Coefficient continuity and these identical nonzero knot values allow the adjacent same-sign cells to merge across t=1. The compositor checks source identity, actual piece intervals, strict bracket order, uniqueness cells, multiplicity and endpoint signs. It concatenates the proved roots and constructs maximal sign cells whose only interior boundaries are physical roots. Rational chart poles, proof cuts and original nonzero knots never become event coordinates.

The reported coordinates remain implicit unique original-source roots in strict rational isolating intervals, carrying original source hash and parameter identity. No rational or algebraic closed-form source coordinate is asserted.

## Bounded input and executed-byte custody

Public source and report inputs receive bounded typed preflight before canonical hashing, serialization or rational parsing. Bounds cover depth, nodes, container sizes, string lengths, aggregate bytes and integer bits. Canonical bytes distinguish booleans from integers. Canonical ASCII rational syntax and bit limits are checked before `Fraction`; decimals, exponents, Unicode digit substitutes and unreduced or oversized rational tokens refuse. The finite conditional helpers admit degrees at most six and input rational components of at most 256 bits.

The verifier itself reads at most one bounded model buffer, verifies its fixed Git blob and compiles that exact buffer. It does not import the model through ordinary module caching. The model applies the same principle to the historical auditor and tail producer code. A module-local import facade restricts nested loading to the one pinned original lowerer, without changing global import machinery. The old producers retain their original contracts and mathematical functions; bounded exact-path adapters replace only their JSON-reader and blob-check entry points.

JSON is hashed and decoded from the same bounded buffer. Replacing a path after hashing cannot substitute the parsed input. Cached bytecode, preloaded modules, unlisted nested modules, unlisted data paths, dependency drift and failed fresh producer proofs remain nontruth. The wrapper has no runtime dependency on the separate component-carrier leaf.

The structural composition helper consumes already-proved views within this fixed wrapper. It is not a public mathematical verifier of arbitrary supplied assertions. Public report validation compares typed canonical bytes against a fresh replay, and public original-source proof entry points require the exact complete-row and source hashes before any legacy execution.

## Validation and qualification

The focused verifier has **29 adversarial methods** covering exact source reconstruction, both conditional lemmas and their positive controls, concrete multiple-root counterexamples, truncated-chart completeness, midpoint-zero refusal, original knot/phase/harmonic boundaries, source and complete-row custody, ordered composition, fresh producer execution/failure, resource limits, false gate claims and mutable report isolation.

Custody controls include actual timestamp/size-valid altered bytecode, preloaded module substitutions, nested lowerer bytecode, unchanged global importer state, JSON/model path replacement after hashing, bootstrap size/pin refusals and every legacy contract's guarded JSON reads. A per-producer regression exercises each actual contract's blob-check spelling: `git_blob` for the V10 ramp and `blob_sha` for the other two producers. This prevents an unused adapter from masking a retained legacy checker.

Reproduction commands:

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_ratio_prefix_composition.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_frontier.py --contract --self-test
python3 tools/validate_repo.py
python3 tools/validate_machining_completeness.py --self-test
```

The focused workflow has one Python job, read-only contents permission, literal PR-head checkout and an eight-minute timeout. Its sixteen exact path triggers cover these five files, the frozen corpus/inventory/coverage/auditor, the original lowerer, all three tail producers and the three domain/programme/authority files. It adds no broad MC-038 tree trigger.

Independent review of exact final bytes, literal-head hosted checks, matching reviewed and landed trees, guarded merge and merged-main qualification remain required. Accepted registry/current-state updates belong to the integrator after qualification; local passing tests do not perform those updates.

## Implications and retained limits

For MSAC, these proofs preserve the actual source parameter, source identity and manufacturing-intent provenance through event ordering. For OpenSimachinist, they supply four complete finite event/sign witnesses that a later source-bound consumer may integrate under the stated hypotheses. They do not establish a general ratio solver, general V43 route or universal proof-consumption mechanism.

The protected 26-operation domain, canonical journal, material/body/lineage semantics, refusal and `UNCERTIFIED` behavior, and conventional usable engineering STEP obligation are unchanged. PB-00701 remains open; MC-B and MC-1 remain `NOT_ESTABLISHED`; production authorization remains false. No native geometry, topology, B-rep, STEP-consumer, paid campaign or production qualification follows from this deterministic result.
