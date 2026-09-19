# Windows/Linux scale, soak and fault-recovery qualification

RCS-026 / issue #45 is the qualification campaign for the accepted Genesis-v2 research contracts under platform, scale and recovery pressure. The campaign is intentionally downstream of RCS-018 through RCS-025; it does not rediscover provider capability or relax earlier semantic findings.

## Contract under test

The durable operation journal remains manufacturing intent. Revision IDs, programme body IDs, lineage and provenance remain programme-owned across process restarts, provider changes and cache loss. OCCT 8.0.1 remains isolated in a worker process because RCS-024 found the same global-state and geometry defects in the tested 8.1.0 development candidate. RCS-025's finite deferred-state guard remains an implementation resource policy in addition to mandatory semantic reconciliation boundaries; the fixture value `2` is not promoted to a production constant.

## Cross-platform qualification subset

The mandatory matrix runs on `ubuntu-24.04` and `windows-2025` with Python 3.12. A C++17 probe is built and executed on both platforms so Windows evidence includes MSVC execution rather than being inferred from a Python-only run. The accepted RCS-019 canonicalizer vectors are reevaluated and compared by programme-level signature.

The scale campaign executes lathe, mill and mixed-provider histories at 10,000 and 100,000 journal events. Each result separately reports material-operation count, body mapping, lineage status, reconciliation count and authority signature. Repeating the same history must produce the same programme-level result. Bitwise B-rep identity is neither expected nor used as a pass condition.

## Worker and recovery stress

The coordinator launches the accepted process-isolated worker probe through success, timeout, deliberate crash and forced-kill paths. Every injected fault must be followed by a successful clean worker invocation. Cache recovery separately deletes and corrupts derived cache data, then reconstructs state from the authoritative journal; cache contents are never accepted as durable authority.

## Resource observations

Wall-clock latency distributions are recorded per platform. Python `tracemalloc` records bounded coordinator-allocation observations during scale runs. These measurements are useful for detecting obvious trend regressions but are not represented as OCCT-worker RSS, native handle accounting or a production performance SLA. Any later claim about native worker leakage requires native process measurements rather than reinterpretation of these Python observations.

## STEP soak and Gate-5 boundary

Linux CI rebuilds/reuses the exact OCCT 8.0.1 baseline and locked RCS-022 independent parser/consumer, then runs three complete live STEP export/read-back campaigns. Programme-level body/export/parser/consumer/check outcomes must be repeat-stable. The measured RCS-022 state remains `interoperability_unqualified`; repeated stability does not erase its independent-consumer metric blockers.

The campaign does not presently establish a live exact-pinned OCCT 8.0.1 Windows/MSVC STEP-worker soak. Therefore founding Windows STEP support remains a Gate-5 blocker unless exact Windows evidence is added. The deterministic Windows programme-level campaign is meaningful qualification evidence, but it is not a substitute for Windows kernel/export execution.

## Evidence lifecycle

The hypotheses, runner/toolchain pins, workload tiers and falsification rules are frozen in `research/rcs-026/experiment-plan-v1.json` before CI measurements. Per-platform and STEP-soak outputs are uploaded as machine-readable artifacts. Once exact-head artifacts pass validation, this document and DR-0023 must be reconciled to those measured values before the issue is considered complete.
