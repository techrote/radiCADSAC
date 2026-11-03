# PB-007-01: five original multiplier sources with complete ramp tails

## Status, purpose and scope

Date: 2026-11-03. Evidence class: **DETERMINISTIC_MODEL**. This is a finite source-mathematics research leaf under MC-038 / PB-007-01. Its measurement baseline is main `4d75edea493a3ee620d3bf64d81fa6e23356800e`; implementation was preregistered in [issue #100 comment 6591866803](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6591866803). Review and integration acceptance are separate from this candidate's mathematical replay.

Five original `tail100` corpus sources have complete finite zero sets, with respectively **3, 3, 3, 2 and 3 distinct simple roots**. Four have signs negative, positive, negative, positive across their maximal open sign cells. The V17 source has signs positive, negative, positive. Every original knot and exterior endpoint is nonzero.

The first two roots of each source are transferred from a qualified carrier lemma only after checking an exact identity against every original harmonic coefficient. The second span is proved directly from its held amplitudes and original affine ramp. No historical tail producer, rewritten surrogate source, saved success row or sampled sign supplies these conclusions.

The [v1 reconciliation](pb00701-post-v54-evidence-reconciliation.json) classifies eight original rows as `NO_REGISTERED_SOURCE_EVENT_OR_ORDER_WITNESS`. These five are in that cohort. Absence of a registered proof was an evidence-registration fact; it was never a proof that their mathematics is impossible. This leaf adds qualified-candidate source evidence without rewriting that historical classification. A separately reviewed reconciliation can consume it after acceptance.

The frozen 121-source census, 20 route refusals and 30 missing ordered-span premises remain unchanged. PB-007-01 remains open; PB-007-02/03/04 remain dependent or propagated. MC-B and MC-1 remain `NOT_ESTABLISHED`, the machining-operation denominator remains 26, and production authorization remains false. This work establishes no native geometry, STEP or universal proof-consumer capability.

## Owned artifacts and hypothesis

The leaf owns only these five files:

- [Executable proof model](pb00701_multiplier_tail_source_completion.py).
- [Contract verifier and falsifiers](verify_pb00701_multiplier_tail_source_completion.py).
- [Complete machine witness](pb00701-multiplier-tail-source-completion-witness.json).
- This research note.
- [One-job workflow](../../../../.github/workflows/mc1-pb00701-multiplier-tail-source-completion.yml).

**Hypothesis:** each selected original first span is a strictly nonvanishing multiplier of the same two-root carrier, and its original second span is strictly increasing with an exactly nonzero starting value. These premises determine the complete original closed-source event set and signs.

**Decisive falsifiers:** a coefficient identity fails; a factor can vanish; the multiplier sign is wrong; original phase or span coordinates differ; an amplitude is nonconstant on the tail; the derivative bound is not strictly positive; a claimed crossing lacks strict opposite signs; the original knot is zero or discontinuous; a source, dependency or witness loses its byte or typed-data binding. Any such failure refuses this proof rather than borrowing a stored result or changing the finite denominator.

No native or paid campaign ran. Exact arithmetic is bounded and uses the Python standard library.

## Exact original sources

All sources come from [the original finite-owner corpus](pb00701-finite-owner-corpus-v54.json), Git blob `5841c331579489b25caef38cd412bdbf286f9134`. Each row is an original `COMPOSITE_TAIL`, uses parameter identifier `source-time-t`, and has interval `[0,2]` and phase turns `t/4`. The original observation records certified component owners but the frozen whole-source disposition `BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE`.

| Label | Exact original case ID | Original provenance |
|---|---|---|
| V13 | `composite:PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC:tail100` | `verify_pb00701_v13` |
| V14 | `composite:PB00701_V14_EXACT_STRICT_DOMINANCE_MULTITERM_MULTIPLIER:tail100` | `verify_pb00701_v14` |
| V15 | `composite:PB00701_V15_EXACT_FINITE_STRICT_DOMINANCE_MULTIPLIER:tail100` | `verify_pb00701_v15` |
| V17 | `composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail100` | `verify_pb00701_v17` |
| V18 Laurent | `composite:PB00701_V18_EXACT_LAURENT_MODULE_FACTOR:tail100` | `verify_pb00701_v14` |

The V18 provenance is intentionally `verify_pb00701_v14`: that is the original row's value. Source identity is not inferred from its informal family label.

Canonical source and whole-row SHA-256 bindings are independently literal-pinned:

| Label | Source specification SHA-256 | Original whole-row SHA-256 |
|---|---|---|
| V13 | `a7131bea021c5c71d0da2682cd6d4c1a982e8c86196c818ad3f69a926afda2e5` | `094b31ab55141488e39589ab6e0deda02b21066f06ba8568110609a23cd0a003` |
| V14 | `bd10ad1d9503335b2d7f745c09805b82a421b8db7beea67329cf33d0c9d78ff2` | `1940ec5f6aafb641a25fcda3f8941ff7dd9f2afc2bf13056da6920159c3f0e18` |
| V15 | `8e41009417dd65f9a47a04b492dd9a91b88a7682f12f45305ce64ac38dffd7b7` | `3954e79fceefbcd6e4b5932197f0314dbd4b90891b8fbad8410f9572f746725d` |
| V17 | `e85d997c9f4d828b1b748c964b375c21e4acef1b1e9046e074b1f7e29011d08f` | `41e86bc30392515873fb55bdd844d154236a81426fd3639c3bd5491dad30f05a` |
| V18 Laurent | `ed61c9b827417327b9dda32ec0469ba5f0eab9622fb531d4b1bc959a312aa4a1` | `7c1304de8afc41ba322fb653f20a1f8b6c3e0ea27af8a7864e44058d6b4d60d1` |

The executable and witness carry the authoritative exact strings and reject drift before mathematical parsing. The whole-row digest also binds origin, original component observations and historical disposition.

## Reconstruct the original splines before factoring

Write the original source as

\[
F(t)=\sum_h C_h(t)\cos(h\theta(t))+\sum_h S_h(t)\sin(h\theta(t)),
\qquad \theta(t)=\pi t/2.
\]

Every selected amplitude is degree zero or one on the fully clamped original partition `[0,1,2]`. A degree-zero pair of controls gives the two constant pieces. Degree-one controls `(c0,c1,c2,c3)`, with knot vector `(0,0,1,1,2,2)`, give global-parameter powers

\[
p_0(t)=c_0+(c_1-c_0)t,\qquad
p_1(t)=(2c_2-c_3)+(c_3-c_2)t.
\]

The latter formula retains original `t`; it does not accidentally evaluate the second piece in `t-1`. Every channel is checked for equality at the original knot, `p0(1)=p1(1)`. All selected nonzero-harmonic second pieces have zero slope. The zero harmonic is zero on the prefix and `100(t-1)` on the tail. The report records all reconstructed coefficients and all channel-level knot equalities.

The checker requires the exact grammar, phase offset and rate, source endpoints, knot multiplicities, control count, permitted harmonics and selected harmonic set. Boolean degree aliases, renamed harmonics, dropped zero channels and discontinuous controls are refused.

## Qualified carrier and the limits of its authority

The qualified provider is [component-prefix composition](pb00701_component_prefix_composition.py), Git blob `530e552bb41c020456fdf0f17506cb18577896f3`, accepted with the same-buffer custody correction at baseline main `4d75edea493a3ee620d3bf64d81fa6e23356800e` ([acceptance record](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6591866576)). This leaf consumes **only** its pure `carrier_prefix_proof()` entrypoint.

That helper proves, on original interval `[0,1]`,

\[
R(t)=(t-1/3)\cos(\pi t/2)+(2/3-t)\sin(\pi t/2).
\]

It supplies two simple roots with strict brackets `(1/6,1/4)` and `(3/4,5/6)`, signs `-1,+1,-1`, endpoint values `-1/3`, and proof cuts `1/3,2/3`. Its canonical receipt SHA-256 is `d9c019f6104618d096d9b87d13bbdf700b958cd197546b6f64db904c8129bbf4`.

For context, the qualified argument uses reflection `R(1-t)=R(t)`, a strictly positive derivative on `[0,1/3]`, positivity on `[1/3,2/3]`, and exact half-angle inequalities at `1/6` and `1/4`. Reflection supplies the second simple root and its derivative orientation. The cuts delimit proof regions; they are not zeros or physical events.

The helper carries no original source binding. The consumer therefore independently reconstructs all selected source coefficients and proves `F=M R` before transferring anything. The provider's source wrapper, older factor identities, historical tail producers and saved whole-source report are not called. A test runs the carrier from a temporary directory containing only its source file and cache counterexample, with no tail producers or saved reports present.

## Original factor identities and strict nonvanishing

Set `a=t-1/3`, `b=2/3-t`, `c=cos(theta)`. The implementation constructs exact Chebyshev polynomials using `T0=1`, `T1=c`, `Tn=2c T(n-1)-T(n-2)` and `U0=1`, `U1=2c`, `Un=2c U(n-1)-U(n-2)`. Thus `cos(h theta)=Th(c)` and `sin(h theta)=sin(theta) U(h-1)(c)`.

For each power `t^0` and `t^1`, the original cosine channels are expanded as a polynomial in `c`; the original sine channels are expanded as the coefficient of `sin(theta)`. All coefficients must agree exactly with the proposed product. This is stronger than agreeing at selected points. The verifier additionally reconstructs the same source coefficients through independent product-to-sum formulas, without calling the model's Chebyshev helper.

| Label | Multiplier `M(theta)` derived from original controls | Strict lower bound for `abs(M)` | Sign |
|---|---|---:|---:|
| V13 | `2 + cos(2 theta)` | `1` | `+1` |
| V14 | `2 - (1/2) cos(2 theta) + cos(4 theta)` | `1/2` | `+1` |
| V15 | `4 + (1/2) cos(2 theta) - (1/4) cos(4 theta) + cos(6 theta)` | `9/4` | `+1` |
| V17 | `-2 + sin(2 theta)` | `1` | `-1` |
| V18 Laurent | `2 + cos(2 theta) + cos(4 theta)` | `7/8` | `+1` |

“Strict lower bound” in this table means a positive bound proving strict nonvanishing: `abs(M)` is greater than or equal to the displayed positive number. Equality with that bound is permitted.

For V13/V14/V15, the constant exceeds the sum of absolute nonconstant cosine coefficients. For V17, `-3 <= M <= -1`. Its sign reverses the carrier's three signs but does not change its zero coordinates or multiplicities.

For V18 Laurent, the ordinary absolute-amplitude bound gives zero and cannot prove nonvanishing. Instead, with `z=cos(2 theta)`,

\[
M=2z^2+z+1=2(z+1/4)^2+7/8>0.
\]

The implementation recomputes and checks that exact square identity and its positive remainder. It does not relabel an inconclusive zero lower bound as success.

For the even cosine multipliers, let `P(c)=M(theta)`. The two exact identities are `C(c)=a c P(c)` and `S(c)=b P(c)`. For a multiplier `m+d sin(2 theta)`, use `sin(2 theta)=2 sin(theta)c` and `sin(theta)^2=1-c^2`:

\[
C(c)=(ma+2db)c-2db c^3,\qquad
S(c)=mb+2da c^2.
\]

These identities account for every original harmonic, including channels whose exact coefficient cancels to zero. At a carrier zero, `(MR)'=M R'`; both factors on the right are nonzero. The transferred roots are therefore simple, with derivative signs determined by the multiplier sign and the qualified carrier orientation.

### Recorded negative finding: the V14 coefficient sign

The actual V14 factor has **minus** `(1/2) cos(2 theta)`. The corresponding plus-sign candidate also has a positive dominance margin, so checking only nonvanishing would miss the error. It fails the independent original coefficient identity. The correct original knot value is `-7/6`, not `-5/6`. A focused regression retains this counterexample.

The historical V41/V13 fixed-source order result is also unsuitable as a substitute: its sine harmonic is 4, whereas this original prefix requires harmonic 3. The source reconstruction and a harmonic-renaming falsifier prevent that cross-source reuse.

## Complete original tail proofs

On `[1,2]`, each original source has the exact form

\[
F(t)=100(t-1)+\sum_{h>0} C_h\cos(h\pi t/2)
                  +\sum_{h>0} S_h\sin(h\pi t/2),
\]

where the coefficients are held original controls. Define

\[
A=\sum_{h>0}(|C_h|+|S_h|),\qquad
W=\sum_{h>0}h(|C_h|+|S_h|).
\]

The elementary bounds `abs(sin)<=1`, `abs(cos)<=1` give

\[
F'(t)\ge100-(\pi/2)W\ge100-(11/7)W>0,
\qquad
F(11/10)\ge10-A.
\]

For a self-contained strict phase bound, polynomial division and integration give

\[
0<\int_0^1\frac{x^4(1-x)^4}{1+x^2}\,dx
 =\int_0^1\left(x^6-4x^5+5x^4-4x^2+4-\frac4{1+x^2}\right)dx
 =22/7-\pi.
\]

Thus `pi/2 < 11/7`. The reported derivative bound is a positive lower bound; no floating approximation supplies it.

| Label | `A` | `W` | Positive bound `100-(11/7)W` | Bound `F(11/10)>=10-A` | Exact `F(1)` | Exact `F(2)` | Tail roots |
|---|---:|---:|---:|---:|---:|---:|---:|
| V13 | `8/3` | `11/3` | `1979/21` | `22/3` | `-1/3` | `98` | 1 |
| V14 | `17/6` | `17/3` | `1913/21` | `43/6` | `-7/6` | `295/3` | 1 |
| V15 | `21/4` | `21/2` | `167/2` | `19/4` | `-3/4` | `193/2` | 1 |
| V17 | `3` | `4` | `656/7` | `7` | `2/3` | `304/3` | 0 |
| V18 Laurent | `10/3` | `20/3` | `1880/21` | `20/3` | `-2/3` | `292/3` | 1 |

For the four negative knot values, continuity and the strictly positive value at `11/10` prove existence of a tail zero in `(1,11/10)`. Strict increase proves uniqueness on the entire original tail; the positive derivative proves simplicity. For V17, the positive starting value and strict increase exclude every tail zero. Exact endpoint values use the cardinal values of sine and cosine at integer multiples of `pi/2`, never numerical sampling.

The derivative check is substantive: setting the original ramp slope to zero makes the V13 tail derivative at the knot equal to `-pi/3`, so unconditional monotonicity would be false. The tests also set the ramp slope exactly to `(11/7)W`; the resulting zero certified lower bound must refuse even if some stronger proof might exist. The conditional helper does not claim completeness outside its sufficient inequalities.

## Closed-source event order and knot composition

The ordered prefix brackets are disjoint and lie before the original knot. Any tail bracket begins at 1 and lies after them. The source-identified implicit zero in each strict bracket is the event coordinate; neither its rational bracket endpoints nor the proof cuts are emitted as event positions.

Each event carries the original source digest, parameter identifier, original piece index, strict bracket, physical multiplicity 1, derivative orientation, and left/right signs. The original knot is channel-continuous and exactly nonzero, so it introduces no additional event and the adjoining equal-sign cells merge. The two exterior endpoints are explicitly checked and nonzero.

| Label | `F(0)` | `F(1)` | `F(2)` | Complete ordered root brackets | Maximal open signs |
|---|---:|---:|---:|---|---|
| V13 | `-1` | `-1/3` | `98` | `(1/6,1/4)`, `(3/4,5/6)`, `(1,11/10)` | `-,+,-,+` |
| V14 | `-5/6` | `-7/6` | `295/3` | `(1/6,1/4)`, `(3/4,5/6)`, `(1,11/10)` | `-,+,-,+` |
| V15 | `-7/4` | `-3/4` | `193/2` | `(1/6,1/4)`, `(3/4,5/6)`, `(1,11/10)` | `-,+,-,+` |
| V17 | `2/3` | `2/3` | `304/3` | `(1/6,1/4)`, `(3/4,5/6)` | `+,-,+` |
| V18 Laurent | `-4/3` | `-2/3` | `292/3` | `(1/6,1/4)`, `(3/4,5/6)`, `(1,11/10)` | `-,+,-,+` |

This proves 14 simple physical roots, five nonzero original knots and ten nonzero original exterior endpoints. A private composition helper accepts only the fresh prefix/tail views generated in the source proof. It checks matching source identity, phase and parameter; full original piece intervals; exact integer counts and signs; strict bracket order; complete-span flags; original channel continuity; and agreement with the exact knot and exterior values. Public report validation regenerates all proof views before comparing them.

## Public replay contract and bounded inputs

`expected_report()` is the complete consumer entrypoint. It audits the pinned original corpus and historical census, selects only the five exact whole rows, replays the qualified carrier, independently derives each factor and tail proof, composes original events and regenerates the entire witness.

`validate_report(candidate)` first bounds and canonicalizes exact typed candidate data, then compares it with fresh `expected_report()` bytes. A changed count, event, factor bound, source row, gate or dependency map cannot be accepted merely because Python considers `True == 1` or `False == 0`: canonical typed JSON bytes differ.

`source_proof(row)` accepts only one of the five exact original rows after source and whole-row digest checks. `prove_prefix`, `prove_tail` and the factor helpers are conditional mathematical primitives, not claims that a new source belongs to the frozen corpus. A regression doubles all nonzero-harmonic V13 controls and proves the valid doubled factor identity and tail; the frozen-row API correctly refuses that different source.

JSON/file input is limited to 1 MiB, 65,536 nodes, depth 32, 1,024 elements per container and strings of at most 8,192 characters. Cycles, custom scalar types, floats, duplicate keys, non-finite JSON constants and oversized integers refuse. Exact rationals must have canonical ASCII spellings, at most 78 decimal digits per numerator/denominator and at most 256 bits before constructing `Fraction`; negative zero, unreduced fractions, denominator 1 spellings and Unicode digits refuse. Internal polynomial vectors are limited to 16 coefficients and 4,096-bit exact values before rational reconstruction. Resource refusal is not evidence of either existence or absence of roots.

## Executed-byte and JSON custody

The verifier reads at most 1 MiB of its model source, checks its literal Git blob and directly compiles that same byte buffer into a fresh module. Each consumed project module is handled similarly. No project module is accepted from `sys.modules`, `importlib` source-loader caches or a path that is reopened after checking. A matching-timestamp, matching-size stale `.pyc` counterexample is constructed in the tests and demonstrated to alter ordinary import behavior; the actual carrier loader still executes the pinned source and returns the qualified receipt.

The provider and historical auditor are the only two consumed modules. Their required import names are restricted to an explicit standard-library allowlist. A local `sys` facade has its own `path` list, so the carrier module's existing path setup does not mutate process-global import search paths. The pure carrier call reads no other repository files. The historical auditor is called as `audit(corpus, inventory, coverage)` with already bounded, same-buffer-decoded pinned JSON; its legacy path-loading entrypoint is not used.

Every consumed JSON file is read into a bounded buffer, hashed and decoded from that identical buffer. A regression replaces the path after checking and confirms the checked content is the content decoded. The next call detects the changed path. Parallel code replacement and preloaded-module regressions cover the same distinction for execution.

### Complete consumed dependency closure

The following nine dependencies are literal-pinned in the model and witness. The workflow triggers on these nine paths plus all five owned files, on pull requests and pushes to main. There is no broad `MC-038/**` trigger.

| Path relative to repository root | Git blob | Consumed role |
|---|---|---|
| `research/machining-completeness/tasks/MC-038/pb00701-finite-owner-corpus-v54.json` | `5841c331579489b25caef38cd412bdbf286f9134` | Original 121 rows and exact selected source controls |
| `research/machining-completeness/tasks/MC-038/pb00701-finite-owner-inventory-v54.json` | `8649c20ab77e199f9c3fa351b8b6742218f27abb` | Frozen inventory audit |
| `research/machining-completeness/tasks/MC-038/pb00701-finite-owner-coverage-v54.json` | `600ba29786f50397f29fd435fc5e2c57076088f9` | Frozen historical dispositions |
| `research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_frontier.py` | `12c6efeb667a954ffc5a7e27849ae815d466580a` | Pure historical audit called with pinned decoded inputs |
| `research/machining-completeness/tasks/MC-038/pb00701-post-v54-evidence-reconciliation.json` | `9f62dd6edc37206317eec054b2969bade02d7728` | Historical eight-row unregistered cohort only |
| `research/machining-completeness/tasks/MC-038/pb00701_component_prefix_composition.py` | `530e552bb41c020456fdf0f17506cb18577896f3` | Pure qualified carrier lemma only |
| `research/machining-completeness/tasks/MC-002/domain-contract-v1.json` | `23de82f5240a72509f7afe4acd5948b65bc4ff13` | Unchanged 26 required machining operations |
| `research/machining-completeness/programme-v1.json` | `dee7045a1790b2870744df8ae7693429bd1d81a6` | Open programme and MC-B state |
| `handoffs/current-authority.json` | `fa0233323a0804d8a5d3eb7cd892a274a6173fab` | Unchanged MC-1 authority and production prohibition |

Older tail producers, the carrier's saved full-source report, and the v1 reconciliation producer code are not consumed transitively by these entrypoints. Their claims are not accepted through this closure. Any later expansion of the called provider path requires a newly reviewed dependency closure.

## Verification and retained alternatives

Run from repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/machining-completeness/tasks/MC-038/verify_pb00701_multiplier_tail_source_completion.py --contract --self-test
python3 tools/validate_repo.py
python3 tools/validate_machining_completeness.py --self-test
```

The focused verifier has **32 tests**. Alongside full fresh source replay, they challenge independent product-to-sum identities; V14's wrong sign; every original harmonic; V18's inconclusive L1 bound; vanishing and sign-uncertain multipliers; forged factor bounds; valid nonfrozen identities; V17 sign reversal; lost or non-strict tail derivatives; inaccurate crossing bounds; nonconstant tail amplitudes; exact-zero and discontinuous knots; phase/source geometry; incomplete or cross-source views; reordered events and proof-cut additions; Boolean/integer aliases; actual replay refusal; source drift before mathematical construction; lexical and resource guards; duplicate JSON; real stale caches; preloads; changed paths; and unchecked dependencies.

The single-job hosted workflow records and checks the literal pull-request head (or main push SHA) with Python 3.12. Hosted CI and independent exact-byte review remain required before this candidate is qualified.

Alternatives considered and retained as negative evidence:

- Reusing a source label or a nonvanishing factor without reconstructing original harmonics fails the V14 wrong-sign and historical harmonic-4 counterexamples.
- A cosine L1 bound cannot settle the Laurent factor; its zero result is preserved, and the exact positive square supplies a different valid proof.
- Transferring a carrier root through a factor that may vanish loses multiplicity and completeness. Such candidates refuse.
- A positive endpoint alone does not establish a unique tail crossing. The strict derivative proof and opposite signs are both required.
- Parsing or importing a file again after checking its hash loses the connection between checked and consumed bytes. The loaders retain and consume the checked buffer.
- Running old historical owners would add code dependencies without proving the missing original whole-source order premise. This finite source proof supplies that premise directly.

## Consequences and remaining work

For MSAC, this leaf supplies a finite example of complete original-source event order, signs and nonzero knots without promoting a family label or an incomplete child proof into coverage. For OpenSimachinist, it illustrates a bounded source-bound certificate consumer with explicit factor assumptions, physical events and exact failure states. Neither implication is an implemented production interface.

The next integration action is independent review of the exact five files, literal-head hosted checks, guarded merge and main-push verification. A later separately preregistered reconciliation may register these five complete source witnesses while preserving all historical dispositions and other unresolved obligations. This leaf does not edit the old evidence registry, current implementation-state navigation or any capability gate.
