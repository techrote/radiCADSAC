# MC-038 / PB-007-01 — exact V11 source-bound V43-refused tail contrast

**Date:** 29 October 2026. **Evidence class:** deterministic exact-source mathematical research only. **Parent:** [MC-038 / issue #100](https://github.com/techrote/radiCADSAC/issues/100). **Starting main:** a1b600a687a7c626bccb3f0a81bca7762edacfd7 (after reviewed/merged V12 PR #286). **Disposition:** research candidate, not a new general V43 theorem or v54 integration.

## Exact custody and frozen denominator

The original 121-case v54 source corpus is pinned by Git blob 5841c331579489b25caef38cd412bdbf286f9134. The accepted exact degree-0/1 source helper from V43 PR #283 is pinned by Git blob 2a8079ee2cf012bc2a12794c4c5ff19ebd760007. A small independent exact clamped degree-2 Bernstein expansion is added locally because V11's first harmonic is quadratic and the historical V43 helper supports only degrees 0/1. Neither original V11/V43 implementation nor any historical evidence is changed.

The two source records are **exactly**:

- composite:PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO:tail0;
- composite:PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO:tail100.

Each retains the historical first-span PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO CERTIFIED, second-span PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF BLOCKED:CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED, and whole-source v54 BLOCKED. They are two of **11** V43 refusals (one harvested, ten manufactured) in the original 121-case corpus.

The original source parameter is source-time-t on [0,2]; phase turns are exactly 2s (zero offset). The cosine first harmonic is the clamped quadratic with Bernstein controls (1/8,-3/8,1/8) on [0,1], (1/8,1/8,1/8) on [1,2]. Exact lowering yields s²-s+1/8 on the first piece and constant 1/8 on the second, with value 1/8 on both sides of the physical knot. The sine first harmonic equals 1 on both pieces. The harmonic-zero cosine is identically zero in tail0 and equals 100(s-1) on the second piece of tail100, with a continuous original knot.

## Second physical source span [1,2]

Let \(\theta(s)=4\pi s\), so the source covers two complete phases, from \(4\pi\) to \(8\pi\). The shared oscillatory component is

\[
g(s)=\tfrac18\cos(4\pi s)+\sin(4\pi s).
\]

**Tail0 — exactly four distinct simple physical crossings.** At source points 1,5/4,3/2,7/4,2 the exact values alternate +1/8,-1/8,+1/8,-1/8,+1/8. With \(\alpha=\arctan(1/8)\in(0,\pi/4)\), the four and only four roots in (1,2) satisfy

\[
s_k=1+\frac{k+1}{4}-\frac{\arctan(1/8)}{4\pi},
\qquad k=0,1,2,3.
\]

Within each successive half-cycle, the tan equation \(\tan\theta=-1/8\) has exactly one solution; \(\cos\theta=0\) is not a zero. Differentiation at these exact implicit roots gives

\[
g'(s_k)=(-1)^{k+1}\frac{\pi\sqrt{65}}2\ne 0.
\]

Thus all four crossings are simple, with successive sign cells POSITIVE, NEGATIVE, POSITIVE, NEGATIVE, POSITIVE. None of the source roots is claimed to have a rational or algebraic coordinate.

The strict rational source bracket for root \(k\) is
\[
\left(1+\frac{k+1}4-\frac1{16},\
      1+\frac{k+1}4-\frac1{128}\right).
\]
The upper displacement bound follows from \(\alpha<\pi/4\); the lower follows from \(\alpha>\frac18-\frac1{3\cdot8^3}=\frac{191}{1536}>\frac1{10}\), \(\pi<22/7\), hence \(\alpha/(4\pi)>7/880>1/128\). The phase crosses tan-half poles. Therefore **no pole-free V6 certification or general cross-pole ordered-root owner authority is asserted**.

**Tail100 — strictly positive, strictly increasing, zero roots.** The exact original second-span source is

\[
F_{100}(s)=100(s-1)+g(s).
\]

The derivative satisfies
\[
F_{100}'(s)=100+4\pi\left(\cos(4\pi s)-\tfrac18\sin(4\pi s)\right)
>100-\tfrac92\cdot\tfrac{22}{7}=\frac{601}{7}>0.
\]
As \(F_{100}(1)=1/8>0\), this proves positivity over the closed source span and no physical roots. \(F_{100}(2)=801/8\).

## Verification and falsification

Run:

~~~sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v43_v11_tail_contrast.py --contract --self-test
~~~

The verifier checks source/knot/affine phase identity and two exact clamped Bézier polynomials; preserved V11 first-span/V43 second-span owner tags; 121 frozen cases and 11 historical V43 refusals; exact root order, alternating signs, four strict rational isolating brackets, derivative bounds and signed no-root contrast. Adversarial mutations include changed original controls, quadratic clamped knots, phase, provenance, harmonic inventory, source ID, historical disposition, duplicated/omitted root, forged bracket/sign/margin, and capability promotion. It checks the 26-operation domain and NOT_ESTABLISHED programme/production authority.

The verifier shares a pinned degree-0/1 source helper; it is not fully mathematically independent of historical source-normalization assumptions. The certificate checker is deliberately restricted to exact replay of these two immutable originals, not a universal oracle.

## Review/landing gates and explicit nonclaims

A distinct AI-assisted technical review (clearly attributed) of the final exact head, focused CI and mc1-static on the exact head, literal/synthetic tree comparison, expected-head-protected merge and merged-main verification are required before any landing. Negative CI is retained, not reported as success. #275 stays closed/completed; issue #100 and PB-007-01/02/03/04 remain open. All historical v54 dispositions, 43-owner inventory, task graph, gate/outcome, current authority and source records stay read-only.

These two case-specific proofs do **not** establish general V43 correlation/closed-handoff authority, V27/V41 child composition, original-source knot composition, PB-007-01, MC-B, MC-1, native material/topology/B-rep/STEP capability, or production authorization. All 26 required operations, physical source/provenance/phase, canonical journal, positive material, durable bodies/lineage, typed refusal and UNCERTIFIED, and conventional usable engineering STEP obligations remain in force.
