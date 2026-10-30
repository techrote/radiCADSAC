# MC-038 / PB-007-01 — independent arithmetic challenge to frozen V44 biquadratic model

**Status:** bounded adversarial deterministic-model check, 30 October 2026. **Owner:** [issue #100](https://github.com/techrote/radiCADSAC/issues/100), preregistered at [comment 6520571947](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6520571947). **Qualified base:** main `9a6c34ed10cbdb2cbdf1e924608ccfe385f0e805`, [PR #318](https://github.com/techrote/radiCADSAC/pull/318). This memo is the test specification, not an assertion that proposed-head/merged-main CI passed. Final evidence belongs in the issue review ledger.

## Purpose and scope

[PR #318's fixed-field construction](pb00701-v44-two-quadratic-cut-research.md) uses nested quadratic conjugation to decide signs and inverses of elements of `K=Q(sqrt(2),sqrt(3))`, with rational basis `(1,sqrt(2),sqrt(3),sqrt(6))`. This check challenges exactly **that frozen arithmetic**, using mathematically different algorithms, against a source pin and an unchanged physical-root claim. It is not a new theorem for general algebraic fields, a second physical proof or independent native geometry evidence.

Original frozen source: `harvested:verify_pb00701_v44:ffaea08e30c9`; SHA-256 `d3b3a90024ea283dfd96811b8fc2b66ceff621b3b48defc44c77f85557adbba2`; original parameter `t in [0,1]`, phase turns `-1/8+t/16`. Owner source Git blob must be `46b89ccb449bb37f3c07b14d6de5e9fb92c50352` and its complete predecessor pin chain must replay unchanged. The synthetic cut `sqrt(3)/3` is **not** an orientation owner or physical event.

## Independent methods

1. **Strict sign intervals.** For each radical n=2,3,6 and bit precision b, use integer arithmetic `isqrt(n*2^(2b))` to obtain certified dyadic strict lower/upper bounds; combine the coefficient-signed intervals over all four terms. Refine only through a fixed explicit budget of 8,16,32,64,128,256,512 bits. Positive sign requires a strictly positive lower endpoint, negative requires a strictly negative upper endpoint; unresolved nonzero input is **RESOURCE_REFUSAL**, not zero. Exact zero is reported only for all four zero coefficients, using the separately reasoned field basis independence.

2. **Field independence.** `sqrt(3) not in Q(sqrt(2))`: rational x,y satisfying `(x+y sqrt(2))^2=3` require `2xy=0`; neither rational-square case `x^2=3` or `y^2=3/2` is possible. Thus the four basis elements are Q-linearly independent. This permits the only exact zero decision above without relying on the implementation's nested norm/sign method.

3. **Independent multiplication.** Represent the basis with two binary radical flags; multiply basis indices using XOR, multiplying by 2 and/or 3 for overlapping flags. Compare the resulting exact rational coefficient vector to the owner's separate nested polynomial product.

4. **Independent inverse.** Construct rational 4x4 multiplication matrix L_a from the independently derived product operation and solve `L_a*x=1` by exact rational Gaussian elimination. Demand a separate exact roundtrip and equality with the owner's conjugation inverse. This avoids the implementation's norm/inverse formula for expected truth.

## Falsifiers and coverage

The executable verifier exhaustively compares strict signs of all **625** coefficient quadruples in `[-2,2]^4`; samples their exact inverses, products, product-sign homomorphism and nontrivial fractional coefficients; challenges the near-cancellation values `-577+408 sqrt(2)` and `-49+20 sqrt(6)` with their negations; and verifies exact-zero, float/noncanonical, oversize, zero-inverse and exhausted-refinement refusal. Any arithmetic disagreement or source/pin drift fails the workflow. A nonzero field element is never classified as zero because its interval still overlaps zero.

Before repository integration, a local **pure-oracle** preflight syntax-compilation succeeded; 625 integer vectors all admitted strict interval signs, representative 4x4 exact inverses multiplied to unity, near cancellations returned negative, and a deliberately one-bit budget refused. This is not a source-matched full repository check and is not cited as CI acceptance. Final source-bound qualification requires literal-HEAD Actions and MC-1 static validation.

Run:

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701_v44_biquadratic_independent_check.py --contract --self-test
python3 tools/validate_machining_completeness.py
```

## Result boundaries and downstream impact

This checks a **fixed degree-four arithmetic representation**. It does not decide transcendental irrational-phase zero/equality/multiplicity, nonmonotone event isolation, arbitrary dependent square-root composita or higher-degree algebraic extensions; it does not independently reproduce the source's physical sign or positive derivative theorem. Even successful checks do not admit historical v54, close PB-007-01, satisfy MC-038/MC-B/MC-1, qualify STEP/native material, or authorize production. No historical V41–V54 evidence, MC-002 domain, task outcomes, task graph, proof registry or accepted authority changes are made. Native and paid work remain unpermitted.

**Next theorem questions:** derive a certifiable primitive-element/embedding and root-order algorithm for arbitrary represented algebraic inputs, identify exact equality and resource-refusal contracts, then qualify it independently on actual nonmonotone original-source constructors rather than promoting these synthetic controls.
