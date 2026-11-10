# A1 — Conditional termination of exact signed H0/H1/H2 event partition

**10 November 2026 · speculative RESEARCH · Draft/HOLD · A3 review required.**

Accepted main checked: 48222d6c40b15ad42cc36d56e6d25f3b284e7fc9. Previous existing A1 Draft #470: 858d3d9bc1f93af34054d64df306a6e9aafb3c0f. Source lease: [#324 comment 6755055364](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6755055364). This report makes no MC-038 gate, native B-spline, engineering STEP or source-authentication claim.

## One theorem seam: conditional completeness rather than bounded success

For finitely many nondegenerate rational closed time intervals, joined end to end, define each analytic piece by

\[
F_i(t)=H_{0,i}(t)+\sum_{h=1}^2\left[C_{h,i}(t)\cos(h\pi(a+bt))+S_{h,i}(t)\sin(h\pi(a+bt))\right],
\]

where every amplitude is a rational polynomial, a,b are rational, and each of the five coefficient values matches exactly at a common piece knot. A real C0 derivative discontinuity may occur; no differentiability is required across the knot.

**Promise:** every zero of each piece on its closed physical interval is a *simple strict-interior* zero; all exterior endpoints and knots are nonzero. This promise is NOT automatically decidable. A strictly zero-free piece also satisfies it.

**Theorem (conditional, independent proof review pending).** There exists a finite rational tiling of every piece whose independently checkable leaves prove either a strict signed zero-free cell or exactly one simple crossing with direction and strict rational root bracket. An *ideal fair search* that increases rational grid resolution, shifts of grid pivots, and outward-enclosure precision will eventually find that tiling. Neither a uniform complexity bound nor an oracle deciding whether the promise holds follows.

**Preregistered falsifiers:** any missed crossing in a successful tiling, duplicate physical event, wrong direction or positive cell, invalid Taylor/Machin bounds, a source/knot discontinuity admitted as continuous, a forged source receipt accepted, or a promised source with no certifiable tiling under fair unbounded search. Tangency and continua are mandatory typed-refusal controls, not permitted to become empty event sets.

## Proof outline and the actual certificate rule

1. Each rational-polynomial/trigonometric piece extends to an entire function. Under the simple-zero promise, its zeros in a compact interval are finite. Infinite zeros would have an accumulation point and force analytic identity, contradicting the simple-zero premise.
2. Each root has nonzero first derivative, hence a small neighborhood of strictly constant derivative sign. Away from finitely many disjoint root neighborhoods, compactness and nonvanishing give a strictly positive minimum of the absolute function. The nonzero piece endpoints and knots also have root-free neighborhoods.
3. For a fixed uniform grid of n rational intervals, shift all internal pivots by a rational fraction j/(M+1) of one grid spacing. Each root excludes at most one such shift: no two internal pivots with the *same* shift coincide with a single root. For M strictly greater than the total number of roots, some j avoids all roots. This also applies to rational zero times without claiming they have been algebraically evaluated by the checker.
4. Shrink the grid diameter below the separation and local monotonicity scales. On cells away from roots, strict function sign is certifiable. On cells containing a simple root, strict derivative sign and opposing nonzero endpoint signs eventually certify one crossing; near-root cells with equal endpoint signs may instead be certified zero-free by strict monotonicity. No cell spans two events once the grid is sufficiently fine.
5. Rational interval Horner enclosures, intersected with an exact centered mean-value enclosure, converge for polynomial amplitudes. Rational Machin bounds for pi plus sin/cos Taylor remainder bounds converge uniformly for rational phase points; the additional phase-Lipschitz radius tends to zero with cell width. The same applies to the exact first derivative. Therefore each strictly valid sign or monotonicity claim is eventually detected at finite precision. The intermediate value theorem and strict derivative sign prove existence, uniqueness, crossing direction and root order one on each crossing cell.
6. The verifier reconstructs the complete ordered rational tiling, source SHA, every strict cell sign, endpoint sign and derivative enclosure. It rejects gaps, mismatched cells and missing or changed events.

This is a compactness/interval-certification theorem under a *promise*, not a general bounded Continuous Skolem solution. The proof uses established facts, not a new theorem of transcendence.

**Vital finite-versus-ideal distinction.** The uploaded executable uses a finite maximum mesh level, number of shifts, Taylor precision and rational input sizes; it returns a typed refusal if these are insufficient. A mathematically fair search must increase ALL budgets, *including shift count*; a fixed set of eight candidate shifts cannot establish universal termination. The theorem establishes only eventual existence under the promise, and the bounded tool demonstrates/replays selected witnesses. It cannot decide the existence of arbitrary tangencies or zero continua.

## Source grammar, executable resource limits, authority

The strict source parser takes a canonical JSON-compatible dict with rational strings in numerator/denominator form, shared phase a+b*t measured in **pi units**, 1–3 contiguous pieces with exactly agreeing coefficient values at seams, H0/C1/S1/C2/S2 polynomial vectors of degree at most 3, rational numerators and denominators at most 96 bits, and intervals inside [-16,16]. The mathematical theorem itself does not require these code budgets.

