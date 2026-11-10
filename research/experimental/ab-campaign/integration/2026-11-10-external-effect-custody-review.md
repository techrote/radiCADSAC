# B5 — Cross-owner crash-window indistinguishability

**10 November 2026 · DETERMINISTIC_MODEL · Draft/HOLD; source-critical negative review, not a native defect.**

## Source identities and scope

- Accepted radiCADSAC main: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`; B5 integration Draft PR [#472](https://github.com/techrote/radiCADSAC/pull/472), preceding head `cac349e6307beeacbfb999fadc75b8e9a7a630fa`.
- Accepted CyberSand main: `d4b18e7f06839b35c8f6a66195206da0f33c5fa3`; [B3 #555](https://github.com/techrote/cybersand/pull/555) head `2622a1204748d3630affa7f08e8ebb51dbb8fbe8`, unchanged research `handoff_contract.py` blob `e8176a1a2a63fdd3edc1b097cf47647a20ff34bf`. [B3 restore-lineage experiment](https://github.com/techrote/cybersand/blob/2622a1204748d3630affa7f08e8ebb51dbb8fbe8/research/solver-certificates/handoff/RESTORE-LINEAGE-20261110.md) shows a fixed World incarnation is insufficient after rollback without trusted monotonic continuation.
- Other candidate heads inspected: radiCADSAC A1 #470 `2aa6fe5a`, A2 #471 `fb0bb9f8`, B1 #473 `ed5005bd`; CyberSand B2 #556 `f138874f`, B4 #554 `391be51b`. No applicant has qualified a cross-owner exactly-once native handoff. Reviews/comments and assigned file ownership were inspected on these Draft candidates. Source status/provenance is distinct from author-local test claims.
- B3's `ReceiptStatus.COMMITTED` is explicitly **MODEL_ONLY** and expressly not permission to mutate a Rapier body, spawn a native parcel or apply an external force. Native World, actual `physical_hash`, worker fences and Rapier main-thread owner remain protected. This B5 experiment **does not allege B3 code presently invokes Rapier**.
- Work only under `research/experimental/ab-campaign/integration/**` in B5's existing Draft branch. No author implementation, MC-038, physics or CI changes.

## Hypothesis, falsifier and elementary proof

**Hypothesis to challenge:** adding a trusted World incarnation and strictly increasing rollback-continuation serial to a prepared handoff is, by itself, enough to safely resume an *externally effectful* transfer after a crash.

**Counterexample:** consider a possible future opt-in native→main-thread handoff that has prepared an external action token `T` but has not durably recorded its outcome. There are two valid crash windows:

1. **H0:** external body/contact effect has not happened; native precommit state is saved.
2. **H1:** external effect has happened exactly once; crash occurs *before* durable native acknowledgement.

Restore the same native snapshot in both, advance the trusted continuation serial in both (correct B3-8 revocation), and assume the external effect survives but its receipt is unavailable. All native-observable fields, source signatures, accepted-token state, serial and native-state digest are now *identical*. The actual external-effect counts differ, 0 versus 1.

For any deterministic total recovery function of **only that native observation**, the same decision applies to H0 and H1:

| Recovery choice | H0 external count | H1 external count | Outcome |
|---|---:|---:|---|
| Replay non-idempotent external effect | 1 | 2 | H1 duplicate |
| Skip external effect | 0 | 1 | H0 missing |
| UNKNOWN/refuse | 0 | 1 | Safe to decline admission; **not** completion |

There is no correct total exactly-once decision from these identical observations. The proof is indistinguishability, over **every** positive integer payload, any finite source records and any token namespace; the 96 deterministic controls below only test the implementation of the counterexample. Neither trustworthy incarnation uniqueness nor monotonic continuation breaks this ambiguity. A zero-change native physical hash cannot certify external side effects that are absent from the hash's owned input.

**Conditional repair, not a production recommendation yet:** recover independently trusted, durable external transaction identity/outcome (and an idempotent applied-once effect), or make both owners' effect and custody atomically recoverable as a unit. A token-keyed external receipt that survives crash makes both histories retry to count 1; if the external ledger is lost while effect survives, the double effect recurs. The external-owner acknowledgement must be independently authenticated and tied to the current native continuation/source/units and worker/contact barrier. A mere client-supplied token or native generation is not such proof.

This is classical distributed transaction/recovery reasoning, not a new mathematical impossibility discovery. Prior art: Jim Gray, *Notes on Data Base Operating Systems* (1978), DOI [10.1007/3-540-08755-9_9](https://doi.org/10.1007/3-540-08755-9_9); Pat Helland, *Idempotence Is Not a Medical Condition* (2012), DOI [10.1145/2181796.2187821](https://doi.org/10.1145/2181796.2187821).

## Executed bounded deterministic experiment

Run from the B5 integration directory:

```sh
python3 external_effect_custody_probe.py
```

Local CPython standalone state-machine execution completed: **96 observationally indistinguishable history pairs**, **192** native-only deterministic total-policy failures, **96** conditional idempotent-external-ledger correct retry controls, **96** lost-ledger double-effect negative controls. The model carries an explicit native epoch, trusted continuation, source quantity, accepted map and token, and independently tracks external effects. **Exact published-source qualification:** the published B5 checker Git blob is `9c5e986d92dd860cb4a2d7983b7d8953da4bf2c7`. Recreated the published file byte-for-byte in the local CPython 3.13.5 environment, ran `python3 external_effect_custody_probe.py` (192/96/96 PASS as above) and independently ran `git hash-object` against the executed bytes: **exactly `9c5e986d92dd860cb4a2d7983b7d8953da4bf2c7`**, matching GitHub's fetched blob. This is **not** execution of the native CyberSand World, B3 parent module or Rapier; hosted B5 checks and independent review remain separate gates.

Falsification of this review requires either proving the two crash histories impossible under an actual admitted native/main-thread lifecycle (e.g. atomic reconstruction explicitly restores **both** owners), or producing a recovery rule that only sees these equal native states yet correctly distinguishes both effects. A recovery that sometimes returns UNKNOWN is safe but not a completed transfer, and does not refute the incompleteness result.

## B2/B3/B4 handoff and discovery-scoreboard delta

- **B3:** non-reusable continuation serial prevents old intent *admission* after rollback; it is insufficient to certify an already-applied external side effect. Define an opt-in external-effect custody boundary at the main-thread/World barrier; do not let `MODEL_ONLY` receipts confer authority. B3's model-only Water conservation theorem remains intact.
- **B2:** during unknown external-effect status, all coupled contact/pressure/actor dependencies are **UNKNOWN=>RECOMPUTE**, and incomplete worker participation remains BLOCKED, not permission to skip. Exact stale certificates are revoked on restore; physical parity is unestablished.
- **B4:** if such a consumer is ever proposed, require real host A/B/B/A with preserved effect receipts, actual 1/4 workers, full quantity/physical-hash checks, p50/tail and allocation/cost. A per-transfer O(1) token lookup and durable record is a *hypothetical* overhead floor, not measured or free. The original #470 packet-stage result and #470/#471/#522 accepted optimisations are unaffected.
- **A1/A2/B1:** mathematical expression identities and primitive-safe receipts remain distinct from authenticated spline source/knot provenance. Their new exact projective H2 quartic domain (A1), sparse mixed-rate jets (A2), and B1 receipt type hardening are bounded useful results but do not resolve real producer custody.

**Weekly delta:** one additional source-bound *non-admission* condition for a hypothetical cross-owner runtime consumer; **zero** newly accepted historical machining classes, **zero** B2/B3 native cost or physics gains and **zero** default changes. Maintain historical 121/20/30/50, 26 operations, MC-B/MC-1 `NOT_ESTABLISHED`, `production_authorized=false`. Research-only GO on the literal-blob-executed finite/model counterexample, HOLD on independent review and native lifecycle/physics qualification, NO-GO on calling native-only stamps exactly-once external authority. **No guarded research merge warranted in this run.**

**Next single decisive evidence request:** trace actual #406/#474 native→Rapier lifecycle for a concrete opt-in contact effect across crash/restart/restore, identifying which actor effects are reconstructed/retired and where an owner-bound idempotent receipt could legally reside. If effects are reliably rebuilt from saved native state, this model's persistent-external-effect premise is inapplicable to that particular transition; record a negative falsifier, not a retrofit by assumption. Do not touch native source.
