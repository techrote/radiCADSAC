# MC-038 / PB-007-01 — frozen V12 V43-refused tail contrast

**Date:** 29 October 2026. **Status:** draft, source-bound exact research. **Parent:** [issue #100](https://github.com/techrote/radiCADSAC/issues/100). **Base:** 16f77a14f806566047fb42a21830dae43cc7af0f. **Evidence class:** deterministic exact-arithmetic/analytic model, not native geometry.

## Target and evidence custody

The frozen [v54 original-source corpus](pb00701-finite-owner-corpus-v54.json), Git blob 5841c331579489b25caef38cd412bdbf286f9134, contains 121 cases and 11 historical PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF refusals (one harvested, ten composite). Two selected cases are:

- composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail0
- composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail100

Both remain historically BLOCKED: V12 certifies original first span [0,1]; V43 refuses second [1,2] with CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED. This study does not revise the frozen dispositions, promote the first span to whole-source composition, or establish a general V43 owner premise.

The independently pinned [accepted original-source linear B-spline lowerer](verify_pb00701_v43_refusal_cone.py), Git blob 2a8079ee2cf012bc2a12794c4c5ff19ebd760007, checks all original channels, original physical knot continuity and exact phase source identity. On [1,2], both have C1=2/3, S1=-1/3 and phase turns t(s)=s/4. The harmonic-zero source coefficient is C0=0 for tail0, and C0=100(s-1) for tail100. Let theta=pi*s/2 and g(s)=(2/3)*cos(theta)-(1/3)*sin(theta). Their actual source functions are F0=g and F100=100(s-1)+g.

## Falsifiable contrast

**Hypothesis A:** F0 is root-free and truly nonmonotone. On [1,2], theta belongs to [pi/2,pi], where cos(theta)<=0, sin(theta)>=0, and the two are never simultaneously zero. Thus g(s)<0 on the whole closed span; g(1)=-1/3 and g(2)=-2/3. Exactly zero open roots exist and one complete negative sign cell applies.

The derivative is g'(s)=-(pi/3)*sin(theta)-(pi/6)*cos(theta), with g'(1)=-pi/3<0 and g'(2)=+pi/6>0. Its continuity implies at least one interior turning point; no exact count of derivative zeros is claimed.

**Hypothesis B:** F100 has one simple negative-to-positive crossing and is strictly increasing. For all s in [1,2], |sin(theta)|<=1, |cos(theta)|<=1, and pi<22/7 imply

F100'(s) >= 100-pi/2 > 100-11/7 = 689/7 > 0.

F100(1)=-1/3 and F100(2)=298/3. For s=101/100, delta=pi/200 in (0,pi/2), and sin(delta)<delta, cos(delta)<=1 imply

F100(101/100)=1-(2/3)*sin(delta)-(1/3)*cos(delta) > 2/3-pi/300 > 689/1050 > 0.

Thus the unique root lies in the strict physical source bracket (1,101/100), with multiplicity one and negative-to-positive sign change. No rational or algebraic source coordinate or closed form is asserted; the root is the unique preimage of the exact source equation.

## Implementation, negative controls and review

Run the [source-bound verifier](verify_pb00701_v43_v12_tail_contrast.py) with:

    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v43_v12_tail_contrast.py --contract --self-test

It pins the v54 corpus, prior lowerer, original source harmonic inventory, controls, knots, continuity, shared source parameter, affine phase, V12/V43 ownership and both historical refusals. Adversarial mutations change each source's controls, phase, knot, source identity, historical owner and disposition, or alter report root counts, derivative bound, bracket, sign orientation or promotion fields. All must refuse. Report validation is deterministic replay of this same bounded construction, not an independent general analytic proof checker.

The dedicated [focused workflow](https://github.com/techrote/radiCADSAC/blob/main/.github/workflows/mc1-pb00701-v43-v12-tail-contrast.yml) is required alongside mc1-static. Source-matched verification, distinct final-head technical review, exact tree identity, expected-head-protected merge and merged-main CI are landing gates; draft status alone confers no acceptance.

## Explicit nonclaims

No historical V6–V54 route/evidence, 43-owner inventory, MC-038 gate/outcome, task graph or authority is modified. The machining domain retains all 26 required operations. PB-007-01/02/03/04 and original-source codec, canonical journal, phase/provenance, material/body/lineage/topology/connectivity, refusal/UNCERTIFIED, native B-rep and conventional usable STEP obligations remain open. MC-B/MC-1 remain NOT_ESTABLISHED; production authorization remains false. This pair does not establish universal V43 correlated closed handoff, V27/V41 child composition or usable engineering geometry.
