# MC-054 — Engineering-output profile decision for singular and grouped material

Status: **completed profile/design research; output semantics decided, native/independent-consumer qualification still open; MC-C not established**  
Issue: #116  
Source baseline: `1b86aff77958dd1f0330f0a5aac9631a8ebef1b3`

## Question and falsification criterion

MC-054 resolves the product/profile choice that MC-016 deliberately left open: how should engineering output represent valid machining states that are empty, multi-body, exact-zero-contact, touching-cavity, or otherwise non-manifold without changing the material result merely to satisfy a B-rep writer?

The profile is rejected if it drops positive material, fuses durable bodies because boundaries touch, adds a positive bridge or wall at an exact-zero contact, lets kernel topology replace programme-owned body/lineage authority, treats an auxiliary decomposition seam as a physical material boundary, fabricates residual geometry for an empty state, or promotes source-level/native-unexecuted evidence into STEP interoperability.

## Reconciled authority

Formal artifact dependencies are MC-005, MC-016 and MC-017. MC-005 fixes the current domain/precision/request denominator and states that point/edge contact is not a volumetric connection, coincident/touching boundaries do not merge durable bodies, positive-volume remnants remain material and whole-body removal is valid. MC-016 records the representability obstructions and leaves RB-016-01 through RB-016-05 open. MC-017 identifies a credible independent BRL-CAD/STEPcode/OpenNURBS consumer route but explicitly does not claim measured interoperability.

No historical `research/rcs-*` evidence is rewritten. No new native or paid campaign is run. The engineering representation remains derived from the canonical material/body result; it does not become a new authority source.

## Standards facts used

The profile uses two narrow STEP source facts already compatible with MC-016's screen. `advanced_brep_shape_representation` permits manifold-solid and mapped items and requires at least one solid-bearing item; it is not restricted to exactly one manifold solid. `manifold_solid_brep` carries one outer closed shell. These facts support a multiple-manifold-item route for nonempty grouped output, but they do not prove that any producer/consumer preserves the intended grouping, identity or contact semantics.

References:

- https://www.steptools.com/stds/stp_aim/html/t_advanced_brep_shape_representation.html
- https://www.steptools.com/docs/stp_aim/html/t_manifold_solid_brep.html

## MC-ENG-OUTPUT/1.0 decision

MC-054 establishes the versioned profile `MC-ENG-OUTPUT/1.0`.

Every engineering-output package has a mandatory `engineering-output-manifest.json`. The manifest binds the derived geometry to the exact material certificate and durable-body/lineage record. STEP topology, object names, nearest geometry, largest-volume selection and kernel handles are never allowed to define durable identity.

For ordinary regular nonempty material, the primary engineering geometry remains advanced B-rep STEP. Enclosed disjoint cavities continue to use the MC-016 `BREP_WITH_VOIDS` route when qualified. Positive micro-features remain ordinary material: the writer may not erase them because they are inconvenient relative to a sewing or modelling tolerance.

For multiple disconnected positive-volume durable bodies, every retained body is emitted as a distinct manifold-solid item or distinct STEP artifact under one manifest. There is no “keep largest” escape. The manifest records a one-to-one binding from emitted body-level geometry to the canonical durable-body/lineage authority.

For exact-zero contact between already-distinct durable bodies, the bodies remain distinct. Their contact is recorded as a source-certificate-bound exact-zero contact relation in the manifest. The producer may not add a bridge, fuse the solids, or let sewing tolerance create a new body relationship.

For a valid singular/touching state that cannot be represented faithfully by one manifold solid, the approved route is a **certified grouped decomposition**. The canonical material assigned to a durable body may be covered by a finite set of regular positive-volume manifold representation pieces whose interiors are pairwise disjoint and whose certified union equals the canonical material set. Each piece carries the same durable-body/lineage binding. Any additional partition face exists only to make the derived engineering representation regular and is labelled `NON_MATERIAL_PARTITION`; it is not a new physical boundary and may not alter canonical body identity.

This explicit decision is the only circumstance in this profile in which auxiliary internal partition faces may appear. They must be certificate-backed, they must not add or remove material, and a downstream consumer that treats them as physical manufacturing semantics fails the profile.

