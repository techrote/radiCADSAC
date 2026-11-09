# B1-D1 — source-typed phase-basis equivalence, not cross-lane certificate admission

**9 November 2026 · research-only · deterministic model · Draft/HOLD.**
Code: `phase_bridge.py`; checks: `test_phase_bridge.py`. Owner: B1, exclusive `research/experimental/certificate-algebra/core/**`. This is an *additive* follow-up to the B1-C1/C2 Bernstein sign-cone model in [Draft #473](https://github.com/techrote/radiCADSAC/pull/473), **not** a modification of A1/A2/MC-038 or a production proof registry.

## Source-critical motivation and exact falsifier

A3's [review of A1 #470](https://github.com/techrote/radiCADSAC/pull/470#pullrequestreview-5833649666) identifies incompatible phase units:
- A1 #470 at `281705e947fd7812300d1d2605d3cdf60cdb005e` evaluates `cos(h*pi*(offset+rate*t))` (and sine).
- A2 #471 at `38b45dbd028742cca3758a86666d366e9b5df66b` and accepted MC-038 `pb00701_transverse_trig_interval.Span` at main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9` evaluate `cos(2*pi*h*(offset+rate*t))`.

For `F=-1+sin(theta)`, `offset=0,rate=1,t=1/2`, A1 computes `-1+sin(pi/2)=0` while A2/MC-038 compute `-1+sin(pi)=-1`. Reusing certificates on apparently identical untyped phase fields is **unsound**. This is not a counterexample to either lane's own theorem.

**Preregistered falsifier:** any accepted cross-source receipt with identical numeric offset/rate and mismatched phase units, altered Fourier channels, altered interval, changed claimed origin identity, unreviewed producer head, or unsupported source grammar. Unknown/unsupported must refuse, never mean root-free.

## Exact closure theorem D1 (infinite family)

Let `s` denote the number of radians-per-pi phase units: `s=1` for A1 and `s=2` for A2 or MC-038. For an arbitrary finite family of rational polynomial amplitudes `P_h(t),Q_h(t)` and a rational affine phase `a+b*t`, define

`F_(s,a,b)(t) = sum_h [P_h(t) cos(h*pi*s*(a+b*t)) + Q_h(t) sin(h*pi*s*(a+b*t))]`.

For sources 1 and 2 on the **same physical interval**, with identical *physical-time polynomial coefficients and harmonic indices*, if

`s1*a1 = s2*a2` and `s1*b1 = s2*b2` exactly over the rationals,

then `F_1(t)=F_2(t)` for **every real t** on that interval. Proof: each harmonic's trig argument is identical as a real expression. Adding equal terms proves pointwise equality, without sampling, root isolation, a Taylor truncation or a conjectured transcendence property. Consequently all existing zeros, true derivatives, multiplicities, and physical-t sided germs of the same function agree whenever independently defined. The phase conversion **does not reparameterize physical time**, so no knot-side reversal occurs; unlike the separate #462 signed-time affine transform.

This theorem is elementary unit normalization, not a new theorem. It has no claimed converse: equivalent functions might not share a canonical syntactic record (periodic offsets, dead harmonics, cancellations). They deliberately refuse in this checker. No Boolean/topology or physical-solver closure follows.

## Typed source and verifier contract

Input `b1-typed-phase-source-v1` records contain schema, producer kind, **exact pinned producer head**, opaque `origin_source_sha`, immutable physical-time interval, rational offset and rate, and explicit rational-polynomial `terms` (harmonic 0 sine must be zero). The conversion produces a canonical `pi_phase=[s*a,s*b]` with unchanged coefficient vectors and interval. All rationals are canonical Fraction strings, at most 90 characters and 128 bits per numerator/denominator. Arrays are bounded **before iteration**. Producer restrictions are conservative: A1 only H0/H1/H2 with contiguous positive harmonics and at most degree 16; A2 only nonzero phase rate, at most eight admitted harmonic entries and degree 3; MC-038 at most eight entries and degree 3. A2/MC-038 physical domain and rate bounds are checked. Some genuinely admissible producer states can still be refused by this narrower envelope grammar.

`prove_equivalent(source,target)` verifies and normalizes **both** records, then checks exact normalized equality and emits a `b1-phase-equivalence-v1` receipt binding both envelope SHA-256 values and normalized semantic SHA-256. `verify(..., pinned_source_hash, pinned_target_hash)` independently recomputes the statement, checks exact caller-provided trusted pins and refuses stale/forged/malformed statements. Input syntax is validated before potentially large untrusted JSON hashing. The checks are deterministic rational arithmetic.

**Critical trust boundary:** `origin_source_sha` and `producer_head` are only *claimed* fields of these standalone records. This program does **not** replay A1's `Source`, A2's `source_dict`, MC-038's `Span`, upstream spline control arrays, B-spline knot identities or #462 transform receipts. Nor are SHA-256 digests signatures. A trusted, independently verified producer-to-envelope codec and external hash pin custody are required before any cross-lane event certificate can be admitted. A self-created pair of envelopes proves their *internal mathematical equivalence*, not their identity to real producer objects.

## Deterministic controls and results

Run from this directory with Python 3.11+ stdlib:

```sh
python3 -m unittest -v test_phase_bridge.py
```

At the locally tested source bytes, **6/6 tests PASS**, including **260 rational parameter combinations** (208 nonzero-rate A2↔A1, 52 stationary MC-038↔A1), degree-two polynomial amplitudes and two positive harmonics; exact A3 phase mismatch and corrected transfer in both directions; negative rates, forged coefficient/source identity/head/pins, malformed input, overlong coefficients, unsupported harmonic arrays, A2 stationary refusal and deliberately conservative periodic-alias refusal. These finite tests are implementation challenges, **not** the proof of the infinite family.

Source-matched Git blob identities (the actual locally executed byte streams):
- `phase_bridge.py`: `1fff5c4403324ac87c690c78b924970b20813ce3`
- `test_phase_bridge.py`: `15f92a5d3c14e6aeaa068550942515b543a39d76`

No native/paid campaign and no new host workflow. The checker scans only bounded metadata (at most nine harmonics and up to 17 coefficients for A1, or eight harmonics and four coefficients per channel for A2/MC). It is **not** placed on a solver hot path. Neither wall-clock improvement nor production certificate reuse has been measured. The earlier B1-C2 2080-vs-96 leaf-proof comparison remains only abstract recomputation accounting.

## Existing mechanisms and next proof obligations

- A1 [#470](https://github.com/techrote/radiCADSAC/pull/470) is an exact algebraic-time *point* classifier, not an authenticated global event solver.
- A2 [#471](https://github.com/techrote/radiCADSAC/pull/471) proves a restricted rational-time local valuation; its source-admission/resource review remains separate.
- MC-038 [#453](https://github.com/techrote/radiCADSAC/pull/453) supplies a bounded simple-root interval partition, not arbitrary tangency closure.
- [#462](https://github.com/techrote/radiCADSAC/pull/462) already addresses B-spline insertion and signed affine **physical time** covariance; this bridge neither duplicates nor replaces that transformation's real source authentication.
- Classical Bernstein/de Casteljau sign and subdivision results underpin earlier B1-C1/C2 (Bertot, Guilhot & Mahboubi 2011, [DOI](https://doi.org/10.1017/S0960129511000090)). This D1 conversion is ordinary exact change-of-phase units.

**A3 review request:** challenge producer-specific admission, stale-head handling, noncanonical zero channels, altered origin hashes, signed-rate checks and whether any cyclic/periodic alias can accidentally pass as equality. **B5:** identify who owns an independently verified adapter from real A1/A2/MC-038 source hashes to this typed envelope. Do not integrate a source receipt until that adapter itself is verified. A later scope might compose externally accepted germ/root statements *after* this equivalence precondition; the present program only proves function identity.

**Authority invariant:** Original census **121/20/30/50**, supported machining operations **26**, newly closed historical original IDs **0**; no PB/PO gate discharge. MC-B and MC-1 remain `NOT_ESTABLISHED`; `production_authorized=false`. No native geometry, STEP output, source-acceptance claim or CyberSand physics change.
