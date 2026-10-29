# MC-038 / PB-007-01 — finite ordered nontransverse guards with complete interguard coverage

**Status:** 29 October 2026, conditional deterministic-model research only. **Parent:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100), [preselection and falsifiers](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6509923027). **Base:** `964bb935943eb41301a792e3d7f0922070ac5495` (reviewed merged PR #303). No historical v54 or native qualification is changed.

## Exact hypothesis and finite proof object

Take one canonical rational-polynomial-modulated finite-harmonic rational-affine-phase original-source span F on the **original source parameter** interval [L,R]. Admit a finite list of distinct exact rational roots `r_1<...<r_n`, n>=2, each strictly inside its own **disjoint** closed rational guard [a_i,b_i]. Require the guards themselves to be strictly ordered, internal to [L,R], and non-touching. The **claim is conditional on a successfully checked complete source partition**, not on the nominal list.

For every i, independently reconstruct the exact source and prove the #298 cyclotomic point jet has F(r_i)=...=F^(m_i-1)(r_i)=0 and strict signed F^(m_i)(r_i), m_i>=2. Use the full rational Leibniz/2π<44/7 global bound on |F^(m_i+1)| from reviewed #303, widen the strict m-th derivative point enclosure by `M_(m_i+1)*max(r_i-a_i,b_i-r_i)`, and demand strict unchanged sign. Taylor's integral remainder then proves that root is the **only** zero in its guard, with exact smooth multiplicity m_i, even tangency/odd crossing and one-sided signs. No numerical near-root matching is involved.

**New global composition obligation:** fully cover **all n+1 complementary intervals** [L,a_1], [b_1,a_2], ... [b_n,R] with rigorous closed dyadic cells from #303. Every cell receives a strict constant-sign enclosure `F(midpoint) +/- M_1*halfwidth`, where M_1 is a proved global rational first-derivative bound. Cells must tile their complete gap with no omissions; adjacent guard and gap signs and both true original-source endpoints must agree. The ordered union of n guards and n+1 signed gaps is a complete closed source partition. Therefore there are **exactly n distinct ordered physical source zeros**, with the stated finite multiplicities and crossing/tangency sequence. This theorem requires each source/root/guard/cover identity, full source interval, phase, every harmonic channel, checked certificate digest and a global bounded work budget. No point-local event alone implies whole-span completeness.

If a guard sign, gap enclosure, endpoint, parity, source identity or resource budget fails, the checker **refuses** and reports `is_truth_value=false`. No conclusion about unknown roots is drawn. This is a sufficient certificate class, not a universal zero-decision or root-isolation algorithm.

## Deterministic source-bound example and falsifiers

Complete **synthetic source** (not harvested v54 data):

- `source_parameter_id = source-time-t`, original interval `[-5/8,5/8]`, phase turns `0+1*s`.
- h=0 cosine amplitude `s`, h=2 cosine amplitude `-s`, both sine channels identically zero, other harmonics absent. Thus `F(s)=s(1-cos(4πs))`, genuinely polynomial-modulated trigonometric source.
- Rational roots `(-1/2,0,1/2)`, disjoint guards `r +/- 1/128`, orders `(2,3,2)`. Every left/right root sign follows the exact jet: double negative tangency, triple negative-to-positive crossing, double positive tangency. The four root-free gaps have signs `(-,-,+,+)`, including the two large interguard intervals.

An essential adversarial counterexample keeps **all three nominated nontransverse rational roots and their same multiplicities and one-sided signs** but inserts **two missed simple roots** at `1/8,1/4`:
`G(s)=s(s-1/8)(s-1/4)(1-cos(4πs))`.
The amplitude degree is 3, still within the existing exact source grammar. Endpoint and guard signs alone cannot detect the two even-numbered omitted crossings. The complete intermediate signed dyadic cover must refuse: `G` has zeros where a certificate claims a strictly root-free gap. Mutations additionally cover omitted/false roots, overlapping/permuted guards, forged full cover hash/count/order/parity, changed source and phase, noncanonical rationals, exhausted resources and forbidden capability promotions. Historical failure traces must be retained.

## Provenance and independent status

The new isolated model **reuses**, rather than alters, reviewed #303 single-guard/complete-cover model at Git blob `37c0271852e1468aa5ecfa9078d6f950841e4194`; it transitively pins the #298 point-jet blob `9fc344e045fa800fb24d30902a641e534a1e197b` and #296 interval source blob `2320f92efe4316d865a89f6d848737e2c000ca4d`. Frozen v54 121-case corpus blob `5841c331579489b25caef38cd412bdbf286f9134`, MC-002 **26-operation** domain blob `23de82f5240a72509f7afe4acd5948b65bc4ff13`, and current no-production authority blob `fa0233323a0804d8a5d3eb7cd892a274a6173fab` are checked read-only. This is a deterministic source-bound proof composition sharing earlier exact primitives, not an independent geometry kernel or human/native experiment.

## Reproduce, status and remaining gap

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_multi_nontransverse.py --contract --self-test
python3 tools/validate_machining_completeness.py
```

Landing requires literal-head focused and `mc1-static` CI, distinct exact-head technical review, expected-head protected merge, identical reviewed/synthetic/landed source trees, and merged-main checks. Research does **not** establish any historic V27/V41 nested child; irrational or implicit nontransverse roots, rational source-knot joins with differing one-sided multiplicities, arbitrary cross-owner coincidences and general PB-007-01 root completeness remain open. It does **not** change frozen v54 dispositions, task graph, capability registries, MC-B/MC-1 `NOT_ESTABLISHED`, `production_authorized=false`, or native topology/B-rep/conventional engineering STEP obligations. Preserve all 26 operations, source/provenance/phase, canonical operation journal, material/body/lineage, refusal and UNCERTIFIED semantics.
