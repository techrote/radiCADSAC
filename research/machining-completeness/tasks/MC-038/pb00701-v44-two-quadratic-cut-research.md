# MC-038 / PB-007-01 — frozen V44 two-quadratic cut research

**Status:** bounded deterministic-model candidate, 30 October 2026. **Owner:** [issue #100](https://github.com/techrote/radiCADSAC/issues/100); preregistered at [issue comment 6519543548](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6519543548). **Base:** qualified `main=1bf6cc382afdd3c901998d8a6dcdde1184384811` after [PR #317](https://github.com/techrote/radiCADSAC/pull/317). Final-head review, GitHub Actions, and merged-main acceptance are recorded in the issue ledger, not asserted by this prerelease memo.

## Source, hypothesis and strict scope

Frozen case `harvested:verify_pb00701_v44:ffaea08e30c9`, original-source SHA-256 `d3b3a90024ea283dfd96811b8fc2b66ceff621b3b48defc44c77f85557adbba2`, `t∈[0,1]`, phase turns `-1/8+t/16`. The original finite-harmonic source is

```text
F(t) = Σ_h [P_h(t) cos(2π h(-1/8+t/16)) + Q_h(t) sin(2π h(-1/8+t/16))]
P1 = -3/2+t+2t², Q1=-1/2-t+2t², P2=1/100000000, Q2=0.
```

PR #317 proved all *historical* four children over one field `Q(alpha)`, `alpha=sqrt(2)/2`, and preserved the verified original V41/V46 proof cut atlas. This incremental experiment introduces precisely one **synthetic** additional cut `beta=sqrt(3)/3` whose second field does not belong to the historical source's orientation roots. The question is whether the exact *fixed* compositum `K=Q(sqrt(2),sqrt(3))` can hold the original-source restrictions and rigorously decide the additional cut's physical nonzero sign, without taking the synthetic cut as an approved historical event, expanding the domain, or asserting a general compositum algorithm. This is one constructed example, not a general theorem.

### Exact arithmetic and independently falsifiable premises

Four rational basis coefficients `(a,b,c,d)` encode `a+b√2+c√3+d√6`. Arithmetic is exact; multiplication uses the two quadratic extensions. `√3∉Q(√2)`: if `(a+b√2)²=3` for rational a,b, then 2ab=0. For b=0, a²=3 contradicts rational squares; for a=0, b²=3/2 likewise contradicts rational squares. Thus `K` has degree four over Q, with unique basis coefficients. Nested conjugation gives `(A+B√3)^(-1)=(A-B√3)/(A²-3B²)`, with denominator nonzero for any nonzero element, while the quadratic inverse inside `Q(√2)` is exact. Its sign is determined by exact signs of `A,B,A²-3B²`, with no floating point or unbounded isolator refinement. The module verifies inverse multiplication roundtrips.

The real order `0<beta<alpha<1` is decided in the field, not by decimal approximations. For synthetic beta, the *original source*, not the synthetic child, is evaluated by the pinned rational trigonometric enclosure implementation at rational midpoints of an exact Sturm isolator for `3t²−1`. The original bounded global source derivative magnitude transports these intervals to beta by the mean-value theorem. Strict sign is required; unknown/zero within budget is nontruth (RESOURCE_REFUSAL). For the historical alpha cut, replay PR #317's separately certified original-source nonzero sign. The source global derivative lower bound `m>0` comes from the immutable pinned whole-source positive-derivative proof.

For exact ordered cuts `0,beta,alpha,1`, define 3 children `t=a_i+(b_i-a_i)u` with `0<=u<=1`. Verify exact strict width, `P_h(a+wu),Q_h(a+wu)`, inverse polynomial composition, all harmonic channels, exact phase shift/rate and child derivative `F_child'(u)>=m*w>0`. For this frozen case, independently source-certified signs are expected `[-,+,+,+]` and strictly monotone open-root counts `[1,0,0]`. No synthetic cut is a physical event; all root counts are source-derived, not atlas-authorized extensions.

### Decisive adversarial controls

The Python verifier tests exact quadratic identities, algebraic ordering, cancellation-sensitive signs, inverses of 39 nonzero field elements, noncanonical/float refusal, inverse Horner composition, bounded report canonical replay, cycle/oversize refusal, source/phase/pin mismatch, independently certified beta sign, tampered child width/phase/root count, false gate promotion, and forced sign-refinement exhaustion. A code artifact is not qualified until `--contract --self-test` and `mc1-static` pass against its **literal final PR head** and the source has been reviewed, followed by source-matched merged-main checks.

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v44_two_quadratic_cut_restriction.py --contract --self-test
python3 tools/validate_machining_completeness.py
```

#### Retained negative attempt

Before publication, the preliminary pure-field arithmetic control incorrectly asserted that `239/169 > √2`, producing one failed local test; the claim was wrong and corrected to `577/408 > √2` while preserving the same exact-sign falsification intent. The five preliminary pure-arithmetic tests passed after the correction. This was *not* a source-matched repository integration pass. Exact GitHub checks and any later failures are retained at issue #100.

## Authority, refusal and boundaries

This is **DETERMINISTIC_MODEL**, not native physical machining, kernel material evidence, B-rep construction, STEP, an independent engineering consumer, a general multiple-algebraic-field primitive, a general transcendental phase endpoint equality/zero/multiplicity oracle, or general nonmonotone root isolation. The extra beta is not in the historical V41/V44 source proof cut atlas and must not mutate old V41–V54 reports. Historical v54 remains `BLOCKED`; PB-007-01 and MC-038 remain OPEN; MC-B and MC-1 are `NOT_ESTABLISHED`. No domain operation is removed, no historical corpus, domain or authority source is modified. Production remains unauthorized. No native/paid campaign, OS kernel, machine/physical host or STEP was executed.

**Future work:** characterize whether the exact two-field arithmetic can be generalized to multiple independently isolated algebraic generators *without* circular use of a purported zero or ordering oracle, then independently prove required source-point/derivative and discontinuous-knot conditions. The synthetic experiment alone cannot close PB-007-01.