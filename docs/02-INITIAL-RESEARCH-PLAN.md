# Initial research plan

Status: superseded by reviewed plan in `04-REVISED-RESEARCH-ROADMAP.md`  
Purpose: preserve the first coherent planning sequence before critique.

## Initial sequence

The first pass proposed a mostly linear programme:

1. Freeze the MSAC geometry contract.
2. Define OpenSimachinist requirements/invariants.
3. Audit OCCT architecture and identify fork points.
4. Define adversarial manufacturing geometry fixtures.
5. Specify a baseline benchmark/validation harness.
6. Research tolerance models and virtual tolerances.
7. Research provenance/bookkeeping.
8. Research deferred topology and regularized solids.
9. Research a lathe-specialized geometry path.
10. Research a mill/swept-removal geometry path.
11. Research hybrid implicit/B-rep/mesh representations.
12. Define STEP export/conformance requirements.
13. Synthesize an OpenSimachinist founding architecture.
14. Synthesize an MSAC founding architecture.
15. Freeze clean handoffs and create the production repositories.

## Why this was initially attractive

- It appeared to make dependencies explicit.
- It prevented implementation before requirements existed.
- It put the MSAC↔backend boundary before kernel surgery.
- It reserved process-specific solvers rather than assuming generic Booleans.
- It ended with clean handoffs rather than turning the planning repo into a permanent monorepo.

## Initial architecture hypothesis

The first working hypothesis was:

- start from OCCT because it already provides industrial B-rep and STEP infrastructure;
- retain or adapt the parts that work;
- radically alter tolerance, Boolean/topology and bookkeeping machinery where manufacturing workloads demand it;
- expose none of OCCT's private model through the stable MSAC contract;
- supplement generic geometry with lathe/mill-specific solvers;
- permit internal hybrid representations but reconcile to conventional valid STEP.

## Initial research hypotheses

### H1 — semantics beat anonymous Booleans

Manufacturing-process semantics can avoid or disambiguate cases that a general `A - B` solid Boolean sees only as coincident/tangent geometry.

### H2 — tolerance is multidimensional

Separating manufacturing, numerical, topological, contact and export tolerances will be more robust than propagating a single epsilon.

### H3 — provenance can resolve ambiguity

Knowing that a face/path was deliberately produced by a finishing pass or specific tool can resolve some coincidence decisions more safely than geometric proximity alone.

### H4 — deferred topology reduces failure

Not materializing every lower-dimensional topological event immediately may prevent intermediate sliver/zero-thickness states from destabilizing later operations.

### H5 — batching beats sample-by-sample subtraction

Canonicalized cutter trajectories and swept-removal batches should produce fewer topology events and better robustness/performance than one subtraction per controller sample.

### H6 — process-specific reduction is high leverage

Lathe operations in particular may often reduce to robust 2D material-domain operations followed by reconstruction/revolution, avoiding most general 3D Boolean pathology.

### H7 — hybrid representations provide escape routes

Some operations may be best represented temporarily using implicit, volumetric, cell-complex or robust manifold-mesh techniques before returning to analytic/B-rep geometry.

### H8 — operation journals future-proof saved work

A stable canonical manufacturing history lets future kernels regenerate old workpieces and lets research compare competing solvers on identical user intent.

## Initial success condition

The research phase would be considered ready to hand off when it could provide:

- a stable MSAC↔OpenSimachinist contract;
- a versioned operation-journal concept;
- measured baseline behaviour on adversarial fixtures;
- evidence for the chosen tolerance/provenance/topology approach;
- at least one credible lathe strategy and one credible mill strategy;
- a defensible STEP conformance specification;
- a clean OpenSimachinist founding plan;
- a clean MSAC founding plan.

This initial plan is preserved for historical comparison. The next document records the critique that materially changed it.
