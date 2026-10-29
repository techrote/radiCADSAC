# MC-038 / PB-007-01 — source-knot zero completeness research

Status: **bounded deterministic-model research candidate**  
Date: 2026-10-29  
Issue: #100  
Preselection: https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6510971493

## Purpose and scope

This investigation asks one narrow question left open after the synthetic multi-root
whole-span result in PR #304: when two exact source spans meet at one rational
real-source knot that is itself a zero, can the shared boundary event be proved
complete without double-counting it or inventing a global smooth multiplicity?

The admitted source grammar remains the exact rational-polynomial-modulated
finite-harmonic affine-phase grammar already reviewed for PB-007-01. This work
does **not** adapt or admit a frozen historical V27/V41 child owner.

## Hypothesis

For two source-bound spans meeting at one exact rational source coordinate, the
whole two-span union contains exactly one physical zero at the knot when all of
the following are checked:

1. the original source parameter, phase and knot coordinate agree;
2. the #298 cyclotomic/π-transcendence checker proves exact continuity and an
   exact zero on both sides, with finite nonzero one-sided derivative jets;
3. the left and right one-sided smooth orders are retained separately;
4. a global rational bound on the next derivative keeps the first nonzero
   derivative strictly signed throughout a left and right knot guard;
5. Taylor's theorem therefore excludes any other zero inside either knot guard;
6. complete strict-sign dyadic covers exclude every zero in both outer regions;
7. one global node budget covers both outer proofs; and
8. the shared boundary event is counted once.

Failure of any premise is nontruth/refusal, not a root count.

## Decisive positive fixtures

The verifier uses two independently specified source records with common phase
turns `s` and exact knot `s=1`.

Left span on `[0,1]`:

`F_L(s)=(s-1)^2(1+sin(2πs)/2^20)`.

Right crossing span on `[1,2]`:

`F_R(s)=-(s-1)^3(1+sin(2πs)/2^20)`.

The left one-sided order is 2 and the right one-sided order is 3. The physical
signs are positive to negative, so the shared event is a crossing. Negating the
right span gives the same separate orders but positive-to-positive signs, hence
a distinct touching result. In neither case is a global smooth multiplicity
claimed.

## Completeness argument

The exact point checker establishes the zero and derivative order at the shared
knot, but point evidence alone is insufficient.

For each side, the reviewed PR #303 derivative-envelope primitive supplies a
global rational bound on `|F^(m+1)|`. Widening the exact enclosure of
`F^m(knot)` by that bound times guard width must remain strictly signed across
the entire one-sided guard. Because all lower derivatives vanish at the knot,
Taylor's integral remainder proves the only zero in that guard is its knot
endpoint.

The remaining outer interval on each source is then exhaustively partitioned
into closed dyadic cells. Every accepted cell has one rigorous strict-sign value
enclosure after widening by a global `|F'|` bound. The two outer covers plus
the two one-sided knot guards tile the complete two-span union without gaps.
The implementation passes the **remaining** node allowance to the second cover,
so the declared node budget is global rather than per-side.

## Falsifiers and negative controls

The adversarial verifier rejects or refuses:

- a discontinuous source knot;
- mismatched source coordinate or phase;
- a nonzero shared knot;
- an identity-zero source whose finite jet cap cannot establish a first nonzero
  derivative;
- changed one-sided order/sign/event claims;
- noncanonical exact-rational inputs;
- source mutation followed by reuse of an old report;
- forged cover hashes, counts or capability fields;
- node/depth/jet-order exhaustion; and
- two omitted remote tangencies with unchanged positive endpoint signs, using
  `(s-1)^2(1+cos(4πs))` on the left span. Endpoint signs therefore cannot
  substitute for complete root-free coverage.

Unknown, undecided and resource-exhausted cases remain typed nontruth.

## Source custody

The new checker pins the reviewed source blobs:

- `pb00701_jet_guarded_nontransverse.py`:
  `37c0271852e1468aa5ecfa9078d6f950841e4194`;
- `pb00701_rational_phase_point.py`:
  `9fc344e045fa800fb24d30902a641e534a1e197b`;
- `pb00701_transverse_trig_interval.py`:
  `2320f92efe4316d865a89f6d848737e2c000ca4d`;
- frozen v54 corpus:
  `5841c331579489b25caef38cd412bdbf286f9134`;
- MC-002 26-operation domain:
  `23de82f5240a72509f7afe4acd5948b65bc4ff13`;
- current authority:
  `fa0233323a0804d8a5d3eb7cd892a274a6173fab`.

The #303 primitive also rechecks its own transitive custody.

## Verification

Focused command:

```bash
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_knot_zero_cover.py --contract --self-test
```

The PR must also pass `mc1-static` on the exact final head, receive a distinct
technical/source review of that exact head, and use expected-head-protected
merge if accepted. Merged-main focused/static checks and reviewed/landed tree
identity remain required.

## Explicit nonclaims

This result, if accepted, remains **DETERMINISTIC_MODEL** evidence only. It does
not establish arbitrary nonrational or irrational coincident roots, general
V27/V41 nested-child composition, frozen v54 owner admission, PB-007-01, MC-B,
MC-1, native material/topology/lineage, B-rep, usable engineering STEP, or
production authorization.

Historical v54 dispositions, the 26-operation lathe/mill domain, source and
provenance semantics, phase identity, canonical journal, material/body/lineage,
refusal/UNCERTIFIED behavior and conventional STEP obligations remain
unchanged.
