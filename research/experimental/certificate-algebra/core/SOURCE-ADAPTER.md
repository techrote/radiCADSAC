# B1-D2 — source-derived phase-certificate binding, restricted A1 ↔ A2

**Research date:** 9 November 2026. **Evidence:** deterministic exact-rational model, source-matched local test execution. **Status:** Draft/HOLD, independent A3/B5 challenge outstanding. [Candidate PR #473](https://github.com/techrote/radiCADSAC/pull/473). Entire change confined to `research/experimental/certificate-algebra/core/**`.

## Question and preregistered falsifier

B1-D1 already proves that two finite Fourier polynomial sources with physically identical coefficient polynomials and normalized phase have identical values for every real time. [B5 review](https://github.com/techrote/radiCADSAC/pull/473#issuecomment-6753698864) correctly observed that caller-created envelopes cannot establish the source was an A1 or A2 producer object. This experiment implements a *restricted serialization-to-envelope attachment* without invoking either producer or modifying either research lane.

Falsifier: modified A1/A2 coefficient, phase, interval, pin or unsupported grammar is admitted against **unchanged trusted external pins**, or matching numeric phase fields are mistaken for equal radians-per-time. A self-authored new envelope and *new* pins are an explicit counterexample to any stronger authentication claim.

## Exact admitted inputs and source versions

- A1 [#470](https://github.com/techrote/radiCADSAC/pull/470): `algebraic_zero.Source`'s canonical `source_sha()` JSON object with exactly `c0, cos, sin, phase_offset, phase_rate`. For zero polynomials A1 serializes `[]`; conversion maps this to explicit `["0"]` without changing the function. H0 plus zero-to-two contiguous harmonics; degree at most 16. A1 has **no physical interval field**: a separately trusted rational window is mandatory.
- A2 [#471](https://github.com/techrote/radiCADSAC/pull/471): canonical `source_dict()` JSON object with `interval, phase, terms`, exact rational polynomial coefficients and physical-time domain. A2 has nonzero phase rate and degree at most three; this codec deliberately admits only the *intersection* with B1's explicit-H0/contiguous-harmonic rules. Not every legitimate A2 source is admitted.
- Source record source pins are `SHA256(json.dumps(record,sort_keys=True,separators=(",",":"),ensure_ascii=True))`, matching the inspected producer serializers. The domain pin is SHA256 of the complete two-rational window; it must agree with A2's interval. All three pins must come from independent trusted custody; passing `digest(record)` as the pin without external checking proves no provenance.
- Exact inspected A1 source code blob `daeb0b4ff0325c246bbf0f5737daf359400b7c3d`, head `281705e947fd7812300d1d2605d3cdf60cdb005e`; A2 code blob `311b5421e0e51f0b34739a7d0428533018a9a383`, head `3b6eaf70e1e7422b7ac8e8e9ff6f0fef85281978`. Previously B1-D1 hardcoded A2's earlier head `38b45dbd...`; the narrow D2 patch repins its producer declaration to the **current inspected A2 head**. Producer head metadata remains a *constant in this model*, not a code-signing mechanism.
- Rational text must be canonical and within B1's 128-bit/90-character budget; reject unsupported producer-valid larger values. Validate nested sizes/types **before hashing**; unsupported and resource over-budget mean REFUSE/UNKNOWN, not a mathematical nonzero claim.

## Conditional preservation theorem (infinite family)

Let \(S_1\) be an A1 canonical serialized rational-polynomial Fourier source and \(S_2\) an A2 canonical serialized source, both admitted by `producer_codec.py`. Let the externally pinned physical window \(I\) equal A2's source domain; A1 is restricted to \(I\). Assume source hash pins refer to those exact immutable upstream serializations and the code-version contract is independently trusted. The codec reconstructs coefficients unchanged, except for representing A1's empty polynomial as the zero coefficient `["0"]`. It does not rescale physical time or move knots.

If `certified_pair` succeeds, all harmonics and polynomial coefficients agree, and the exact rational phase expressions obey \(\alpha_{A1}=2\alpha_{A2}\) and \(\beta_{A1}=2\beta_{A2}\). Consequently, for **all real \(t\in I\)**,

\[
F_{A1}(t)=\sum_h\left(P_h(t)\cos(h\pi(\alpha+\beta t))+Q_h(t)\sin(h\pi(\alpha+\beta t))\right)
=F_{A2}(t).
\]

Proof: direct canonical reconstruction and equality of each trigonometric argument; summing equal terms yields equality. Thus any independently proved point-root, multiplicity or sided sign of *this same function* can be transported semantically, but an upstream receipt still requires its own verifier/source binding. The result applies to an infinite family of rational-polynomial coefficient choices and nonzero rational A2 rates, within the structural grammar. It is **classical semantic identity and canonical serialization preservation**, not new general event isolation, decidability or machining topology.

**Important failure of stronger converse:** An adversary may create two modified equivalent sources and supply fresh matching self-authored pins; the checker accepts such an internally valid pair. Therefore no external authorship, saved-history epoch, A1 execution, A2 module provenance, cryptographic signature or MC-038 evidence is established. Pins must be obtained from actual independently verified source producer and custody. This is an explicit maintained negative result.

## Adversarial fixture and measurement

`A1`: `c0=[-1], cos=[[]], sin=[[1]], phase_offset=0, phase_rate=1` (A1 uses pi-radian phase units). `A2`: physical domain `[0,2]`, `P0=-1, Q0=0, P1=0, Q1=1`, offset 0, rate 1/2 (A2 uses 2pi-radian phase units). Thus the two sources represent the same function, -1 + sin(pi*t). Changing A2 rate to 1 or changing either amplitude, source or window with the original pins refuses. The 52 `(k,degree)` cases include negative rates, 48 accepted nonzero-rate pairs and four explicitly refused A2 stationary cases, besides substitution/over-budget controls.

Run from the core directory with Python 3.11+ and standard library:

```sh
python3 -m unittest -v test_phase_bridge.py test_producer_codec.py
```

**Source-matched local result:** **12/12 test methods PASS** using exact Git blobs:
`phase_bridge.py=4ff925423fe74ef76dcf3fd27cc71c5b3761a09a`,
`test_phase_bridge.py=ea3b2d9552e74e1bd6ba18dc9890dc8002113751`,
`producer_codec.py=3f8c988a3ca1708ecac4a13fcd8a5f688032fc99`,
`test_producer_codec.py=af5951ca57745687d8a578aca27a194eed5c4193`.
A1/A2 upstream modules were **inspected, not executed** as part of this D2 fixture. Native/STEP and hosted exact-head test runs are not claimed. Finite source-serialization fixtures are reproducibility checks, not proof of the infinite theorem.

B1-C2's prior *abstract certificate check counter* was 2,080 versus 96 full-leaf validations and 2,015 versus 155 seam validations for 64 single-piece updates; those counts are **not repeated or transformed into runtime gains by D2**. D2 does fresh bounded metadata validation/hashing. No memory/CPU/physical solver speed claim; no hot-path proof engine.

## Prior work, open laws and next independent check

The mathematical equality is elementary; Bernstein positivity and de Casteljau closure were already formalized by Bertot, Guilhot and Mahboubi (2011), DOI [10.1017/S0960129511000090](https://doi.org/10.1017/S0960129511000090). [#462](https://github.com/techrote/radiCADSAC/pull/462) separately proves exact B-spline knot-insertion/affine-time source covariance; its source-codec/ordered-knot proof is not imported or reproduced. [#453](https://github.com/techrote/radiCADSAC/pull/453) provides restricted interval-root certificates, not a general multiplicity theorem.

**Open:** independently run the exact pinned producer modules on valid and malicious real source objects, compare fresh upstream producer digests to the D2 serializer, bind source-to-physical-window custody, then independently verify one genuine A1/A2 receipt before considering a richer event-certificate transport. Require A3 to challenge source grammar and B5 to review pin custody/interface and nonoverlap with #462. No arbitrary Boolean/topology, simulation invalidation or pressure/solver authority transfer follows.

The frozen **121 originals / 20 historical route refusals / 30 missing ordered premises / 50 complete witnesses** remain unchanged; all **26** machining operations remain required. New historical original closures **0**. MC-B/MC-1 **NOT_ESTABLISHED**, `production_authorized=false`. No native/paid work, production files, shared proof ledger or original corpus altered.
