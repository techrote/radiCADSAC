# MC-038 / PB-007-01 — jet-guarded nontransverse whole-span root completeness

**Date:** 29 October 2026. **Status:** isolated, research-only candidate, evidence class **DETERMINISTIC_MODEL**. **Parent:** [MC-038 issue #100](https://github.com/techrote/radiCADSAC/issues/100). **Selection and preregistered falsifiers:** [#100 checkpoint #6509232134](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6509232134). **Original base:** \`ac894eeaf9f627c5bec51585cad01170ce9830d5\` (reviewed and merged #302). No new issue or native/paid campaign.

## Hypothesis and constructive certificate

For any **admitted exact original-source parameter span** in the finite rational-polynomial-modulated affine-phase trigonometric grammar, a *conditional* complete nontransverse-root result follows from three independently checked mathematical premises:

1. An exact rational interior point \`r\` is a root of order \`m >= 2\`, established by the previously landed cyclotomic-field derivative jet (#298, Git blob \`9fc344e045fa800fb24d30902a641e534a1e197b\`). An algebraic coefficient of a polynomial in transcendental π cannot falsely vanish; the first nonzero derivative receives a **strict** rational trig/π interval sign.
2. On a rational guard \`a < r < b\`, globally bound the \`(m+1)\`th derivative by rational number \`M_(m+1)\` using Leibniz, exact amplitude-polynomial derivatives, \`|sin|,|cos| <= 1\` and \`2π < 44/7\`. Enclose \`F^(m)(r)\` independently with rigorous rational trig/π evaluation. If widening by \`M_(m+1)*max(r-a,b-r)\` is strictly sign-definite, \`F^(m)\` keeps that sign over the WHOLE guard. Taylor's integral remainder and exact vanishing derivatives 0 through \`m-1\` imply \`sign F(s) = sign(F^(m)) * sign(s-r)^m\` for every \`s != r\` in the guard. Thus exactly one root of order m occurs in the guard; even m is tangency, odd m crossing.
3. For each complementary source interval \`[L,a]\` and \`[b,R]\`, exhaustively subdivide into closed rational dyadic cells. At every accepted cell with midpoint q and half-width d, rigorously enclose all values by \`F(q) +/- M_1*d\`, where \`M_1\` is an exact whole-span absolute first-derivative bound. A strictly signed enclosure proves the entire cell contains NO ROOT. Cells tile the complete complement without gap/overlap, and their signs agree with the Taylor guard and independently evaluated original source endpoints. These three regions form a finite exhaustive source-span cover with **exactly one nontransverse interior root**.

Neither a point jet, a handful of sample signs, a near-zero floating approximation nor a refinement timeout is enough for a whole-span result. Failed guard signs/outer subdivision/jet resources are typed **nontruth refusals**, never proof that a source has no other zeros. The method proves a **sufficient** bounded certificate for successful admitted spans; it is not a universal trigonometric root decision procedure.

## Executable original-source synthetic controls

The verifier supplies complete exact source records using the existing #296 finite-harmonic rational-polynomial span grammar and the original source coordinate \`source-time-t in [1/2,3/2]\` with phase turns \`0 + 1*s\`:

- **Nontrivial modulated double tangency**: \`F(s) = 1 - cos(2πs) + ((s-1)^2/8)*sin(2πs)\`. An exact cyclotomic jet proves root \`s=1\` has smooth multiplicity **2**, positive signs on both sides; a derivative-sign guard \`[15/16,17/16]\` and the complete outer root-free dyadic covers prove **one and only one** open root on the original span. Polynomial modulation is genuinely present, and the proof does not assume a global trigonometric factorization.
- **Modulated cubic stationary crossing**: \`F(s)=(s-1)^3*[1 + sin(2πs)/1024]\`. The exact jet proves multiplicity **3** at \`s=1\` with negative-to-positive crossing. The guard \`[7/8,9/8]\` and outer exhaustive root-free covers prove exactly one whole-span root.
- **Decisive negative counterexample**: \`F(s)=(s-1)^2(s-3/4)\` has a valid exact double-zero jet at \`s=1\` but ALSO a simple root \`s=3/4\` elsewhere in the source. Its outer sign-cell coverage **must refuse** rather than promote the point jet to complete one-root evidence.

A negated tangency, too-wide guard, exhausted finite budgets and incorrect source/report mutations are additional required controls.

## Source, independence and provenance boundaries

The new checker pins the unchanged #298 point-jet model Git blob \`9fc344e045fa800fb24d30902a641e534a1e197b\`, the #296 rigorous interval model \`2320f92efe4316d865a89f6d848737e2c000ca4d\`, frozen v54 source corpus blob \`5841c331579489b25caef38cd412bdbf286f9134\`, MC-002 26-operation domain blob \`23de82f5240a72509f7afe4acd5948b65bc4ff13\` and no-production authority blob \`fa0233323a0804d8a5d3eb7cd892a274a6173fab\`. Both existing methods share rational-trig/π interval primitives. This is a checked mathematical composition of proof methods, NOT an independent native geometry experiment or an independent human review.

A complete original source record is reconstructed with no hidden optional authority fields, exact canonical source/phase/harmonic polynomial data and SHA-256 binding; the verifier computes its own exact root/coverage certificate and recomputes the expected report when validating untrusted input. It emits rational source-root identity, exact order, sign cells, and hashes for complete dyadic cell witness sets. The full cell evidence is deterministically reproducible from the pinned checker.

This research exercises **new synthetic original-source spans** and explicitly does NOT admit any frozen V27/V41 or other v54 historical owner, retroactively alter the 121-case dispositions, or solve arbitrary open-root configurations, irrational-point tangencies, multiple separate nontransverse roots, zeros at source knots or implicit/algebraic cross-owner event comparison.

## Falsification and reproduction

The adversarial tests reject a valid double-jet incorrectly promoted despite a second root, inconclusive m-th derivative guard, insufficient dyadic resources, insufficient jet order, wrong multiplicity/parity/sign, forged outer coverage count/hash or source SHA, changed harmonic coefficients, phase, parameter, interval, unreviewed source fields, noncanonical/float/oversized input and any PB-007/MC-B/MC-1/native/B-rep/STEP/production promotion. Every uncertainty carries \`is_truth_value=false\`.

\`\`\`sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_jet_guarded_nontransverse.py --contract --self-test
\`\`\`

Landing requires the literal-head focused workflow, \`mc1-static\`, separately recorded technical review of the final head (AI-assisted through owner-account COMMENT if applicable, without inventing independent human status), identical reviewed/synthetic/landed trees, expected-head-protected merge, actual merged-main focused and static CI, and a durable #100 checkpoint.

**Explicit gate nonclaims:** PB-007-01 and issue #100 stay OPEN, MC-B/MC-1 \`NOT_ESTABLISHED\`, production authorized false. All 26 lathe/mill operation families, source/provenance/phase, canonical journal, material/body/lineage, refusal and UNCERTIFIED semantics, native topology/B-rep and conventional usable engineering STEP obligations remain unaffected. No v54 data, task graph, programme registry, gate or authority files are modified.
