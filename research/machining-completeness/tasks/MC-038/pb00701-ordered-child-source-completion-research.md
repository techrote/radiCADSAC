# MC-038: complete fifteen original sources previously represented by one ordered child

Status: bounded implementation and deterministic exact proof, pending separate
technical review and integration qualification. Source snapshot: 2 November
2026, `e0514500aeca59afa4924dcc2da3ca0c2688d9ac`.
Preregistration: [issue #100, comment 6591355781](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6591355781).

## Purpose and evidence boundary

The accepted [post-v54 reconciliation](pb00701-post-v54-evidence-reconciliation-research.md)
registered an ordered V6 view for only the second original source span of
eighteen cases. Its historical child `CERTIFIED` labels did not establish a
complete ordered physical root sets for the original composite sources.

This leaf supplies **fifteen complete original-source mathematical witnesses**.
It reexecutes the unchanged general exact B-spline lowerer and bounded transverse
interval engine on **both** actual source spans, checks the finite proof
partitions against the lowered functions, and composes them through the actual
continuous nonzero source knot. The selected sources have eight simple physical
roots in total; eight sources are root-free. The three exact-zero cases that the
transverse engine refuses remain explicit negative controls and are excluded
from the fifteen-source result.

Evidence class: **DETERMINISTIC_MODEL / exact rational mathematical research**.
These witnesses do not repair a historical owner adapter, change frozen
dispositions, or establish the general PB-007-01 theorem, native geometry,
engineering STEP, MC-B, MC-1 or production capability. The source set is finite
and explicit. Failure, refusal or exhaustion remains nontruth.

The [machine witness](pb00701-ordered-child-source-completion-witness.json)
contains complete original source/row hashes, source phase and parameter,
original global polynomial coefficients, every finite proof partition, physical
root descriptors, maximal sign cells, source-knot facts and dependency pins.

## Hypothesis and falsification

The preregistered hypothesis is that exact bounded transverse interval proofs
can complete both original spans of fifteen sources whose registered evidence
previously covered only one V6 child. A finite complete partition, continuous
original channel values at the shared knot, nonzero knot value and compatible
physical signs suffice for whole-source composition.

The hypothesis fails for any selected source if either span refuses, a closed
endpoint is zero or undecided, the partition leaves a gap or overlap, an alleged
simple-root bracket lacks strict opposite signs or derivative sign, original
phase/parameter identity changes, or actual channel continuity fails. A saved
report and historical child count cannot overcome any such failure. A missing
source, changed source identity or forged event also invalidates the result.

## Exact source set and findings

Every case has the original identifier `composite:<owner>:tail0`, source interval
`[0,2]` and true source knot `1`. The full owner strings and source identities are
in the model's fixed `CASE_PINS` and machine witness. Version labels below are
only compact labels for those exact rows, not claims about every source accepted
by an old version.

| Original owner | Simple roots in first span `(0,1)` | Simple roots in second span `(1,2)` | Whole-source sign sequence |
|---|---|---|---|
| V9 monotone single-harmonic ratio | `(17/64,9/32)` | none | `-,+` |
| V22 partial-derivative phase anchor | none | none | `+` |
| V24 mixed-quadrature phase anchor | none | none | `+` |
| V28 algebraic phase-cell projection | `(13/32,27/64)` | none | `-,+` |
| V29 nested algebraic phase projection | `(9/32,19/64)` | none | `-,+` |
| V30 adaptive projective separator | `(3/32,7/64)` | `(121/64,61/32)` | `-,+,-` |
| V34 correlated common factor | none | none | `-` |
| V35 proportional common factor | none | none | `-` |
| V36 varying-ratio shared factor | none | none | `-` |
| V37 two-polynomial shared factor | `(9/16,37/64)` | none | `-,+` |
| V38 direct rotated coordinate | none | none | `-` |
| V39 signed-A rotated coordinate | none | none | `+` |
| V42 orientation-transition bridge | `(45/64,23/32)` | none | `-,+` |
| V43 correlated closed handoff | none | none | `+` |
| V48 mixed-root single cut | `(15/32,31/64)` | none | `-,+` |

All fifteen source knots and thirty exterior endpoints are strictly nonzero.
Each bracket denotes the unique simple zero of the pinned original physical
function within that strict rational interval. A bracket is not an exact root
coordinate or a claim that the source-coordinate root is algebraic.

The old frozen census remains **121 original sources / 20 route refusals / 30
missing ordered premises**. This leaf adds fifteen source-specific witnesses;
the earlier reconciliation and current-state files are deliberately unchanged.
Their integrator may register the qualified additions later by exact source ID,
without double-counting independently completed source groups.

## Source lowering and finite proof

The [general coupled B-spline lowerer](pb00701_coupled_bspline_model.py) preserves
the original parameter while converting each actual spline piece to rational
power coefficients. Its `_normalise_harmonic_splines`, `_master_boundaries` and
`_piece_from_normal` routines give the exact two pieces `[0,1]` and `[1,2]`.
The first amplitudes have degree at most three and the second amplitudes are
constant. The V37, V42 and V48 cubics are retained; the older convenience
degree-zero/one `linear_piece` helper is not used.

For each piece, the unchanged [transverse interval kernel](pb00701_transverse_trig_interval.py)
evaluates the original expression

`F(t) = sum_h [P_h(t) cos(2*pi*h*(offset+rate*t)) + Q_h(t) sin(2*pi*h*(offset+rate*t))]`.

Rational Machin arctangent bounds enclose pi. Rational Taylor polynomials,
Lagrange remainder bounds and the trigonometric Lipschitz bound enclose every
point value. The kernel derives global first- and second-derivative magnitude
bounds from the actual polynomial coefficients and `2*pi < 44/7`. For example,
the first-derivative bound sums each amplitude-derivative norm plus the harmonic
frequency bound times the amplitude norm. The second-derivative bound includes
second amplitude derivatives, twice frequency times first amplitude derivatives,
and squared frequency times amplitudes.

On a rational cell with midpoint `m` and radius `r`, widening `F(m)` by `M1*r`
encloses every value in the cell; widening `F'(m)` by `M2*r` encloses every
derivative. A strict function sign proves no root. A strict derivative sign and
same strict endpoint signs also prove no root. A strict derivative sign and
opposite endpoint signs prove exactly one simple root by the intermediate value
theorem and strict monotonicity. Further rational cuts supply a strict isolation
bracket of width at most `1/64`.

The new consumer checks these conditions again against the actual lowered span,
including point signs at the root-bracket endpoints. It checks every partition
cell is in order, covers the complete closed span without gaps or overlap, and
continues the same physical sign chain. A returned count/status field is not
sufficient. The complete source has no other roots because both span covers are
exhaustive and their shared knot is proved nonzero.

Each run permits at most twelve recursive levels and two thousand visited nodes
per actual span. These are refusal bounds, not an assertion that every admitted
analytic source terminates successfully. The successful selected first spans
needed at most fifteen visited nodes. No wall-clock or native performance claim
is made.

## Original knot and physical composition

Every original polynomial channel is evaluated exactly at `t=1` from the two
adjacent pieces. Equality is checked separately for each cosine/sine harmonic,
so continuity is established from the original source rather than inferred from
matching sampled values. Both complete span proofs establish the same strict
physical sign at the knot.

The composite root list concatenates the ordered first-span and second-span
roots in the original parameter. Maximal open physical sign cells merge through
the nonzero knot. The real spline knot and all internal certificate partition
cuts remain distinct concepts: no partition cut becomes a physical event merely
because it refines a proof.

V30 is the positive control for composition with a root in each span: signs are
negative, positive, negative, and the continuous knot is positive. The model
also checks root-free cases of each sign, including genuinely cubic amplitudes.

## Preserved negative boundaries

The exact original first spans of three other child-only cases are replayed as
negative controls with depth eight and node limit 256:

| Excluded original case | Unchanged interval-kernel refusal | Retained work |
|---|---|---|
| V23 phase-amplitude anchor, `tail0` | `UNDECIDED_EVENT_OR_TANGENCY` | Exact original-knot zero and sided evidence |
| V25 component-cone anchor, `tail0` | `UNDECIDED_EVENT_OR_TANGENCY` | Exact original-knot zero and sided evidence |
| V40 signed-B coordinate, `tail0` | `UNDECIDED_ISOLATION_CUT` | Exact rational physical zero at a bisection cut |

These refusals are not impossibility results. Their source hashes and original
record hashes are retained. They are not silently omitted from the eighteen-case
cohort or promoted into this fifteen-case positive result. A subsequent bounded
leaf can supply exact zero identities and sided source-knot semantics while
preserving the transverse kernel's existing contract.

## Custody, report validation and resource limits

The model pins the frozen corpus, historical inventory/coverage, accepted
reconciliation used to select the cohort, programme/domain/authority, and the
complete lowerer/interval implementation chain. That chain includes
`pb00701_rational_turn_model.py`, `pb00701_event_model.py` and the external
`MC-032/event_engine.py`. Each fresh replay reads and pins the five implementation
source buffers, then compiles those exact buffers into a private module graph.
Normal project imports and the event model's dynamic MC-032 import use that
graph through module-local import handlers. Existing bytecode caches and
preloaded project modules cannot replace the checked code. Global import hooks
and module caches remain unchanged; the legacy lowerers' search-path additions
use a local list. File pins are checked again after replay, and module paths
and transitive identities must match the checked graph.

The verifier also bounds, pins and directly compiles its own model source
buffer, closing its bootstrap dependency before any model code executes.
Ordinary source/path checks and disabling bytecode writes would not establish
this property: Python can accept altered timestamp/size-matched bytecode even
while the source hash is unchanged. The regression suite reproduces that
counterexample for every implementation module and for the verifier's model,
then demonstrates that the checked-buffer execution preserves the source code.

Every consumed authority, corpus and prior-cohort JSON input is decoded from
the same bounded byte buffer whose Git blob was checked, with an exact input
path whitelist. A filesystem replacement between checking and consumption
cannot substitute different data. Every selected original record and original
specification retains its separate SHA-256 binding. These custody corrections
leave the mathematical procedures, all original source records and the saved
machine witness byte-for-byte unchanged.

Only those exact original records reach legacy source parsers and interval
constructors. Public report validation first checks typed bounded data, then
compares canonical bytes against a fresh complete replay. Caller report fields
never become source coefficients or proof premises. The public proof-validation
entry point is `validate_report(candidate)`; lower/partition/composition helpers
operate inside that replay and are not arbitrary submitted-proof acceptance APIs.

Preflight rejects cycles, custom types, floats, boolean/integer substitutions in
the canonical comparison, strings over 8192 characters, integers over 256 bits,
containers over 1024 members, depth over 32, more than 65536 visited nodes, and
aggregate data over one MiB. File reads are bounded before allocation. JSON
loading rejects duplicate keys, nonfinite/decimal scalars and oversized integers.
Canonical rational parsing checks bounded ASCII integer/ratio syntax before
constructing a `Fraction`; exponent strings cannot trigger expansion.

## Verification and adversarial controls

Run the complete source replay, saved-report comparison and adversarial suite:

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_ordered_child_source_completion.py --contract --self-test
python3 tools/validate_repo.py
python3 tools/validate_machining_completeness.py
python3 tools/validate_machining_completeness.py --self-test
```

The 29 test methods include actual composition counterexamples: changed channel
values at the original knot; missing, overlapping or reordered spans; changed
companion parameter/phase; a proof object for a different lowered function;
partition gaps; erased real crossings; false root isolation, derivative signs
or multiplicity; and actual resource exhaustion. They also challenge source
custody, partial-to-complete promotion, duplicated identities, false knot events,
report aliases/resources, unsafe rational syntax, dependency drift and false
gate assertions. Seven added custody methods exercise actual accepted stale
bytecode, same-path preloaded modules, transitive source replacement after
pinning, JSON replacement after hashing, the exact input whitelist, complete
guarded JSON consumption, and bounded model bootstrap. The tests verify that
global import machinery and search paths remain unchanged. Replay refusal
aborts generation instead of falling back to a saved successful report.

To regenerate the machine witness explicitly:

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701_ordered_child_source_completion.py --write-report
```

The focused workflow checks out the literal PR head, uses one Python job with a
five-minute timeout and read-only repository permissions, and triggers on the
owned artifacts plus the complete pinned dependency set. Distinct technical
review, final-head CI, guarded merge/tree equality and merged-main qualification
remain integration requirements. This report does not predeclare those results.

## Invalidation and programme implications

Any original source/phase/parameter/piece, historical record, lowerer or interval
dependency change invalidates these source-bound witnesses until replay and
review qualify the new identity. A weaker partition, lost companion span,
unsupported knot, refused root, resource exhaustion or changed authority cannot
be normalized into successful coverage.

For MSAC and OpenSimachinist, the result provides a concrete exact event-evidence
slice for future research integration. It supplies neither an application nor
native material/topology reconstruction. Original provenance, canonical journal,
material-body/lineage semantics, refusal/UNCERTIFIED behavior and conventional
usable engineering STEP obligations remain protected. All 26 operations remain
in the domain. PB-007-01 and the other PB-007 obligations remain open; MC-B and
MC-1 remain `NOT_ESTABLISHED`, with production authorization false.
