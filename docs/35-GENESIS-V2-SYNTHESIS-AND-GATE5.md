# Genesis v2 synthesis and Gate-5 decision

Status: RCS-027 synthesis candidate; Gate 5 remains pending until the exact Windows/MSVC OCCT STEP qualification job is frozen on the final PR head.  
Issue: RCS-027 / #46  
Genesis-v2 evidence range: RCS-018 through RCS-026 plus the RCS-027 Windows STEP closure probe.

## Purpose

This document is the bounded final synthesis for Genesis v2. It consumes the accepted evidence produced after the Genesis-v1 handoff freeze, reconciles architecture-impacting results without rewriting the v1 package trees, and defines the clean v2 handoff contract for later OpenSimachinist and MSAC repositories.

The research programme stops here only if every remaining limitation has a truthful, bounded success/pending/refusal policy. Performance tuning, optional future process classes and broader geometry coverage are production-owned when they cannot silently corrupt the stable journal/API/material-body/provider/reconciliation/STEP semantics.

## Evidence matrix

| Evidence | Accepted result | Gate-5 use |
| --- | --- | --- |
| RCS-018 integrated slice | journal/revision/body/lineage/provider/reconciliation/worker/STEP seams compose; failed derived work cannot mutate durable authority | foundation composition |
| RCS-019 canonicalizer | independent Python/Node paths and Windows/Linux evidence agree; `msac-journal/1.0` requires no semantic revision | deterministic journal normalization |
| RCS-020 lathe envelope | realistic circular-nose turning/boring, facing, shoulder, taper, groove/parting subset qualified; holder-collision undercut refused | exact lathe admission predicate |
| RCS-021 manual mill | independent material oracle qualified for measured fixed-axis domain; directional fallback is bounded only where material/spatial budgets close | safe milling fallback/pending policy |
| RCS-022 STEP Layer D | all 11 fixtures pass strict Layer C, independent parser and independent B-rep import; consumer metric gate remains `interoperability_unqualified` | truthful export qualification state |
| RCS-023 uncertainty | conservative interval algebra, strict one-sided decisions and fail-closed export-budget rules | end-to-end error semantics |
| RCS-024 OCCT differential | 8.1.0.dev1 reproduces decisive defects; retain OCCT 8.0.1 and process isolation; BRepGraph IDs stay private | backend/version/concurrency choice |
| RCS-025 handoff stress | durable identity survives provider replacement; hard semantic boundaries plus finite observable deferred-state guard required | coordinator/reconciliation contract |
| RCS-026 platform/soak | Windows/Linux programme semantics agree through 100k events and worker faults; Linux STEP negative state stable | cross-platform/recovery qualification |

The machine-readable counterpart is `research/rcs-027/evidence-matrix-v1.json`.

## Genesis-v1 decision audit

The machine-readable audit is `research/rcs-027/decision-delta-v1.json`. The material classifications are:

- DR-0001 through DR-0008 remain valid. Canonicalization is strengthened by executable conformance; journal physical meaning is unchanged.
- DR-0009 remains the STEP conformance/body-preservation contract and is refined by the exact RCS-022 profile plus its truthful Layer-D negative state.
- DR-0010 is retained and strengthened by DR-0020: uncertainty channels are now propagated rather than merely separated.
- DR-0011 is retained and strengthened by RCS-024/RCS-025: backend graph/topology identity is demonstrably unsuitable for durable programme identity.
- DR-0012 is retained and refined: deferred material is allowed only behind hard semantic/query boundaries and a finite observable resource guard.
- DR-0013 is retained and refined by DR-0017's realistic tool-envelope/reachability admission predicate.
- DR-0014 is retained and refined by DR-0018: fixed-axis directional material can be a bounded fallback, never an automatic STEP authority.
- DR-0015 remains the selected architecture, refined by explicit provider-handoff/reconciliation/error-budget rules.
- DR-0016 remains mandatory: OCCT process isolation is still the default and current-upstream evidence gives no reason to relax it.

No Genesis-v1 decision is silently rewritten. Genesis-v1 manifests and package trees remain historical frozen objects.

## Architecture questions resolved

### Selected architecture

Retain **semantic-provider hybrid**. The canonical journal, immutable revision graph, durable material-body identities, semantic lineage, source/audio identity and provenance are programme authority. Geometry providers own replaceable derived state only.

### Journal and canonicalization

Retain `msac-journal/1.0`. RCS-019 found no semantic revision requirement. Production canonicalizers must pass policy-versioned conformance vectors, preserve semantic boundaries even when numeric tokens coincide, use explicit units/frames/transforms, and fail closed on overflow or uncertified fitting.

### Lathe capability predicate

The first-class axisymmetric provider admits only operations for which all of the following are qualified: rotational material semantics, tool-envelope construction for the supported tool class/orientation, reachability, and explicit body/connectivity handling. The measured founding subset covers external circular-nose OD/facing/shoulder/taper, internal circular-nose through/blind boring, bounded rounded grooving and complete parting. Holder-collision undercut, general form tooling, live-tool/eccentric and other non-axisymmetric work routes to another qualified provider or `refused_unsupported`.

### Mill strategy and fallback

