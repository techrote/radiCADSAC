# MC-038 / PB-007-01 — frozen V16 Chebyshev crossing under V43 refusal

**Date:** 29 October 2026. **Owner:** [MC-038 issue #100](https://github.com/techrote/radiCADSAC/issues/100). **Base:** 7158e8125457099fca37340b2a7afa869c0d814d (merged #289). **Evidence class:** one deterministic original-source classification only, not PB-007 general ordered composition, MC-B/MC-1, native, B-rep or engineering STEP acceptance.

## Frozen source and historical status

The 121-case v54 corpus Git blob 5841c331579489b25caef38cd412bdbf286f9134 records 11 V43 refusals. This investigation selects only composite:PB00701_V16_EXACT_CHEBYSHEV_STURM_MULTIPLIER:tail100, provenance verify_pb00701_v16. Its first physical source span [0,1] remains V16 CERTIFIED, second [1,2] remains V43 BLOCKED:CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED, and whole v54 source remains BLOCKED.

Original grammar: RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE; source parameter source-time-t on [0,2], phase turns s/4. The channels are continuous, clamped degree-1 B-splines joined at s=1. The checker requires every original coefficient, knot, physical source and phase field and re-lowers them with the pinned accepted exact degree-0/1 helper Git blob 2a8079ee2cf012bc2a12794c4c5ff19ebd760007, not a new surrogate owner.

On [1,2], set theta=pi*s/2. The exact source channels are C0=100(s-1), C1=40, C3=-50, C5=17, C7=1/3, S1=-260/3, S3=125/3, S5=-49/6, S7=-1/6. Chebyshev recurrence, retaining all 8 sine/cosine channels, gives

\[
F(s)=100(s-1)-\frac{2u+v}{3}P(z),\quad
u=-\cos\theta,\quad v=\sin\theta,\quad
z=u^2,\quad u^2+v^2=1,\quad u,v\geq0,
\]
\[
P(z)=32z^3+352z^2-782z+409.
\]

The executable reconstructs the full original polynomial arrays and checks the exact shared factor, not only sampled signal values.

## Exact positive multiplier and interval signs

With w=1-z in [0,1],

\[
P=11-18w+448w^2-32w^3
\geq11-18w+416w^2
\geq4495/416>0.
\]

P''(z)=192z+704>0; P'(7/8)=-185/2<0. Thus P decreases on [0,7/8]. Values: P(1/2)=110, P(3/4)=34, P(1)=11.

- On s in [1,5/4], z<1/2, P>=110, 2u+v>=1, bias<=25, hence F<=-35/3<0.
- On [5/4,3/2], z<=1/2, u>=sin(pi/8)>3/8, v>=sqrt(2)/2>7/10, P>=110, bias<=50. Hence F<-19/6<0.
- At s=3/2, F=50-55sqrt(2)<0.
- On [7/4,2], z>3/4; convexity gives P<=34, Cauchy-Schwarz gives 2u+v<=sqrt(5)<3, bias>=75. Hence F>41>0.

Eighth-angle bounds follow from rational-square comparisons (7/5<sqrt(2)<3/2 and sqrt(2)<23/16) and exact half-angle identities. No floating-point evidence or guessed root coordinates are used.

## Unique simple crossing, nonmonotone whole span

On [3/2,7/4], z is in [1/2,7/8), P>0 and P'<0, P<=110. For G=(2u+v)P(z)/3,

\[
G_\theta=\frac{(2v-u)P+(2u+v)2uvP'}3.
\]

Here 2v-u<=sqrt(2)/2<3/4, so G_theta<55/2. With pi<22/7,

\[
F'(s)=100-(\pi/2)G_\theta
>100-55\pi/4>795/14>0.
\]

Therefore the original source has **exactly one simple negative-to-positive physical crossing** strictly in (3/2,7/4), and complete negative and positive sign regions on either side. This bracket is source specific; no closed-form coordinate or generic ordered-root certificate is invented.

Exact endpoints: F(1)=-409/3 and F(2)=278/3. Derivatives F'(1)=100-409pi/3<0 and F'(2)=100+11pi/6>0. Therefore the full second span is genuinely nonmonotone, despite the unique crossing. A global-monotonicity hypothesis is false.

## Reproduction, falsifiers and limits

Run from a repository checkout:

~~~sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v43_v16_chebyshev_crossing.py --contract --self-test
~~~

The deterministic checker requires the frozen corpus/lowerer Git blobs, all 121 historical entries and 11 V43 refusals, original source/provenance/phase/knot/continuous channels, full Chebyshev coefficients, rational sign/derivative bounds, 26 required machining operations, MC-B/MC-1 NOT_ESTABLISHED and production authorization false. Adversarial mutations reject changed source or owner, spurious omitted crossing, weak derivative and sign claims, false bracket, added harmonics, false authority and capability promotion.

Falsifier: any changed original source, incorrect recurrence, nonstrict sign interval, wrong derivative inequality, changed historical status or weak source binding invalidates the candidate. This deterministic probe shares the accepted pinned lowerer and does not independently qualify an original-source codec, general V43 closed handoff, V27/V41 ordered child composition or full PB-007.

The 121 historical dispositions, all 26 machining operations, canonical journal, source/phase/provenance, material/body/lineage/refusal/UNCERTIFIED, reconstructed topology and conventional usable STEP obligations are unchanged. #275 stays closed; #100 and PB-007-01/02/03/04 stay open; MC-B/MC-1 are NOT_ESTABLISHED, production authorization false. No native/paid campaign, new issue or handoff promotion.

Required landing: exact-head focused and static CI, distinct current-head technical review with attribution, matching literal/synthetic Git trees, expected-head protected merge, actual merged-main focused/static PASS, issue #100 checkpoint. After this individual source, the higher-level V27/V41 ordered-child composition proof gap remains unresolved.