## Empty-material contract

A valid completely exhausted workpiece is represented by the manifest state `EMPTY_MATERIAL`, an empty `step_artifacts` list and an empty `representation_pieces` list. The exhausted/disappeared durable-body and lineage transitions remain in the manifest.

No epsilon solid, dummy cube, empty placeholder STEP counted as a nonempty success, or fabricated residual shell is permitted. For the geometry consumer path, the empty state is `NOT_APPLICABLE_EMPTY`; a follow-on geometric operation must return `EMPTY_NO_GEOMETRY`. This is a successful explicit engineering-output state, not a failed attempt to manufacture a fake solid.

The STEP source fact that an advanced B-rep representation requires at least one solid-bearing item is therefore not treated as a reason to invent geometry. The product profile branches before STEP generation when the canonical material is empty.

## Independent-consumer evidence plan

MC-054 decides semantics but does not execute the qualification campaign. Nonempty qualification remains routed through MC-017's pinned strict BRL-CAD `step-g` path under MC-043: exact STEP bytes, strict/exact/no-repair import, complete accounting of every expected item/piece, body/lineage binding without nearest-geometry or largest-body heuristics, and a downstream operation that actually consumes the imported geometry.

Required controls include a conventional known-good solid, a known-bad/incomplete STEP, the valid-but-materially-wrong negative class, a multi-body exact-zero-contact case, a grouped singular decomposition case, a positive micro-feature boundary case and the manifest-only empty state. The empty control must prove that the harness does not invoke STEP import and does not fabricate geometry.

The existing MC-045 campaign harness remains the execution mechanism once a native permit exists. MC-054 itself does not authorize expenditure or native work.

## Blocker reconciliation

MC-054 resolves the **profile-decision portion** of RB-016-04 and RB-016-05, but does not close either blocker because their required native/downstream evidence does not exist yet.

- **RB-016-01 — OPEN:** cavity output still lacks qualifying native `BREP_WITH_VOIDS` plus independent-consumer evidence.
- **RB-016-02 — OPEN:** the multi-body mapping is now specified by `MC-ENG-OUTPUT/1.0`, but native STEP and independent-consumer preservation of every durable-body/lineage binding remain unqualified.
- **RB-016-03 — OPEN:** positive micro-feature preservation remains unqualified at the engineering-output/consumer boundary.
- **RB-016-04 — OPEN:** singular/contact semantics are now decided, but grouped/singular native STEP and independent-consumer evidence remain outstanding.
- **RB-016-05 — OPEN:** empty output semantics are now decided, but downstream manifest-only empty handling remains unqualified.
- **XB-017-01 — OPEN:** actual source-bound independent-consumer execution remains owned by MC-043 under an authorized native campaign.

No duplicate blocker is created.

## Adversarial and boundary controls

The deterministic verifier rejects, among other corruptions: making STEP topology authoritative for body identity; omitting the mandatory manifest; keeping only the largest body; fusing exact-zero-contact bodies; inserting a positive bridge; permitting a grouped-decomposition piece outside the canonical material; treating an auxiliary seam as material; erasing a protected positive micro-feature; emitting placeholder STEP or epsilon material for `EMPTY_MATERIAL`; dropping exhausted lineage; closing inherited blockers without evidence; or promoting MC-C.

The boundary rules are non-compensating: positive material remains positive, exact zero remains exact zero, distinct durable bodies stay distinct, grouped pieces cannot silently become bodies, and empty remains empty.

## Result

MC-054 is suitable for `COMPLETED_RESEARCH`. The required product/profile choice is explicit, versioned, machine-readable and independently testable. Every changed output rule states material and identity semantics plus a concrete consumer evidence plan.

This task does **not** establish engineering-output interoperability. No native or paid campaign ran. MC-C remains **NOT_ESTABLISHED**, as do MC-B, MC-D, MC-E, MC-F and MC-1. The accepted result is the profile decision itself; the inherited representability/consumer blockers remain open until their recorded native and independent-consumer evidence genuinely exists.
