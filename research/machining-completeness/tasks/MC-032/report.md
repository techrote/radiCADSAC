# MC-032 — Certified classification and critical-topology event engine

## Result

MC-032 is complete as bounded research/implementation evidence. It implements the event/classification ownership assigned by MC-026 without promoting MC-B or closing the inherited general transcendental/topology obligations.

The implementation has three deliberately separated routes:

1. **Exact algebraic classification (MC032-A/B).** Rational polynomial predicates are evaluated exactly. Multiplicity is obtained from exact derivatives and root exclusion uses the square-free Sturm sequence. A box/interval is assigned a sign only when exact evidence proves its open interval root-free and neither endpoint is an exact zero. Exact-zero boxes and boxes containing a root route to the critical-event path.
2. **Certified analytic evidence adapter (MC032-B).** MC-032 does not evaluate transcendental functions using binary floating point. It consumes only independently certified separated-interval evidence or unique transversal-root evidence with a strict positive derivative lower bound on the same source parameter. General tangential, multiple, or singular transcendental events remain `TRANSCENDENTAL_EVENT_BLOCKER / PB-007-01`.
3. **Critical-topology certificate boundary (MC032-C).** A topology event may be certified only from independently certified event evidence plus an independent connectivity certificate in the common workpiece frame. Positive-volume material semantics remain mandatory. Touching alone is not a material/body transition. Backend topology identifiers cannot become durable `body_id`/`lineage_id`, and MC-032 does not commit body transitions; that remains MC-033 ownership.

## Exact/boundary controls

`verify.py` exercises exact positive/negative predicates; exact zero; `±1/1000000` signed neighbours; simple roots; even-multiplicity tangency; odd-multiplicity crossing; singular multiple roots; exact endpoint roots; and square-free Sturm counting where a multiple root counts as one distinct critical event. The implementation rejects `float` values as correctness-authority rationals.

The analytic adapter has positive controls for separated intervals and unique transversal roots. Adversarial controls reject uncertified evidence, zero-containing intervals, nonpositive derivative lower bounds, mismatched/projected source parameters, and binary-float interval bounds. Resource/refinement exhaustion terminates as `RESOURCE_REFUSAL`, explicitly not as a truth value.

Topology controls distinguish exact touching from positive-volume material. They reject backend topology identity, reject positive-volume connectivity claims lacking an independent connectivity certificate with propagated `PB-007-04`, and accept only a bounded critical-event fact whose durable transition is still deferred to MC-033.

## Certificate/challenge binding

The event-certificate helper binds input digest, canonical-geometry digest, sweep digest, challenge identity, configuration digest, and the decision under canonical sorted JSON plus SHA-256. Mutation/staleness attacks are rejected.

MC-049 remains exactly the 64-record `PUBLIC_PRESELECTION_PREREGISTRATION` challenge set. MC-032 neither modifies it nor relabels it as secret/held-out evidence.

## Termination and nonclaims

The engine has only the finite terminal states `DECIDED`, `CERTIFIED`, `BLOCKED`, `UNCERTIFIED`, `RESOURCE_REFUSAL`, and `SEMANTIC_BLOCKER`. Epsilon, tolerance, binary float, refinement depth, timeout, resource exhaustion, provider cycles, and backend topology are not correctness authority.

MC-032 does **not** establish a universal exact transcendental tangency/multiplicity/singularity solver and therefore does not close `PB-007-01`. It does **not** establish universal 3-D topology/connectivity and therefore does not close propagated `PB-007-04`. Consequently PO-04/PO-07 are not globally discharged and MC-B remains `NOT_ESTABLISHED`.

## Protected semantics

No source/audio/provenance asset is changed. The canonical journal remains the durable source of intent; positive-volume material meaning, durable body/lineage identity, refusal semantics, and conventional STEP semantics are unchanged. No native or paid campaign is required or executed.

## Verification

- `python3 research/machining-completeness/tasks/MC-032/verify.py --self-test`
- `python3 research/machining-completeness/tasks/MC-032/verify.py --contract`
- `python3 tools/mc_workflow.py verify MC-032`
- `python3 tools/validate_machining_completeness.py --self-test`
- `python3 tools/mc_workflow.py sync --check`

The PR must also pass the repository `mc1-static` workflow on its exact head. After merge, that same required workflow must pass on the exact main merge SHA before issue #94 is closed.
