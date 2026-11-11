# B1-D19 — Unicode harmonic-key source-boundary refusal

**11 November 2026; bounded research GO; authenticated producer integration HOLD; native/STEP adoption NO-GO.** Draft PR #473, owner B1. Baseline accepted main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`; tested predecessor head `f81bbf4004d2bce15a6c5ba91eb657a075ff7b38`. Three ADD/MODIFY paths, all within `research/experimental/certificate-algebra/core/`. No production or MC-038 authority changes.

## Defect and falsifying control

The actual `phase_bridge._canonical_owned()` A1 harmonic-channel preflight called `str.isdigit()` and then `int(k)`. Python reports `'²'.isdigit() is True` yet `int('²')` raises built-in `ValueError`. Superscript `'⁴'` and subscript `'₃'` do the same. The correctly primitive-validated untrusted envelope therefore escaped the typed consumer refusal instead of classifying its harmonic source as inadmissible. This is a source-grammar/exception-contract failure, **not** a false mathematical zero certificate.

The newly committed `test_phase_unicode_harmonics.py` challenges `canonical`, `prove_equivalent`, and the genuine `verify` entry point using untrusted, pinned envelopes; includes seven non-ASCII digitlike keys, positive valid ASCII 0–2 harmonics, and an ASCII gap negative control. On literal D18 predecessor, focused regression **FAILED (4 errors)** from real `int()` exception escapes; original complete suite still passed **104/104**. The direct source-consumer correction restricts numeric preflight to `re.fullmatch(r"[1-8]", k)`, consistent with its existing authoritative ASCII harmonic grammar. The later grammar validation then returns typed `Refusal` on unrecognized keys; no extension or reinterpretation of source semantics.

## Complete tests and exact Git-source custody

Local test execution assembled from the D18 source archive, with **26/26 predecessor Python Git blob SHA-1 objects matched to the published exact-head Git tree** (not just a standalone receipt probe). After modifying the one real consumer and adding the one regression module:
- `python3 -m unittest -v test_phase_unicode_harmonics.py`: **2/2 PASS**.
- `python3 -m unittest discover -v -p 'test*.py'`: **106/106 PASS**, zero skips, **1.500 s**; includes all B1 parent-module, hostile equality/Fraction, nested primitive, source/identity, invalid digest, split/affine, closure budget and E1–E7 consumer tests.
- `python3 -m compileall -q .` and `python3 experiment.py`: **PASS**.
- New published Git blob IDs: `phase_bridge.py=576c472335122949a1de264659d0200f0c9394fc`; `test_phase_unicode_harmonics.py=0b45f8c1ae16149c0ef15cc8bfbc3f99269bcb9e`. Both computed locally from executed bytes and matched independently created GitHub blobs. The D18 subtree remained otherwise unchanged.

A1 #470 at `fe0dada7c430053c4c387f17a062909da9aab8bc` was executed with its actual pinned producer modules (`algebraic_zero.py=5a8e52898725aa10b427de4e5736cb1cf5578d68`, `receipt_integrity.py=77f0ba7700002b7a376dfcc2c29b820ea4def485`), reconfirmed against current producer Git tree. Genuine `-1+sin(pi*t)` event at rational `t=1/2` verifies `EXACT_ZERO`, at `t=0` gives `EXACT_NONZERO`, and forged result/source mutation fails. B1 codec and phase checks were replayed on locally corrected B1 bytes. Its adapter still stamps historical A1 producer `281705e9…` and explicitly **refuses unreviewed current A1 head**. Window is research-supplied, *not* independently authenticated physical spline controls, knots or source window. **Current A2 genuine source receipt is not executed: HOLD.** No source ancestry has been inferred or invented.

## Fair verification economics and native decision

Five-repeat symmetric-order Python-only experiment, 32 static polynomial pieces and 64 edits, identical intermediate hashes across all arms. Medians (ms): trusted incremental **30.729**, efficient full reproving **84.261**, incremental + equal strict every-edit readmission **165.142**, efficient full + readmission **216.220**. Complete-readmission benefit **1.309×** or **51.078 ms / 64 edits (0.798 ms/edit)**; only if any additional incremental-side external custody/native dependency-closure cost **minus** the corresponding full-side cost is below this saving. The 3×-Bernstein baseline is not the fair comparator. The local Unicode fix is unrelated to this proof-work optimization.

**NO-GO native/STEP/simulation adoption:** no measured native/STEP consumer, fully authenticated source lineage, nonlocal influence-cone proof or end-to-end cost. B5's global-influence counterexample invalidates direct extrapolation to CyberSand pressure/multisolver physics; #462's B-spline transformations do not by themselves supply A1/A2 physical lineage.

## Review, open laws, and frozen programme gates

A3 should independently execute literal B1 head and authentic current A2 `source → point_germ/knot_germ → verify` controls; label BLOCKED if unable to establish producer provenance. B5 should challenge this source boundary and the fully reverified economic break-even; do not treat locally matched current A1 code as authenticated external custody. All findings remain DETERMINISTIC_MODEL research. B1-C1/C2 infinite-family Bernstein sign/split/affine laws retain their precise assumptions; arbitrary Boolean topology, physical B-spline ancestry and complete dependency closure remain OPEN. Draft only, do not merge or mark Ready without independent review and exact-head hosted qualification.

Frozen historical **121/20/30/50**, **26 supported machining operations**, **MC-B/MC-1 NOT_ESTABLISHED**, `production_authorized=false`, immutable evidence and original proof/production hold remain unchanged.
