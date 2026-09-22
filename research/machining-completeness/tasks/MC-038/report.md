# MC-038 — MC-B constructive-coverage integration decision

Status: **BLOCKED — MC-B remains `NOT_ESTABLISHED`**.  
Issue: #100.  
Source baseline: `e82f417b0474a51648928f26d1035d39860777b0`.  
Native/paid execution: **none**.

## Decision

MC-038 cannot honestly accept MC-B from the current reviewed evidence. Its gate contract requires all required constructive branches to have reviewed terminating routes with no required lemma left open. The current evidence instead contains explicit, still-live proof and representation blockers. The frozen 26-operation denominator is therefore preserved and MC-B remains `NOT_ESTABLISHED`; no operation is dropped, no timeout/refusal/uncertified result is relabelled as success, and no negative result is overwritten.

This is a bounded integration/blocker review, not a repeat of broad defect discovery. The review consumes the already-recorded MC-005 capability plus the current accepted/negative artifacts of MC-006/007/008/016/018–023/026/054/058 and asks only whether their surviving obligations permit the MC-B gate to move.

## Decisive live blockers

The constructive side still carries four proof-family blockers:

- `PB-007-01` — unconditional finite exact decisions for required tangential, multiple-root and singular transcendental events are not established. MC-007 and MC-022 deliberately fail closed rather than pretending repeated refinement or a timeout decides these cases.
- `PB-007-02` — a general semantics-preserving route for coupled spindle/feed/eccentric membership remains open outside the bounded qualified slices.
- `PB-007-03` — a universal finite exact source codec for every admitted imported-stock and arbitrary form/undercut cutter instance remains open/propagated.
- `PB-007-04` — universal exact topology/connectivity certification remains propagated to the critical-event/material-body work.

The output/representation side still carries `RB-016-01` through `RB-016-05`, including complete conventional representation coverage, durable multi-body mapping, certified micro-material preservation, exact-zero/touching/singular output without healing or tolerance fusion, and complete reconstruction/certificate coverage for the frozen profile.

These are sufficient to reject gate promotion. They are not converted into new blockers and their producing identities are preserved.

## Proof-obligation state

The current proof register has only PO-01 accepted. In particular PO-02 (sweep semantics), PO-03 (finite composition), PO-04 (sound classification), PO-05 (finite progress), PO-07 (topology/connectivity), PO-08 (complete dispatch) and PO-09 (conventional engineering realization) remain open. PO-05's own contract explicitly says any explicit proof blocker keeps it open and that timeout, iteration caps or provider cycling are not semantic success.

MC-030 and MC-026 establish a noncycling dispatch/design selection, not a proof that every admitted request now succeeds. The selected `PRIMARY_CERTIFIED_ADAPTIVE_IMPLICIT` route still has typed fail-closed terminals for unresolved event/source cases, while `EXACT_CELL_SEMIALGEBRAIC_CONTROL` remains only an independent bounded challenger. Directional, mesh/Manifold and sparse-volume representations remain non-authoritative accelerators/challengers.

## Orchestration defect found by the integration review

The current task graph has a dependency inversion that prevents the programme from repairing the very obligations MC-038 must see closed:

- package order places MG-07 native material realization (`MC-031`, `MC-032`, `MC-033`) before MG-08 (`MC-038`);
- `MC-031`, `MC-032` and `MC-033` nevertheless each require **MC-038 as a capability dependency**;
- PO-02 is owned by MC-031, PO-04/PO-07 are owned by MC-032, and the live PB/RB repair routing also requires MC-031/032/033 work;
- MC-038 cannot accept while those obligations are open.

Accepting MC-B merely to unlock its producing remediation would be circular and would weaken the gate. The repair must instead correct orchestration so the pre-gate MC-031/032/033 remediation can run under the already accepted MC-A/domain authority and their existing artifact dependencies, while MC-B stays `NOT_ESTABLISHED`. Later reconstruction/qualification work whose capability dependency is genuinely post-gate should remain gated.

## Recorded repair path

The bounded final repair path is:

1. correct only the MC-038 → MC-031/032/033 capability inversion, with explicit adversarial checks that MC-B, production authorization, the 26-operation denominator and protected semantics do not move;
2. run MC-032 pre-gate remediation for exact-zero/multiple/singular event and topology/connectivity obligations (`PB-007-01`, `PB-007-04`, PO-04/PO-07), retaining any theorem-level remainder as an explicit blocker;
3. run MC-031 pre-gate remediation for source/sweep/material coverage (`PB-007-02`, `PB-007-03`, PO-02) without narrowing the admitted domain;
4. run MC-033 pre-gate durable material-body/lineage state work needed by the representation blockers without backend topology identity becoming durable authority;
5. retry MC-038 only after producing-owner evidence actually closes every lemma required by the MC-B contract.