Use qualified exact fixed-axis strategies first. For the measured manual/freehand fixed-axis domain, the independent material-set oracle is regression truth and the directional material representation is a bounded fallback only when its per-case material and spatial budgets close. Otherwise return `accepted_pending` for refinement/reconciliation or an explicit refusal. Five-axis/tool-reorientation and rounded simultaneous-Z motion remain unqualified. A watertight mesh or valid B-rep alone is not material correctness.

### Hybrid/deferred representation

Deferred or directional state may preserve work and avoid pathological Boolean escalation, but it is not successful engineering output. Exact connectivity/body-selection/inspection/STEP requests are hard reconciliation boundaries. A separate finite observable resource guard bounds deferred accumulation; RCS-025's threshold `2` is a stress fixture, not a production constant.

### Uncertainty and error budgets

Carry source/canonicalization, transform, tool-envelope, provider, representation and reconciliation errors conservatively across every provider boundary. Unknown dependence uses interval/Minkowski composition. RSS/cancellation requires evidence. Manufacturing tolerance and STEP acceptance budgets are comparison criteria, never solver error. Positive removal intent survives ambiguity. Unknown required bounds or known budget breaches fail closed.

### OCCT backend and concurrency

Retain exact OCCT 8.0.1 commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42` as the founding B-rep/STEP backend. RCS-024 found the same decisive defects in the tested 8.1.0.dev1 snapshot. OCCT jobs remain process-isolated. Intra-worker parallelism is permitted only for specifically qualified operations that do not multiplex process-global mutable configuration.

### STEP profile and success semantics

The founding production-candidate profile is `rcs-022-occt-ap242dis-layer-d/1.0`: AP242DIS, `STEPControl_ManifoldSolidBrep`, explicit mm/in units, tessellation off, assembly auto, surface curves on, non-manifold export off, `Greatest` precision mode with `0.0001` in selected file units, and all selected committed material bodies transferred.

STEP success requires reconciled conventional B-rep, valid/material/body-preserving Layer A-C checks, propagated error eligibility and the requested qualification level. The exact RCS-022 Layer-D profile remains **`interoperability_unqualified`**. UI/API status must expose that fact; no tolerance widening, body dropping, post-export healing or tessellated substitution may manufacture qualification.

### Platform and recovery boundary

Programme semantics are qualified on hosted Linux/GCC and Windows/MSVC through the 100,000-event research tier, including worker timeout/crash/kill containment and cache regeneration from journal authority. Runtime/RSS figures are research observations, not product SLAs. Exact Windows OCCT STEP execution is the sole RCS-026 Gate-5 blocker being closed by the RCS-027 Windows qualification workflow.

## Gate-5 decision rule

Gate 5 is accepted only after `research/rcs-027/windows-step-qualification-v1.json` records a successful exact-pinned OCCT 8.0.1/MSVC three-repetition export/read-back campaign on the final PR head, with all RCS-022 adversarial controls passing and the Layer-D status remaining truthfully `interoperability_unqualified`.

That Windows execution does **not** need to turn Layer D positive. Gate-5 item 5 explicitly permits a concrete profile to remain unqualified when the exact blocker is preserved. What is forbidden is inferring Windows exporter support without executing it or reporting Layer-D success that the independent metric evidence does not support.

Until that frozen record exists, `gate5_status` is `pending_windows_step_evidence`.

## Production-owned research after Gate 5

The following do not block the foundation when their bounded policies are preserved:

- future independent STEP consumer/metric requalification capable of moving Layer D beyond `interoperability_unqualified`;
- broader lathe tool/holder/fixture families and exact analytic recovery of nose-generated surfaces;
- manual-mill refinement beyond the currently qualified fixed-axis directional subset;
- five-axis/tool-reorientation, rounded simultaneous-Z, live-tool/eccentric and other out-of-scope process families;
- production tuning of deferred-state resource thresholds, worker pool sizing and native telemetry;
- richer validated error representations and geometry-specific volume/angular sensitivity proofs;
- topology/history optimizations, provided programme identity stays independent of them.

These are implementation/capability extensions, not permission to reinterpret existing journals or saved source/audio/provenance.

## Handoff and freeze structure

Fresh v2 packages live under `handoffs/v2/opensimachinist/` and `handoffs/v2/msac/`. They are standalone implementation inputs. `handoffs/genesis-release-v2.json` binds their exact package tree hashes after the package trees are committed, the accepted evidence set, v1→v2 delta, and tag plan.

The v1 trees under `handoffs/opensimachinist/` and `handoffs/msac/` are untouched.

## Tag plan

After the RCS-027 PR is merged and the exact merge commit is independently verified on `main`, create these immutable annotated tags at that same verified commit:

```bash
git tag -a radiCADSAC-genesis-v2 <verified-merge-sha> -m "radiCADSAC Genesis v2 Gate-5 freeze"
git tag -a opensimachinist-handoff-v2 <verified-merge-sha> -m "OpenSimachinist Genesis v2 handoff"
git tag -a msac-handoff-v2 <verified-merge-sha> -m "MSAC Genesis v2 handoff"
git push origin radiCADSAC-genesis-v2 opensimachinist-handoff-v2 msac-handoff-v2
```

No production repository is created by RCS-027.
