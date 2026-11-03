# MC-038: bounded refinement of selected implicit original-source zeros

Status: implemented finite deterministic-model research, 2026-11-03. This record captures local verification; this leaf's independent review, hosted CI and integration acceptance are recorded separately under MC-038. The qualified parent consumer is accepted. Historical source providers and their dispositions remain unchanged.

## Purpose and result

The [selected implicit-root refiner](pb00701_selected_implicit_root_refinement.py) restricts the strict rational isolators of already proved unique simple zeros of the original source functions. Its public operation accepts only a requested step count from zero through twelve. It always replays the qualified [fifty-source zero-set consumer](pb00701_fifty_source_zero_set_consumer.py), derives the selected source/event population from that fresh result, and evaluates the original rational B-spline channels and original global phase.

The default [saved report](pb00701-selected-implicit-root-refinement.json) completes twelve bisections for all 69 selected implicit events across 28 original sources. It contains 828 exact halving steps and 966 logical strict point decisions. Every final bracket has exactly one 4,096th of its initial width. The final widths range from `1/4096000` to `1/8192`; widths alone are not acceptance evidence. Each event retains its original source identity, original parameter, original source span, parent event identity and inherited unique-simple-root proof.

The complete parent baseline is retained unchanged: fifty sources, comprising 49 finite zero sets and one separately typed continuum; 81 isolated physical zeros, comprising twelve rational and 69 implicit events; and 128 maximal connected nonzero cells. Refinement neither replaces that census with 69 nor changes the rational events, continuum type, source knots or physical sign-cell partition.

## Authority and exact inputs

