# B5 — Independent bracketed zero-packet review of CyberSand #470

**2026-11-10; deterministic source-data re-reduction; Draft/HOLD.** This is an independent post-hoc review of historical instrumentation, not a native benchmark, a causal estimator, a native performance certificate or permission to modify CyberSand.

## Source and policy checkpoint

- radiCADSAC accepted main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`; CyberSand accepted main `d4b18e7f06839b35c8f6a66195206da0f33c5fa3` at inspection.
- Reviewed CyberSand B4 Draft [#554](https://github.com/techrote/cybersand/pull/554) exact head `d6d06f05e3e20fcf2b8e4d98345a2e37ef42b46d`; observed source file [hs470_abba_profiles.json](https://github.com/techrote/cybersand/blob/d6d06f05e3e20fcf2b8e4d98345a2e37ef42b46d/research/solver-certificates/performance/hs470_abba_profiles.json), Git blob `40e0813ed6b80bef6feb8d721c196e43ea8d0517`. This is the 12-record published capture of [6 November 2026, run 42302283599 / job 128182806453](https://github.com/techrote/cybersand/actions/runs/42302283599/job/128182806453), not a new execution.
- Control source `4a80af2a891332176a3912a235582d77d076a185`; candidate source `6aa03fe21dbe88b308793f377e4d223a90e4da8f`; ordered arms C1, B2, B3, C4, three canvases per arm. Host Linux AMD EPYC 9V45, Godot 4.7-stable headless, four *logical CPUs*, not evidence of four participating native workers.
- Preserved acceptance: #470 hard-surface packet-stage, #471 neighbour cursor, #522 PressureFlow improvement are separately recorded accepted-main optimisations. B2 #556 and B3 #555 are Draft, with no demonstrated native tick saving. The original default Water FreeMass policy, MAT-AUTH, authoritative World, Rapier owner, worker fence, physical hash and persistence are unchanged.
- radiCADSAC MC-B / MC-1 remain `NOT_ESTABLISHED`, `production_authorized=false`; frozen 121/20/30/50 census and 26 machining operations are unaffected.

## Question and independent calculation

**Question:** After averaging the two forward/reverse C/B differences, how much of the observed whole-simulation summary-statistic movement survives subtraction of the same-arm, zero-packet canvas? This is a *sensitivity contrast*, not a treatment-effect estimate.

For one canvas and summary metric `m`, take reported aggregate values `x1,x2,x3,x4` in arm order C1,B2,B3,C4. Define `g_forward = x1-x2`, `g_reverse = x4-x3`, `g_bracket = (g_forward+g_reverse)/2`. The cross-canvas contrast is `g_bracket(bench-canvas)-g_bracket(my-canvas)`. This is the arithmetic average of B4's already published *descriptive* forward/reverse contrasts; it is NOT the median of pooled ticks, an A/B/B/A randomized-block estimator, or a paired confidence interval.

I independently parsed all **12** source records from the GitHub-connected exact file, verified one record per arm/canvas key, the 6 November run identifier, the ordered arm labels, source blob `40e0813e…`, and packet counts. I recomputed the following directly from the source values using separate arithmetic, rather than trusting B4's report or calling its reducer. The original Python checker and upstream GitHub Actions job were **not rerun**.

| Published aggregate statistic | Bench C1→B2 gain (ms) | Bench C4→B3 gain (ms) | Bracketed bench gain (ms) | Bracketed zero-packet gain (ms) | Bracketed contrast (ms) |
|---|---:|---:|---:|---:|---:|
| simulation p50 | +0.206383 | +0.086287 | **+0.146335** | +0.138079 | **+0.008256** |
| simulation mean | +0.723760 | +0.100184 | +0.411972 | +0.269478 | **+0.142494** |
| simulation p95 | +2.760954 | +0.194995 | +1.477975 | +0.444075 | **+1.033900** |

Packet-stage sample counts in `bench-canvas` are **122, 142, 143, 143**; `my-canvas` has **0, 0, 0, 0**. This gives **8.256 microseconds** p50 contrast, about **0.10%** of the roughly 8.2 ms benchmark-simulation p50 *as a scale comparison only*. The p95 contrast is much larger and unstable: the bench control-only p95 changes **−2.489773 ms** from C1 to C4 (11.464171 to 8.974398 ms), while the bench p50 control drift is −0.015629 ms. The corresponding zero-packet control-only p95 drift is **−0.831607 ms**. In the larger stress canvas the forward/reverse p50 differences have **opposite signs**: −0.218965 and +0.764767 ms; stress packet calls are just 4,1,4,3.

Sample counts differ between arms (`bench-canvas` observed snapshots **259,255,256,255**). These are independently sampled summary statistics, not a matched tick series. The unit arithmetic is reproducible by reading the exact pinned JSON file and applying the formulas above; it does not depend on image interpretation, native rebuilds or numerical root samples.

## Source-critical disposition and falsifier for next design

**GO** — retain the original qualified #470 packet-stage improvement. The B4 historical packet-work reduction remains real evidence for *that stage*, not for general full-tick acceleration.

**HOLD** — whole-tick causal attribution to #470; any B2 region-sleep runtime win; any B3 representation-transfer runtime win. The source data contain a nontrivial timing shift where **no packets execute**, and the p50 cross-canvas bracketed descriptive residual is much smaller than either canvas's standalone gain. Conversely, the p95 residual is sizable but control-only drift is very large; it cannot be interpreted as a robust native tail improvement. The control canvas is smaller/different, so its shift is **not necessarily an exchangeable nuisance correction**. Neither a zero/near-zero descriptive residual nor a nonzero residual proves a causal effect.

**Next decisive falsifier, if an authorized native campaign becomes available:** preregister a same-host bounded A/B/B/A with identical recorded event/terrain streams; emit per-tick **paired** packet and complete-tick durations plus packet counts, worker participation (actual 1/4), physical-hash parity for identical laws, RSS/allocations and pressure/gas/contact/wake diagnostics. Specify a stop budget and work-avoidance-versus-overhead condition before measuring. With a changed hybrid law, require explicit physical tolerances instead of claiming hash parity. No such campaign was run or requested here.

The distinction between time/run blocking and unmeasured nuisance effects is standard experimental-design practice; see [NIST/SEMATECH, randomized block designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm). This is not a novel mathematical theorem. The new useful result is an independently source-checked **negative attribution constraint** for the present empirical CyberSand evidence. Do not merge this as native acceptance or change current solver defaults.
