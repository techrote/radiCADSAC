# MC-013 — Physical adversarial corpus F09–F12

Status: **COMPLETED_RESEARCH pending exact-head CI at authoring time**. Issue #75. Source baseline `bfe1ee16a28b3c5193d43f0e553a7cb782ee2aa1`.

## Hypothesis and falsification criterion

The F09–F12 tranche can be made candidate-independent and physically discriminating without narrowing the admitted machining domain or turning approximation tolerances into material truth. The task is falsified if any family requires candidate output to define expected truth, if signed/equality neighbours collapse under the reference predicates, if physical access/body retention cannot be witnessed, or if constructing these fixtures requires weakening inherited corpus/provenance semantics.

## Dependency reconciliation

MC-002, MC-003, MC-010 and MC-055 are consumed only through their accepted immutable artifacts. MC-055's strengthened-version map is preserved: F09 has no equivalent historical phase-sensitive record; F10 is motivated by historical separation controls; F11 by contact/connectivity controls; and F12 by sub-tolerance/sliver controls. Historical RCS output is provenance/adversarial motivation only and never supplies current expected truth.

## F09 — phase-dependent turning

F09 uses one shared exact spindle-phase/feed parameter. A body-fixed azimuth meets a fixed machine-angle tool at a deterministically derived phase; axial feed is interpolated from that same phase. The fixture therefore distinguishes two material probes at the same radius and axial location solely through body phase, and separately checks phase/feed correlation. Closed gate endpoints are equality cases, with exact signed phase neighbours around the end boundary.

This is intentionally a bounded rational witness, not a claim that the general transcendental event problem from MC-007 is solved.

## F10 — many surviving components

Seven full cross-stock milling slots produce eight positive-volume slabs, each with a durable output identity and explicit support assumption. Exact controls distinguish a complete separator from a `1/1000000` mm positive residual web and a negative-overtravel neighbour. Any strictly positive web remains one component; exact zero changes the component count to eight. Scalar-volume agreement cannot substitute for retaining all eight bodies.

## F11 — singular boundary limit

Two externally accessible through-bores are arranged so their circular cross-sections are exactly tangent in the base case. Exact `+1/1000` and `-1/1000` centre-separation neighbours are respectively separated and penetrating. The shared tangent point has zero squared clearance to both cutter boundaries. The oracle records `SEPARATED`, `TANGENT` and `PENETRATING` as three distinct semantic states; no epsilon may choose a neighbour for the equality case.

## F12 — scale and precision separation

F12 places an exact `1/1000000` mm retained web near `x=999` inside a 1000 mm stock extent, giving a stock-to-gap ratio of `1000000000`. The same local gap is represented before and after exact translation by +998 mm, and an exact +90° rigid rotation is checked without rebuilding the durable body. Zero and negative-width neighbours remain distinct. Positive material is not deletable merely because the feature is below an engineering error tolerance.

## Independence and protected semantics

`fixture_oracle.py` imports only `Fraction`-based standard-library support and contains no RCS/candidate geometry import. Its SHA-256 is pinned in the corpus contract. Protected `research/rcs-*` sources remain byte-identical; source/audio/provenance, canonical journal, positive-volume, durable-body/lineage and historical negative-evidence semantics are unchanged.

## Programme state

F09–F12 are constructed as `BUILT` prospective records. F13–F16 remain mandatory and `UNBUILT`. No native or paid campaign was run. `MC-A` remains `ACCEPTED`; `MC-B` through `MC-F` and `MC-1` remain `NOT_ESTABLISHED`. `BUILT` is not candidate PASS, proof-obligation acceptance or production authorization.

## Verification

The deterministic verifier checks dependency blob identities, oracle source/import independence, all exact family witnesses, live registry progression, protected historical blobs, branch diff hygiene and deliberately corrupted controls. Static CI must additionally compile the oracle/verifier, run `mc_workflow.py verify MC-013`, validate the programme contracts and confirm managed-issue zero drift before merge.
