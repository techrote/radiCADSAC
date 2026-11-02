# MC-038 / PB-007-01 — source-bound post-V54 evidence reconciliation

**Status:** deterministic-model research candidate; final-head review, CI and
protected landing remain separate integration gates. **Date:** 2 November 2026.
**Parent:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100).
**Archaeology baseline:** `45d4a10343ec8161e92e8bbed634f0edb5f16d24`.
**Additional source proof:** [PR #334](https://github.com/techrote/radiCADSAC/pull/334),
merged source `f69cf47f011fd22bd48687d963d015328fa69e1a`; qualification evidence is
recorded separately in the integration ledger.

## Purpose and falsifiable question

The frozen V54 archive contains **121 distinct original sources**, including
**20 whole-source route refusals** and **30 missing ordered-span-premise cases**.
Many later proofs address some of those exact sources, but the latest small
five- and six-source unions were explicitly selected subsets. Treating one such
subset as an exhaustive frontier leads to repeated work: the follow-up proposed
after PR #333 was the V6 `tail0` endpoint/source-knot case already proved by
PRs #307–#309.

This implementation asks a narrower, executable question: **For each of all 50
historically unresolved source IDs, what does the explicit registered set of
landed source-specific producers actually establish when rerun against the
original source?** It separates complete closed-source zero-set proofs, complete
proofs of only a refused second span, and ordered views of only one V6 child.

Falsifiers include a changed original source or phase, a missing or duplicated
historical ID, an unverified producer/report, a resource refusal, a source-local
proof promoted to a complete-source proof, overlapping selected unions counted
twice, a continuum represented as finitely many isolated roots, or any change to
historical dispositions or programme capability.

## Result and interpretation

The machine report enumerates all 50 historical unresolved IDs, but its evidence
registry is a finite explicit selection. Absence from this registry does not
prove the absence of every possible or otherwise published proof.

| Historical group | Complete source-specific zero-set witness | Refused second span only | One ordered V6 child only | No registered source event/order witness | Frozen total |
|---|---:|---:|---:|---:|---:|
| Route refusals | 11 | 9 | 0 | 0 | 20 |
| Missing ordered-span premises | 4 | 0 | 18 | 8 | 30 |
| Combined | **15** | **9** | **18** | **8** | **50** |

These are **supplemental evidence classifications**, not revised V54 verdicts.
The historical archive remains exactly 121/20/30. Among the 15 complete
source-specific witnesses, 14 have finite zero sets and one has a typed closed
continuum of zeros. None of the 27 partial results can be counted as a complete
source witness merely because the other historical span was `CERTIFIED`.

The accepted pre-#334 producer selection supplies 14 of these complete witnesses.
PR #334 supplies the additional exact original V23 source with the sole boundary
root `t=0`, order two, strict positivity on `(0,1]`, and exact lower bound
`F(t) >= 49*t^2/34992`. The new reconciliation reruns that producer and checks its
saved witness; it does not re-prove or broaden its Bernstein grammar.

No percentage from this table establishes PB-007-01, generic V27/V41/V43 route
coverage, MC-B, MC-1, native geometry or engineering STEP.

## Definitions and source identity

**Complete source-specific** means that a registered producer establishes the
full closed original-source zero set for that exact historical record. Depending
on the producer, this is a checked finite event/sign view, a complete root-set
partition, strict positivity over the full closed source, or a separately typed
continuum-zero component. This reconciliation does not invent a common event
coordinate algebra, a universal normalized event interface, or smooth
multiplicity at a nonsmooth source knot.

**Partial refused tail** means that the producer proves the actual second
original span `[1,2]` of a two-span source. The first span still needs its exact
ordered event/endpoint evidence and a composed full-source result. A sign proof
or complete root proof of `[1,2]` is useful even when the function is nonmonotone;
failure of monotonicity is not failure of zero-set completeness on that span.

**Partial ordered child** means that the registered V6 checker establishes an
ordered view for one actual original-source child. Its other span and the
cross-owner knot composition are not supplied by that receipt. The checker is
rerun on the full original specification, so the receipt retains the original
child index, source interval and historical owner through its replay digest.

**No registered source event/order witness** is a navigation result of the
explicit registry, not a mathematical impossibility verdict or a declaration
that every generic primitive has been tried.

Every report row carries the canonical SHA-256 of both the complete original
source specification and its full archive record, source parameter identity,
closed interval, affine phase law, actual B-spline piece edges, provenance,
historical disposition and span owner/refusal records. The evidence receipt
states the covered original interval, exact producer Git blob and SHA-256 of the
recomputed producer result. All source coordinates are inherited from the
byte-pinned original archive; caller reports are never passed to legacy
source/rational parsers.

## Registered producer coverage

| Producer family | Source IDs selected from the historical 50 | Scope consumed |
|---|---:|---|
| Five-source finite event replay, PR #331 | 5 | Full original finite zero sets; its three pinned underlying producers and reports are reexecuted |
| Closed continuum-zero source, PR #332 | 1 additional | Full closed continuum; its prior five finite IDs are checked but not counted again |
| Two-span V6 source-knot root-set, PRs #307–#309 | 1 | Shared physical knot zero counted once; sided orders preserved by original producer |
| Fixed original V27/V41 trigonometric child views, PR #294 | 3 | Source-bound proof replay followed by the original `compose` consumer |
| Stationary polynomial source-knot composition, PR #295 | 2 | Both originally blocked stationary tails; a third historically `CERTIFIED` source is excluded from the 50 |
| V44 algebraic proof-cut root partition, PR #310 | 1 | Complete actual-source root partition, with event-neutral proof cuts distinguished from physical zeros |
| V43 harvested positive source, PR #283 | 1 | Strict positivity on the full closed harvested interval, despite a genuine turn |
| V23 Bernstein source proof, PR #334 | 1 | One order-two exterior root and positivity on the remaining original source |
| V10/V11/V12/V13/V16/V17 V43 tail studies, PRs #284–#290 | 9 | Complete refused second spans only, never the full two-span source |
| Delegated V6 source-order checker, PR #282 | 18 | One checked ordered child each; full-source composition remains absent from this registry |

The code registry records exact Git blob pins. Saved reports used by the
five-source, continuum and V23 producers are independently pinned and compared
byte-canonically with their freshly recomputed results. Each producer preserves
its existing transitive source/module checks. Other producers regenerate their
proof results directly, so no saved status flag can replace execution.

## Reconciliation algorithm and refusal policy

1. Verify the frozen corpus, owner inventory, boundary artifact, auditor,
   26-operation domain, programme and current authority Git blobs. Rerun the
   original 121-source auditor and require the historical 20/30 split.
2. Reexecute the registered producers only on their pinned original sources.
   Reject any missing proof, nontruth/refusal, mismatch or custody drift.
3. Verify each selected producer's expected source identity and actual coverage
   interval. Full proofs must cover the original closed interval; partial
   receipts must cover one genuine proper source piece.
4. Enumerate the 50 exact historical IDs once. Join evidence by original ID and
   source hash. Retain every historically unresolved record, including the
   eight with no registered source event/order witness.
5. Derive the summary from the 50 rows. Preserve the original dispositions and
   all open programme gates.

Producer refusal aborts report generation. It is never converted into a
mathematical no-root verdict, a completed proof, or a reassuring lower count.
This executable has no caller-selected theorem or source input. Only its report
comparison API accepts external data, and that data is bounded before proof
replay and compared with the new exact result.

Report guards reject duplicate JSON keys, cycles, excessive depth/container
size, aggregate serialized bytes, huge integers, binary floats and custom
objects. Canonical JSON equality distinguishes booleans from integers, unlike
ordinary Python dictionary equality. A string containing an exponent or an
untrusted fraction remains inert report data and never reaches `Fraction`.

## Concrete remaining frontier

The next evidence-integration work is to consume both original spans and their
true knot for the nine V43 tail-only cases, or to combine the 18 V6 ordered
children with independently proved companion-span evidence. This reconciliation
does not imply those integrations are mechanically valid; each needs its own
mathematical and source-binding contract.

The eight cases with no registered source event/order witness are:

- `composite:PB00701_V14_EXACT_STRICT_DOMINANCE_MULTITERM_MULTIPLIER:tail100`
- `composite:PB00701_V18_EXACT_NONVANISHING_SOURCE_MODULE_FACTOR:tail0`
- `composite:PB00701_V18_EXACT_NONVANISHING_SOURCE_MODULE_FACTOR:tail100`
- `composite:PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC:tail100`
- `composite:PB00701_V18_EXACT_LAURENT_MODULE_FACTOR:tail100`
- `composite:PB00701_V15_EXACT_FINITE_STRICT_DOMINANCE_MULTIPLIER:tail100`
- `composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail100`
- `composite:PB00701_V26_EXACT_POINTWISE_COMPONENT_CONE_RESIDUAL_ORTHANTS:tail0`

These IDs, the 27 partial cases, and every current producer binding are
machine-readable in `pb00701-post-v54-evidence-reconciliation.json`. A future
extension must add the actual original-source proof consumer, qualify it, and
update the registry/version and report; editing the classification alone fails.

## Verification and reproducibility

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_frontier.py --contract --self-test
```

The first command reexecutes all registered producers once and then compares the
committed machine witness with that result. Adversarial tests reuse immutable
canonical bytes from the same independent replay to avoid rerunning the expensive
V6 proofs for every report forgery. Direct loading through `unittest` still
performs the real replay. The tests challenge denominator identity, duplicate
and omitted sources, count-preserving status swaps, tail/child promotion,
continuum typing, overlapping selected unions, source/phase/knot/provenance,
historical refusal, producer custody, capability forgery and resource limits.

For an intentional reviewed registry change, regenerate the witness with:

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701_post_v54_evidence_reconciliation.py --write-report
```

The focused GitHub workflow uses the literal PR head, runs Python only, and
triggers on MC-038 changes plus its external event-engine/domain/authority
dependencies. This deliberately protects transitive proof dependencies without
adding a platform matrix or a native campaign. Landing requires focused and
`mc1-static` success, distinct technical review, expected-head-protected merge,
reviewed/synthetic/landed tree equality and independently successful merged-main
checks.

## Programme implications and nonclaims

This adds reliable research navigation and an executable custody record. It
does not modify the frozen V54 inventory or the historic five/six-source reports,
integrate a general event solver, close PB-007, update programme gates, change
source semantics, or qualify native material/topology/B-rep/STEP.

For MSAC, engineering usefulness, undo/replay and preserved manufacturing intent
remain requirements. For OpenSimachinist, complete source-proof consumption,
native realization, material/body/lineage preservation and conventional usable
STEP remain unfinished obligations. The 26-operation domain is unchanged,
MC-B and MC-1 remain `NOT_ESTABLISHED`, production remains unauthorized, and
refusal/`UNCERTIFIED` states remain explicit.
