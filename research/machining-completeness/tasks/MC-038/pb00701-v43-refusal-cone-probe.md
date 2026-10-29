# MC-038 / PB-007-01 — exact source-bound V43 refusal sign probes

**29 October 2026 | DETERMINISTIC_MODEL | research only | issue #100**

Frozen evidence: pb00701-finite-owner-corpus-v54.json at Git blob 5841c331579489b25caef38cd412bdbf286f9134. Base main d672bc2d57b90345184dfff63e69029effc8163f. The 121-case v54 archive records eleven V43 CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED span refusals: one harvested and ten manufactured composites. A refused sufficient derivative certificate does not demonstrate either a physical root or mathematical nonmonotonicity.

## Hypothesis

Two exactly pinned V43-refused physical spans nevertheless have strictly positive source functions, proved directly from original rational B-spline controls and exact trigonometric quadrant inequalities. Falsifiers: altered source identity, harmonic inventory, source knot/control/degree, phase law, historical V43 owner/refusal, knot continuity or sign margin. No historical selecting route, numerical trigonometry or unbounded general solver is admitted.

## Harvested case H

ID harvested:verify_pb00701_v9:4e7b85fa122a; original parameter source-time-t; s in [0,1], phase turns s/8, harmonic h=1. Independent clamped linear source lowering gives C1(s)=1, S1(s)=s-1/2 and

\[
F_H(s)=\cos(\pi s/4)+(s-1/2)\sin(\pi s/4).
\]

Since theta in [0,pi/4], cos(theta) >= sqrt(1/2) > 2/3 and 0 <= sin(theta) <= sqrt(1/2) < 3/4. Exact comparisons: (2/3)^2 < 1/2 < (3/4)^2. Because |s-1/2| <= 1/2, the entire **closed source span** satisfies

\[
F_H(s) > 2/3 - (1/2)(3/4)=7/24>0.
\]

The original v54 V43 disposition remains BLOCKED.

## Manufactured tail100 case T

ID composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail100. The first source span [0,1] was historically V9 CERTIFIED. The **second span [1,2] is V43 BLOCKED**. Its exact original degree-zero/one clamped source B-splines yield C0(s)=100(s-1), C1(s)=1/2, S1(s)=1, phase turns s/8. Thus

\[
F_T(s)=100(s-1)+\frac12\cos(\pi s/4)+\sin(\pi s/4).
\]

On s in [1,2], theta in [pi/4,pi/2], with 100(s-1)>=0, cos(theta)>=0, sin(theta)>=sqrt(1/2)>2/3. Hence **F_T(s)>2/3** throughout the closed V43-refused second span. The verifier checks all channel controls, exact affine lowering and continuity at original source knot s=1. No claim is made about whole-source composition or the first-span root count beyond historical authority.

## Distinct derivative outcomes — exact source-specific conclusion

The same two source-bound functions have **different derivative behaviour**. Differentiating their already checked exact forms (with k=pi/4):

- Harvested: \(F'_H(s)=(1-k)\sin(ks)+k(s-1/2)\cos(ks)\).
  At s=0, \(F'_H(0)=-\pi/8<0\). At s=1,
  \(F'_H(1)=\sqrt{1/2}(1-\pi/8)>0\), since the classical exact rational bound \(3<\pi<22/7<8\) holds. The smooth source therefore has at least one interior local minimum and is **not monotone**, despite having no zeros. Here the failure of a strict complete-derivative V43 certificate is mathematically unsurprising; it cannot be repaired by an alternative bound asserting a globally strict derivative sign.

- Composite tail: \(F'_T(s)=100-(\pi/8)\sin(ks)+(\pi/4)\cos(ks)\).
  On s in [1,2], \(0\le\sin(ks)\le1\), \(\cos(ks)\ge0\), and \(0<\pi<22/7\). Hence
  \[
  F'_T(s)>100-(22/7)/8=\frac{2789}{28}>0.
  \]
  This **refused source child actually is strictly increasing**, so its historical V43 refusal represents insufficient authority of that particular sufficient certificate, not mathematical nonmonotonicity. The proof remains exclusive to this fixed original span.

Together these distinguish a physically nonmonotone but root-free V43 refusal from a strictly monotone, root-free V43 refusal without mislabelling either historical result. The verifier's exact rational controls check the two endpoint derivative signs, the tail derivative margin and the original source/phase identities; the analytic quadrant and classical pi inequalities are explicitly stated proof assumptions, not numeric sampling.

## Verification and limits

Run: python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v43_refusal_cone.py --contract --self-test

The verifier pins the entire frozen corpus, checks the 11 historical V43 refusals and both exact sources, derives rational margins and rejects source/phase/continuity/refusal mutations. Authority, MC-B and the 26-operation domain remain unchanged. These source-specific bounds separate actual harvested nonmonotonicity from the strictly increasing composite tail. They **do not** establish a general V43 theorem, certify a new whole-source ordered event view, resolve the other nine refusals, or modify the historical v54 corpus/43-owner table. V27/V41 child composition, general analytic zero isolation, material/body/lineage/journal/UNCERTIFIED and conventional STEP obligations all remain open.

A distinct source/proof review is required before accepting even this bounded research. No successor issue, MC-B/MC-1/native/B-rep/STEP promotion, expensive run or production authorization. PB-007-01/02/03/04 stay OPEN; MC-B/MC-1 stay NOT_ESTABLISHED.