A source-specific SHA-256 is reconstructed on every verification, including a defense against post-construction frozen-dataclass mutation. This does **not** authenticate an actual MC-038 producer: an attacker controlling a replacement source and replacement trusted SHA can still create a self-consistent model receipt. B1 producer-pin custody is required before external integration. Coefficient continuity is stronger than necessary for physical continuity; it does not establish real clamped B-spline control/knot provenance or sided zero germs. Accepted MC-038/A2 phases are frequently expressed in **2pi units**, unlike this A1 pi-unit source grammar: copying offset/rate without an explicit factor-of-two adapter is unsound.

The leaf types are signed EMPTY and signed CROSS. Missing signs, tangent touches, knot zeros, invalid sources and exhausted budgets return NONTRUTH. There is no false "COMPLETE" response on those rejected cases.

## Tests and observed bounded results

From the research subtree run: python3 -m unittest -v test_simple_promise.py

**11/11 tests passed locally** in the bounded Python deterministic-model environment. The exact *published* source and tests were prepared from local files whose Git blob identities are:
- simple_promise.py — 08098ae007d401616a3e131a597ebdf7a7e05039
- test_simple_promise.py — 8b809d600fd4dd21474705ad9f70b8ed87afa9e1

These are not yet dedicated hosted literal-PR-head execution, native geometry qualification, or independent A3 review. Source-matched GitHub readback and exact-head hosted checks are separate from authors' local run.

| Independent input | Cells | Certified crosses | Mesh level |
|---|---:|---:|---:|
| 3 + sin(pi*t) + cos(2pi*t), [0,2], nonmonotone zero-free | 9 | 0 | 3 |
| 1/2 + sin(pi*t), [0,2] | 9 | 2 | 3 |
| (t-1/2)(t-17/32), separated by 1/32 | 65 | 2 | 6 |
| One crossing 31/64 beside genuine C0 knot at 1/2 | 4 | 1 | 0 |
| cos(-2pi*t), [0,1], negative phase slope | 5 | 2 | 2 |

All positive cases are separately replayed by the deterministic verifier. The initial interval-Horner implementation **failed** the close-pair case at level 8 because dependency inflation could not prove the small negative trough; the corrected exact centered mean-value intersection successfully certified both roots at level 6. Keep this negative finding: more partitions alone did not overcome poor polynomial enclosures at the tested budget. A deliberately low-budget rerun of the same close pair refuses, as do (t-1/2)^2 and the identity-zero continuum. Altered cell sign, altered source SHA, mutated frozen source, and physically discontinuous seam all reject. No arbitrary source-independent numerical sampling is admitted as proof.

**Cost/limitations:** Maximum tested work is bounded by number of pieces × (2^level + 1) cells × candidate grid shifts × precision candidates, plus successful verifier replay. Numerator/denominator widths grow sharply for Taylor and Machin bounds. No input-bit polynomial-time claim, native throughput claim or hard guaranteed resource bound for the ideal fair procedure is made.

## Prior art, source comparison and one next falsifier

[PR #453](https://github.com/techrote/radiCADSAC/pull/453) already builds bounded certified H0/H1/H2 signed interval partitions with exact rational bounds, simple roots, and typed tangency/knot refusals. It does not establish universal termination under unrestricted inputs. **This contribution is the conditional fair-grid termination argument, explicit collision-avoiding rational shifts, and bounded independent controls, NOT a reimplementation of #453's authenticated V44 source importer**. Prior A1 work in [#470](https://github.com/techrote/radiCADSAC/pull/470) provides specified algebraic-time equality and a restricted square-lift transcendental tangency; it is not an exhaustive isolator for arbitrary simply rooted H2 sources. [#462](https://github.com/techrote/radiCADSAC/pull/462) covers spline/time transformations, A2 #471 owns local jets/germs, and B1 #473 owns source-bound certificate algebra.

Established rigorous numerical root isolation is prior art: [Kavvadias & Vrahatis, SIAM J. Sci. Comput. 1996](https://doi.org/10.1137/S1064827594265666). [Chonev, Ouaknine & Worrell, ICALP 2016](https://arxiv.org/abs/1506.00695) identify open general bounded Continuous Skolem zero problems; this work does not resolve them.

**Highest-value next falsifier for A3:** independently inspect exact published source, rerun all tests, and challenge the *unbounded-shift* part of the proof with many rational roots deliberately aligned at all fixed shift candidates; verify no fixed 8-shift or 16-precision version is advertised as promise-terminating. Attack the negative-phase derivative bounds, centering enclosure intersection, rational-pivot collision, and source-hash custody. **B1 request:** assess typed authoritative producer-to-certificate binding, including phase scale, without assuming SHA possession supplies producer authority.

## Final research disposition

**GO for conditional lemma and source-shaped checker review; HOLD for generic physical event isolation and any gate.** All code/report changes are additive and exclusively within A1's isolated research subtree. No author branch other than existing A1 #470 was written, and no MC-038, A2/A3/B1, authority, production, native/STEP, workflow or shared registry source changed. Newly completed frozen-original cases: **0**. Historical census **121 originals / 20 route refusals / 30 missing premises / 50 completed source-specific witnesses**; **26** machining operations unchanged. PB/PO global obligations OPEN. **MC-B and MC-1 NOT_ESTABLISHED; production_authorized=false**. No merge or Ready promotion.
