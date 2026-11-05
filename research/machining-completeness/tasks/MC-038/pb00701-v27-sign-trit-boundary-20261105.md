# MC-038 / PB-007-01 — frozen V27 original-pair endpoint/knot sign information-loss witness

**5 November 2026 · Bounded C falsification · DETERMINISTIC_MODEL only.** This challenges a *proposed* lossy interface, not an accepted solver: KNOT_ENDPOINT_SIGN_TRITS_PLUS_PHASE_SECTORS_DETERMINE_INTERIOR_PHYSICAL_SIGN_CELLS. An interface exporting only physical sign trits at original endpoints and true knots, their coordinates, and a shared phase law cannot reconstruct all interior physical signs. The conclusion does not invalidate richer ordered-root certificates, or establish general analytic-event undecidability.

## Source custody and admitted grammar

The immutable original v54 corpus is Git blob 5841c331579489b25caef38cd412bdbf286f9134; v2 fifty-original complete-evidence register is blob e52d3baf3692a011cf86234eeaa992ef407d99fd. Both selected originals have source-time t in [0,2], true spline knot t=1, phase turns 1/2−2t/3, degree-zero cosine H2=1/100, degree-one sine H1, and the following exact SHA-256 pins.

| Historical case ID suffix | Original source | Original whole row |
|---|---|---|
| composite:PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION:tail0 | bdefb90689be6c6e29ffcd77611c40add0ee7d05099e94e3916174b6f74048dd | ec76b07111b15331c2d509b04c66ee209b5ec0a5c508accbf77eabb99454b0ca |
| composite:PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION:tail100 | 64b130ec50dbe5ae8a8eb2d2335c4a08d2c652f7e458b0bb88ff2b941603a23a | a76882b242c1ff03924ea96aa4290ade41b6dc9d6599c0bec06a537eb5c02260 |

Both historically had BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE, and both **already** have COMPLETE_SOURCE_SPECIFIC original-source witnesses in the v2 register. This finding does not close either one anew.

## Original physical function

Let \(\phi=4\pi t/3\). The actual common phase angle is \(\theta=\pi-\phi\), hence \(\sin\theta=\sin\phi\), \(\cos(2\theta)=\cos(2\phi)\). Exact clamped B-spline span extraction gives S1=2+4t on [0,1], S1=6 on [1,2], C2=1/100 everywhere. The two original physical functions are identical on the first span:

\[
F_L(t)=5+(2+4t)\sin\phi+\frac1{100}\cos(2\phi).
\]

The second-span functions differ by a real source H0 ramp, not a forged event:

\[
F_0(t)=5+6\sin\phi+\frac1{100}\cos(2\phi),\qquad
F_{100}(t)=F_0(t)+100(t-1).
\]

At the original source endpoints and true knot, both originals have exactly the same sign sequence **(+,-,+)**:

| Source t | Exact tail0 value | Exact tail100 value | Both signs |
|---|---|---|---|
| 0 | 501/100 | 501/100 | + |
| 1 | 999/200−3√3 | 999/200−3√3 | − |
| 2 | 999/200+3√3 | 20999/200+3√3 | + |

The middle value is negative because √3 > 5/3, a rational-square comparison. At the *same interior rational source coordinate* t=9/8, however,

\[
 F_0(9/8)=-101/100<0,\qquad
 F_{100}(9/8)=1149/100>0.
\]

Therefore identical endpoint/knot sign trits, knot coordinates and phase law **cannot** determine the correct interior sign in both of these genuine frozen originals. This falsifies exactly the proposed information-loss interface, not V27 or general analytic root solving.

## Exact full sign/root/order argument for the admitted originals

At t=3/4 both sources equal 501/100 >0; at t=1 both are negative. On (3/4,1), sinφ<0, cosφ<0, sin(2φ)>0 and 2+4t>0. Thus

\[
F'_L=4\sin\phi+(2+4t)\frac{4\pi}{3}\cos\phi-\frac{2\pi}{75}\sin(2\phi)<0.
\]

There is **exactly one simple positive-to-negative crossing** in (3/4,1). On [0,3/4], sinφ≥0 and cos(2φ)/100≥−1/100, hence F≥499/100>0.

For tail0, derivative is strictly negative on (1,9/8) because cosφ<0 and sin(2φ)>0, then strictly positive on (9/8,3/2) because cosφ>0 and sin(2φ)<0. Since F0(9/8)=−101/100 and F0(3/2)=501/100, there is exactly one **simple negative-to-positive crossing** in (9/8,3/2). On [3/2,2], sinφ≥0 so F0≥499/100. The two crossings are exhaustive.

For tail100, its derivative everywhere on (1,2) satisfies the strict rational bound (π<22/7):

\[
F'_{100}=100+8\pi\cos\phi-\frac{2\pi}{75}\sin(2\phi)
>100-\left(8+\frac{2}{75}\right)\frac{22}{7}
=\frac{5608}{75}>0.
\]

Its second simple crossing is therefore uniquely within (1,9/8), because F100(1)<0<F100(9/8). Each whole original has **two** distinct simple roots of order 1, parity odd, crossing physical signs (+,-,+), no zero source endpoint, no zero knot, no even/tangential root and no identity-zero interval. The proven strict interval signs and derivatives exclude unlisted roots without a numerical scan, refinement cutoff or timeout.

## Deterministic verifier, refusals, and retained blockers

The executable checks literal Git blob pins for all 121 historical originals and all 50 v2 witness records, each unique ID, canonical original SHA, whole-row SHA, origin, interval, phase and disposition. It reads the actual two source specifications, checks exact original rational B-spline control identities, computes the rational-angle values as Q+Q√3 without floating point, and checks the strict rational derivative margin and unchanged census. Mutations of phase, parameter, source knot, control, harmonic, identity-zero claim, forged root location, fabricated historical closure and false native-evidence classification must refuse. Repeated/tangential, identity-zero or extremely close *prospective* sources are outside this **exactly two-source** theorem; the checker does not falsely admit them.

Historical counts **before = after**: 121 original sources, 20 historic route refusals, 30 missing ordered-premise cases, and 50 already complete v2 source-specific witnesses (49 finite, one continuum); **every delta 0 and no newly closed IDs**.

Required PB-007-01/02/03/04 and PO-02/04/05/07/08 remain OPEN; MC-B and MC-1 remain NOT_ESTABLISHED. This does not qualify native geometry, topology, source journal/body lineage, independent engineering STEP or production, and all **26** supported operations remain required.

## Reproduce and critical path

Run these from the repository root in a complete checkout:

    python3 research/machining-completeness/tasks/MC-038/pb00701_v27_sign_trit_boundary_20261105.py --contract --self-test
    python3 research/machining-completeness/tasks/MC-038/test_pb00701_v27_sign_trit_boundary_20261105.py
    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
    python3 tools/validate_machining_completeness.py

Next develop a total, fail-closed V27 *ordered interior-root/sign certificate consumer*, retaining original source amplitude coefficients rather than relying on exterior/knot trits. Independently qualify actual required proof grammar before any PB discharge. This file is isolated from open drafts #392/#397, the separately owned V13–V15 theorem, issue #100 comment reservation and shared proof/programme/77 registries.