The integration review does not claim that this ordering alone proves MC-B. It merely removes the programme-level circular dependency so the required evidence can be produced and reviewed honestly.

## Adversarial/boundary controls

`verify.py` rejects a missing or falsely closed blocker, MC-B promotion, production/expensive-execution authorization, denominator drift away from 26 operations, conversion of required open POs to accepted evidence, disappearance of the dependency inversion from this frozen blocker review, or weakening of protected source/audio/provenance, canonical-journal, positive-volume, durable body/lineage and conventional STEP semantics. It also checks that MC-038 remains retryable in the programme registry rather than being misrepresented as an accepted capability.

No native geometry or paid campaign was required to establish this blocker. No protected historical source, audio, provenance or Genesis evidence was edited.

## Verification

```text
python3 research/machining-completeness/tasks/MC-038/verify.py --contract
python3 research/machining-completeness/tasks/MC-038/verify.py --self-test
python3 tools/mc_workflow.py verify MC-038
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

A blocked MC-038 review may be merged only after the exact PR head passes the repository gate. Issue #100 must remain open because its capability acceptance criterion is not satisfied.

## Orchestration repair status

Issue #156 resolved `ORCH-038-01`: MC-031/032/033 now consume accepted MC-A (`MC-005`) capability instead of MC-038 capability, while MC-034/035/036/037 retain the legitimate post-gate MC-038 dependency. This removes the programme-level dependency inversion only. MC-038 remains **BLOCKED** on the recorded PB-007/RB-016 and proof-obligation evidence; MC-B remains `NOT_ESTABLISHED`.

## Post-remediation retry and ORCH-038-02 gate-scope reconciliation

After MC-032/#94, MC-031/#93 and MC-033/#95 completed, MC-038 was retried against authoritative main `7a480da12e46764ed972c814df3991ebbf0baee5`. The retry remains **BLOCKED**: those producing-owner tasks deliberately retain the theorem-level `PB-007-01`, `PB-007-02`, `PB-007-03` and `PB-007-04` boundaries, and the corresponding pre-gate PO-02/PO-04/PO-05/PO-07/PO-08 claims are not all established. MC-B therefore remains `NOT_ESTABLISHED`.

The retry also exposed a narrower contract-classification error in the historical v1 review. The canonical programme defines MC-B as reviewed terminating material/topology routes plus explicit finite output construction **before full native implementation claims**. By design, MC-034/035/036/037 remain capability-gated on MC-038 and MC-039 consumes their implementation artifacts later. It is therefore circular to demand that the global downstream native/consumer obligations produced by those tasks be *closed before* MC-038 can establish the capability that unlocks them.

`gate-scope-retry-v2.json` resolves this as `ORCH-038-02` without erasing any negative evidence:

- the historical `constructive-coverage-review-v1.json` remains byte-identical and continues to describe the evidence available at that review;
- `PB-007-01..04` remain explicit **pre-gate constructive blockers** and retain their existing OPEN/OPEN_PROPAGATED states;
- PO-02, PO-04, PO-05, PO-07 and PO-08 remain the still-open proof obligations directly relevant to the current MC-B constructive gate;
- `RB-016-01..05` remain fully **OPEN**, but are classified as downstream representation/native-consumer qualification blockers rather than obligations whose closure is demanded before MC-B;
- global PO-03 (owned by MC-039), PO-06 and PO-09 (owned by MC-037) likewise remain **OPEN**. They are not accepted, waived or weakened; their producing implementation work remains downstream of MC-038 capability;
- MC-034/035/036/037 retain their MC-038 capability dependency and MC-039 retains its reconstruction-artifact dependencies. No native implementation work is moved ahead of the gate.

This supersedes only the v1 review's **gate-prerequisite classification** of those downstream obligations. It does not supersede their blocker state, evidence, or later MC-1 significance. The earlier statement that every listed RB/PO was sufficient *as a prerequisite-to-close before MC-B* is therefore historical and overbroad; the blockers themselves remain real and unchanged.

The distinction is adversarially enforced. The MC-038 verifier now rejects either direction of corruption: falsely closing/promoting a surviving pre-gate PB/PO to force MC-B through, or reintroducing a circular requirement that post-gate MC-034..039 evidence must already exist before MC-038 can unlock those tasks. It also rejects moving native work before the gate, closing any RB-016 blocker, accepting downstream PO-03/PO-06/PO-09, changing the 26-operation denominator, laundering refusal/UNCERTIFIED into success, or weakening source/audio/provenance, canonical-journal, positive-volume, durable-body/lineage or conventional STEP semantics.

With ORCH-038-02 repaired, the next dependency-ready repair is again the surviving **pre-gate proof/constructive blocker path**, beginning with `PB-007-01`. MC-038 must not be retried for acceptance until those required pre-gate claims are genuinely discharged.