This separate five-file leaf was preregistered in [MC-038 issue #100, comment 6592841484](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6592841484), after [consumer acceptance comment 6592839222](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6592839222). Its qualified base is `828df02d3d61b57bd46b0c4a796ce58685d9c987`. The parent consumer remains source-specific deterministic evidence; no generic owner route is repaired by calling it.

| Direct input | Exact Git blob | Role |
|---|---|---|
| [Qualified consumer code](pb00701_fifty_source_zero_set_consumer.py) | `d5eef89ab168a2acc2588f13a6d87ab88b998d40` | Actual fresh complete parent replay |
| [Qualified consumer report](pb00701-fifty-source-zero-set-consumer.json) | `8213026ed2a5205d2cfff44e45c26e89deab4ee9` | Canonical equality check after actual replay |
| [Original frozen corpus](pb00701-finite-owner-corpus-v54.json) | `5841c331579489b25caef38cd412bdbf286f9134` | Independently retained original source rows |
| [Exact trigonometric interval helper](pb00701_transverse_trig_interval.py) | `2320f92efe4316d865a89f6d848737e2c000ca4d` | Rational pi/Taylor point enclosures |

The canonical parent report SHA-256 is `9703c8222f04ce231613bdd4585724f08401a83c2618ab01a362ba71cd57168f`. The model also pins the exact byte count and raw SHA-256 of each direct input. The complete consumed closure contains 101 paths: the parent's 99 dependencies plus the qualified parent model and report. No temporary feasibility map, saved provisional trace or unqualified source inventory is an implementation dependency.

Before any selected-source numerical parsing, the refiner compares its separately retained corpus index with the actual parent index, and matches original-row/source SHA-256, source parameter, phase law, domain, provenance, event ID and ordinal, original piece, initial bracket, simple order and uniqueness-evidence owner. The saved parent report cannot replace its actual proof replay.

## Derived selected population

The following counts are derived from the fresh parent event descriptors. Sources that contribute only rational roots, no roots, or the continuum remain in the parent baseline without being passed to the implicit refiner.

| Parent producer family | Selected original sources | Selected implicit events |
|---|---:|---:|
| `bernstein_sectors` | 2 | 2 |
| `component_prefix` | 5 | 12 |
| `five` | 1 | 1 |
| `multiplier_tails` | 5 | 14 |
| `ordered_children` | 7 | 8 |
| `ratio_prefix` | 4 | 25 |
| `trig_fixed` | 3 | 6 |
| `v44` | 1 | 1 |
| Total | 28 | 69 |

These sources contain 120 coefficient channels: 77 cosine and 43 sine channels, with degrees zero, one, two, three, four, six and seven. The maximum is sixteen controls and twenty-four knots per spline. The implementation therefore evaluates original B-splines directly; it does not lower them through the old transverse helper's cubic-only `Span` grammar.

Five original source-parameter identities are preserved: `pb00701-v44-algebraic-orientation`, `preserved-carrier`, `source-time-t`, `v53-simple-repeated-join` and `v53-strict-48`. The phase is always `h*(offset+rate*t)` using original global `t`. A tail-local coordinate is never substituted into that law.

## Conditional interval-restriction theorem

Assume the qualified original-source event supplies exactly one simple root `r` of a continuous original function `F` in the strict bracket `(a,b)`, with opposite nonzero endpoint signs. Let `m=(a+b)/2` and suppose an exact interval enclosure proves a strict sign for `F(m)`.

If the midpoint sign equals the left endpoint sign, the opposite signs at `m` and `b` place a root in `(m,b)` by continuity. Parent uniqueness identifies that root with `r`. Otherwise the midpoint sign must equal the right endpoint sign, and `(a,m)` retains `r`. In both cases the retained endpoints remain nonzero, the interval is nested, and its width is exactly half the previous width. Induction gives the initial width divided by `2^k` after `k` steps.

The theorem needs no new monotonicity or derivative claim across the bracket. Simplicity and uniqueness are inherited. Opposite samples alone do not establish that an arbitrary function has only one root, and the conditional bracket helper does not supply an accepted parent theorem.

A zero-inclusive point interval cannot select a half. Even an exact midpoint value of zero is outside this strict-bracket operation: the operation refuses rather than guessing a branch, silently shortening its trace or declaring a newly accepted rational root. Any failure for one selected event prevents a successful complete-cohort report. The parent zero-set theorem remains intact; a failed refinement does not mean that its source is root-free.

## B-spline point and one-sided semantics

Preparation checks the entire exact source grammar before constructing any Fraction. The source has eight specified fields, canonical harmonic keys and canonical rational tokens. Every coefficient spline has a built-in integer degree from zero through seven, the exact knot/control cardinality, sorted knots, a nonempty natural domain, full clamping to the original source interval and knot multiplicity at most degree plus one. Rational numerator/denominator sizes and container dimensions are bounded before construction or arithmetic.

The bounded Cox-de Boor table begins with the degree-zero indicators `u_i <= t < u_(i+1)` for right limits and `u_i < t <= u_(i+1)` for left limits. Terms with zero knot denominator contribute zero. The usual rational recurrence builds the higher-degree basis. A maximum-size point calculation has only a finite triangular table; it is not unbounded recursion. Nonnegative basis weights and partition of unity are checked for admitted inward evaluations.

At a checked fully clamped terminal endpoint, the physical value is the last control. Mechanically applying the half-open basis there would incorrectly return zero. The implementation also checks the inward left limit against that final control and the initial value against the first control.

At every original interior coefficient knot, exact left and right limits must agree. The actual selected cohort has 113 such coefficient-knot equalities. A locator must stay within the closure of one original common source span; no true source knot may lie strictly inside it. Thirteen initial brackets touch an original knot at a bound, so a blanket prohibition on knot endpoints would exclude established source events unnecessarily. Exact coefficient agreement supplies the needed endpoint continuity.

Prepared source objects retain immutable rational tuples, and their common source edges must equal the exact union of their channel knots. Their full coefficient/phase specification is reconstructed and checked against the stored source SHA-256 before evaluation. Consequently, changing a prepared object's edges cannot disguise a two-piece bracket as a single original span, and replacing its phase or channels cannot retain an old source identity.

## Exact trigonometric enclosures and outward receipts

The unchanged pinned `trig()` implementation reduces rational turns modulo one, handles exact cardinal phases, bounds pi with its fixed rational Machin construction, and evaluates finite rational Taylor polynomials with Lagrange remainder and a global one-Lipschitz argument-error allowance. The new model calls that point primitive directly and does not call the legacy permissive rational parser or `Span` constructor.

Each exact coefficient amplitude scales its cosine or sine enclosure. Negative amplitudes reverse enclosure endpoints. Exact interval addition then encloses the original `F(t)`. For a complete enclosure `[L,U]`, the compact receipt is:

- lower bound: `floor(2^80*L)/2^80`;
- upper bound: `ceil(2^80*U)/2^80`.

The implementation checks actual enclosure containment and requires the outward interval itself to have the same strict sign. A positive raw value `2^-82` is a decisive negative control: its 80-bit outward lower bound is zero, so it cannot supply the required strict receipt. The analogous negative value loses strictness at its upper bound.

Only compact outward bounds are serialized. Fresh validation recomputes the original-source enclosure chain. Decimal approximations, submitted midpoint signs and claimed interval endpoints are never used to drive the proof.

## Finite resource contract

| Quantity | Enforced ceiling |
|---|---:|
| Requested bisections per selected event | Exact built-in integer, 0 through 12 |
| Coefficient degree | 7 |
| Controls / knots per coefficient spline | 16 / 24 |
| Combined harmonic channels / maximum harmonic | 16 / 7 |
| Absolute original coordinate, phase offset and phase rate | 2 |
| Original rational and point-coordinate operand bits | 128 |
| Derived phase argument bits before trig work | 512 |
| Checked intermediate rational bits | 65,536 |
| Outward receipt operand bits | 256 |
| Outward dyadic precision | 80 bits |
| Report bytes / JSON value nodes / depth | 2 MiB / 65,536 / 32 |
| Public path text | 4,096 characters, no NUL |

Cox-de Boor additions, products and quotients check operand growth before arithmetic and check reduced results afterward. The unchanged trig expansion has a separately bounded input. Its fixed pi-sum numerator/denominator occupy 330/328 bits, and the pi-difference occupies 234/302 bits. For a reduced phase denominator of at most 512 bits, the reduced-angle argument denominator occupies at most 840 bits. A common denominator for the degree-at-most-28 Taylor/remainder terms divides the argument denominator to the power 28 times `28!`, giving at most 23,619 bits. Adding argument error gives fewer than 24,500 bits. The implementation checks returned trig bounds below 32,768 bits; even conservative unreduced binary products remain below 65,536. Scaled and accumulated original-source intervals are checked separately.

These are refusal limits, not a promise that every synthetically bounded spline can be refined. The public population is the qualified original cohort. Excessive arithmetic, an unresolved sign, malformed input or a missing parent premise yields typed nontruth. No adaptive precision or unbounded search is introduced.

Public JSON handling rejects floats, scalar/container subclasses, duplicate keys, cycles, aliased containers, excessive depth/nodes/strings/integers and oversized files before expensive proof work. Canonical rational syntax and operand bounds precede Fraction construction; reduced form is checked with bounded integer arithmetic. The report reader rejects overlong/NUL paths before filesystem access and reports read errors as typed refusal.

## API and evidence custody

`prepare_source_spec`, `spline_value`, `point_receipt` and `refine_bracket` support conditional mathematical tests. Their outputs do not admit caller sources into the accepted corpus or supply whole-cohort success. Public `expected_report(steps)` and `refine_selected(steps)` always execute the fresh qualified parent path. `validate_report(candidate,steps)` preflights the submitted object/request, computes a fresh complete requested result and compares bounded canonical bytes. The internal `report_from_replay` rechecks the exact parent/corpus/event bindings, source preparation, interval trace invariants and direct-input custody; it is not an alternate public proof route.

Project code is compiled directly from the same bounded bytes whose Git blob, byte count and SHA-256 were checked. Stale bytecode and preloaded project modules are not import authority. JSON is parsed from the retained checked buffers. The qualified consumer uses its own reviewed v2 runtime; this wrapper does not try to load the runtime recursively through its private project importer. Python and the standard library remain trusted, with no hostile-Python sandbox claim.

The [workflow](../../../../.github/workflows/mc1-pb00701-selected-implicit-root-refinement.yml) has one Python job, no matrix, exact 106-path PR/push triggers and literal candidate-head checkout. It runs the focused verifier and the preserved post-V54 frontier contract. No native campaign or production task is introduced.

## Verification and observations

Run the deterministic producer and focused contract from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python research/machining-completeness/tasks/MC-038/pb00701_selected_implicit_root_refinement.py --write-report --contract
PYTHONDONTWRITEBYTECODE=1 python research/machining-completeness/tasks/MC-038/verify_pb00701_selected_implicit_root_refinement.py --contract --self-test
```

The [independently authored verifier](verify_pb00701_selected_implicit_root_refinement.py) passes all 46 tests with one complete successful parent/refinement replay shared by its contract and tests. Its separate pinned symbolic B-spline lowerer checks all 4,130 coefficient amplitudes and all 966 point receipts. It checks the exact midpoint, selected half, nested original span, retained endpoint receipts and halved width for every step. Immutable expected bytes support report mutations after the actual replay.

Substantive controls include maximum-degree/seven fixtures, terminal values, both jump cases, exact and unresolved midpoint zeros, loss of strictness during outward rounding, global versus tail-local phase, negative amplitudes, zero requested steps, inherited-sign disagreement, source/event/uniqueness substitutions, dropped or duplicated events, actual selected-point and parent-producer failures, bounded arithmetic/parser inputs, and real accepted stale-cache/preload counterexamples. It also rejects forged prepared source edges, coefficients, phase and source identities, and changes to every direct-input byte/SHA attestation.

A separate review oracle uses the actual original channels' full-multiplicity Bernstein form with an independent quarter-angle/Machin/interval-Horner trigonometric calculation. It checked the same 4,130 channel evaluations, 113 coefficient-knot equalities and 966 logical point decisions at 961 source-scoped distinct coordinates. Every independent enclosure lies inside the corresponding reported outward receipt. This is distinct review evidence, not an additional runtime dependency or a substitute for the executable producer/verifier.

A timed local `expected_report()` call, including the actual parent replay and complete 69-by-12 operation, took 11.648830 seconds. Its result was byte-identical to the saved report. The independent verifier's final test phase took 14.317 seconds, with 25.388479 seconds for its whole process. These timing observations describe the shared local environment; they are platform/process observations rather than native geometry measurements. The saved witness contains no elapsed-time field.

The saved report occupies 1,755,761 formatted bytes and 1,094,975 canonical bytes, with 39,450 JSON value nodes and maximum depth ten. It retains the full parent baseline and all explicit traces within the declared fixed budget.

## Negative results and resolved review findings

The cubic transverse `Span` interface cannot represent the original degree-four/seven coefficient channels and was not reused as a general evaluator. Opposite sampled signs alone are insufficient without parent uniqueness and coefficient continuity. A right-hand value at a discontinuous knot cannot stand in for a different left limit. An exact raw sign can be lost by finite outward rounding. All these cases have executable negative controls.

Early review found that a prepared object's declared common edges could be replaced without checking them against its channel knots. The implementation now requires exact knot-union equality and reconstructs the full prepared source identity. A separate author inspection found that an internal formatter initially checked only the shape of direct-input byte/SHA fields; those four exact identities are now pinned and compared canonically. Both corrections precede final verification and are covered by substantive tests.

## Limits and downstream implications

The narrower locator is still an implicit zero of the same original function. This work does not produce an algebraic coordinate, prove a new complete zero set, handle arbitrary discontinuous sources, repair a generic owner route or implement a universal root-refinement service. Parent rational roots and the continuum are intentionally inherited unchanged. Further precision beyond twelve steps or altered arithmetic/selection bounds requires a separately specified contract and evidence.

For MSAC, source identity and the original parameter survive numerical localization; refinement cuts need not become machining events or source knots. For OpenSimachinist, the result is a bounded research consumer of established analytic event evidence, with explicit uncertainty/refusal semantics. It supplies no native geometry/kernel capability or STEP qualification.

PB-007-01/02/03/04 remain open; MC-B and MC-1 remain `NOT_ESTABLISHED`; production authorization remains false. The twenty-six operations, journal/material/body/lineage invariants, original source/phase/provenance, refusal and `UNCERTIFIED` semantics, and useful conventional STEP obligations are preserved. The [existing one-source V44 refiner](pb00701_v44_implicit_root_refinement.py), all historical providers, all frozen source reports and all navigation snapshots remain unchanged.
