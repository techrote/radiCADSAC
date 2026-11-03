# PB-007-01 — three original-source Bernstein/sector event witnesses

**Task:** MC-038 / [#100](https://github.com/techrote/radiCADSAC/issues/100).

**Preregistered scope:** [three-source continuation](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6591355781).

**Source baseline:** `e0514500aeca59afa4924dcc2da3ca0c2688d9ac`.

**Evidence class:** deterministic exact-arithmetic model research.

**Programme:** PB-007 remains open; MC-B and MC-1 remain `NOT_ESTABLISHED`.

## Purpose and exact source selection

This leaf supplies complete closed-source zero sets and ordered physical signs
for three original two-span sources in the frozen V54 corpus. The existing
registered inventory lists them without a selected event/order witness. Their
historical child labels are `CERTIFIED`, while their historical whole-source
disposition remains
`BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE`. Those labels and all original
source records are preserved.

| Original case ID | Complete closed-source result on `[0,2]` | Forward signs |
|---|---|---|
| `composite:PB00701_V18_EXACT_NONVANISHING_SOURCE_MODULE_FACTOR:tail0` | No zeros | Negative throughout |
| `composite:PB00701_V18_EXACT_NONVANISHING_SOURCE_MODULE_FACTOR:tail100` | One simple zero in `(1,1001/1000)` | Negative, positive |
| `composite:PB00701_V26_EXACT_POINTWISE_COMPONENT_CONE_RESIDUAL_ORTHANTS:tail0` | One simple zero in `(1/2,1)` | Positive, negative |

All exterior endpoints and the original physical knot `t=1` are nonzero. Root
brackets identify unique implicit zeros of the original function; their
rational endpoints are not asserted to be roots. No sign outside the original
closed interval is claimed.

The [machine witness](pb00701-bernstein-sector-source-witnesses.json) records the
complete original specifications, original-row hashes, historical observations,
reconstructed Bernstein blocks, derived rational inequalities, implicit events,
maximal sign cells and non-event proof cuts. The
[model](pb00701_bernstein_sector_source_witnesses.py) recomputes these records.
The [verifier](verify_pb00701_bernstein_sector_source_witnesses.py) compares the
saved witness against fresh proofs and challenges the premises.

## Custody and bounded assumptions

The frozen corpus has Git blob
`5841c331579489b25caef38cd412bdbf286f9134`. Its complete historical audit still
contains **121 original sources, 20 route refusals and 30 missing ordered
premises**. The existing inventory, coverage file and original frontier auditor
are pinned independently. Current authority, the programme and the 26-operation
domain are also pinned and checked.

| Selected source | Source specification SHA-256 | Complete original-row SHA-256 |
|---|---|---|
| V18 source-module tail0 | `2c0db76bcf217c98b53d8b45ee537aec4da818c649df2436c27860a4d8c17111` | `06f88535a67c3d521d831f2205b69c3466ff4a2723cdb53b37c5e430b24c04c8` |
| V18 source-module tail100 | `2b1f53109ad708bd6eab37e83529e1001a7cadfa82fe630ddf230d94f2132d29` | `fa9de27d0eead12eb2c8cee6e49b4b51ba6508e1b1c9dbc8b6e5620c2d15ddf6` |
| V26 residual-orthants tail0 | `a9bb78a5415d1c45f54be7838f77739c8854cf329a97b36576f2a2fedf4ed3e4` | `333c1bf98905cd41773c7da92efd33f36dc2f1e1bc947b285d9175a4926a25ad` |

The sufficient-condition helpers admit two independently fully clamped unit
spans, degrees 0 through 12, the explicitly listed harmonic maps and fixed
original affine phase laws. They check every control count and knot
multiplicity. They require the ending first-block control to equal the starting
second-block control in every channel, proving physical-source continuity at 1.
They do not require derivative continuity at that knot, because its strictly
nonzero value excludes a zero event there.

Bernstein basis functions on a closed unit interval are nonnegative and sum to
one. The minimum and maximum controls therefore give closed-interval amplitude
bounds. Derivative controls and de Casteljau restrictions are reconstructed
exactly and independently checked by power-polynomial expansion. The analytic
proof uses the classical strict bounds `3<pi<22/7`, elementary trigonometric
sector signs, and continuity plus a strict first-derivative bound. Numerical
root sampling or an execution budget does not establish truth.

## V18: complete first-span negativity and exact tail alternatives

Both V18 sources retain original parameter `v53-simple-repeated-join` and

`theta(t)=pi*(1+t)/12`.

Their physical expression is

`F(t)=C0(t)+C1(t)*cos(theta)+S2(t)*sin(2*theta)`.

On the original first span `[0,1]`, direct extrema of the original controls are:

| Original amplitude | Degree | Derived bound |
|---|---:|---|
| `C0` | 7 | `C0<=-98/2187` |
| `C1` | 6 | `abs(C1)<=289/46656` |
| `S2` | 6 | `abs(S2)<=289/93312` |

Consequently,

`F<=-98/2187+289/46656+289/93312=-9943/279936<0`.

This excludes every first-span zero, including its endpoints. The amplitude
polynomials need not be monotone; the proof uses the convex hull of all their
original Bernstein controls.

The second-span control blocks independently reconstruct exactly

`F=-98/2187+k*(t-1)+(49/18225)*cos(theta)+(49/36450)*sin(2*theta)`,

where `k=0` for tail0 and `k=100` for tail100. Every derivative control of `C0`
equals the reported slope; every other second-span amplitude control is
constant. At the original knot,

`F(1)<=-98/2187+49/18225+49/36450=-4459/109350<0`.

For **tail0**, the same bound applies throughout `[1,2]`. Combining both closed
source spans gives strict negativity everywhere and an empty zero set.

For **tail100**, the original derivative satisfies

`F'>=100-(22/7)/12*(49/18225+2*49/36450)=5467423/54675>0`.

At the rational point `1001/1000`, an amplitude lower bound gives

`F>=-98/2187+1/10-49/18225-49/36450=2797/54675>0`.

The strictly negative knot and strictly positive bracket endpoint establish a
zero by continuity. The positive derivative bound on the entire second source
span establishes uniqueness and analytic order one. The same derivative bound
and the explicitly positive right exterior endpoint exclude further tail
zeros. The whole source has exactly one zero, with negative then positive signs.

## V26: a complete crossing proof from original phase sectors

The original parameter is `source-time-t` and

`theta(t)=pi/3-2*pi*t/3`.

The source is

`F=A(t)*cos(theta)+B(t)*sin(theta)+epsilon*cos(2*theta)`,

with `epsilon=1/10000` and no harmonic-zero residual. Its first-span quartic
Bernstein controls are

`A=(83/20,17/4,271/50,403/100,403/100)`

and

`B=(1081/100,269/25,271/25,227/20,269/25)`.

### Positive first half

For `t in [0,1/2]`, `theta in [0,pi/3]`. Thus `cos(theta)>=1/2` and
`sin(theta)>=0`. Both amplitude control sets are strictly positive, so

`F>=min(A)/2-abs(epsilon)=20149/10000>0`.

### One simple crossing in the second half

The exact derivative controls, restricted by de Casteljau to `[1/2,1]`, are

`A'=(-7/25,-161/100,-139/50,0)`

and

`B'=(113/200,51/100,-4/25,-59/25)`.

These represent derivatives with respect to original `t`; no additional local
parameter scaling is silently applied. The right-half controls of `B` are

`(3501/320,8809/800,443/40,2211/200,269/25)`,

so `B>=269/25`. On this half, `theta in [-pi/3,0]`. Hence

- `A'*cos(theta)<=0`;
- `B'*sin(theta)<=59/25`;
- `A*sin(theta)<=0`;
- `B*cos(theta)>=B/2`.

Differentiating the original function and bounding its residual gives

`F'<59/25-269/25+4*(22/7)*(1/10000)/3=-220489/26250<0`.

At the physical knot `t=1`, exact endpoint trigonometry yields

`F(1)=403/200-(269/50)*sqrt(3)-1/20000<=-67301/20000<0`.

Therefore exactly one zero lies in `(1/2,1)`. Its derivative is nonzero, so the
zero has analytic order one. The positive first half and strict decrease on the
second half exclude every other first-span zero.

### Negative complete tail

The original tail blocks are constant `A=403/100` and `B=269/25`. Splitting the
analytic argument at `t=5/4` gives two closed proof sectors:

| Original `t` interval | Phase interval | Exact upper bound |
|---|---|---|
| `[1,5/4]` | `[-pi/2,-pi/3]` | `F<=(A-B)/2+abs(epsilon)=-33649/10000<0` |
| `[5/4,2]` | `[-pi,-pi/2]` | `F<=-min(A,B)+abs(epsilon)=-40299/10000<0` |

The first sector uses `cos(theta)<=1/2` and `sin(theta)<=-1/2`. In the second,
both functions are nonpositive and `abs(cos(theta))+abs(sin(theta))>=1`.
At the right exterior endpoint the value is exactly
`F(2)=-403/100+1/10000=-40299/10000`.

The cut `5/4` changes the proof inequality, not the original source or zero set.
The physical knot remains `1`, is continuous and strictly negative, and is not
a zero event. The complete source has one simple zero and forward signs
positive then negative.

## Validation boundary and negative controls

Public source helpers first preflight bounded typed JSON, then parse only
canonical ASCII integers or reduced integer ratios. Exponent/decimal strings,
non-ASCII digits, numeric aliases, excessive bit lengths and oversized structures
are rejected before dangerous rational construction. Dependency bytes are
bounded and checked against their Git blob before those same bytes are parsed
or the accepted auditor is compiled into a fresh module namespace. The auditor
uses only standard-library imports. Its legacy file-loading entrypoint is not
called: the wrapper supplies the already verified, decoded original inputs.
The verifier likewise bounds and directly compiles the exact reviewed model
blob. Neither code-loading path asks an import loader to choose cached bytecode
or uses a preloaded project module. Candidate report fields never become inputs
to a historical rational parser.

The frozen wrapper separately checks complete original-row custody and the
original source SHA-256. A valid synthetic helper result cannot become evidence
for a different frozen source. Report validation compares typed canonical bytes
with a fresh original-source replay; integer and boolean values remain distinct.
A missing premise or failed replay aborts validation, without reducing the
selected source denominator or publishing a partial success.

The **29 adversarial test methods** cover actual mathematical premise failures:
strict-bound equality, a zero function that must not become an empty finite root
set, missing opposite-sign brackets, phase changes, extra or omitted harmonics,
nonconstant tails, discontinuous source knots, and a positive-amplitude source
whose derivative at `1/2` is provably positive. They also verify valid nonfrozen
conditional examples, a nonmonotone but strictly negative amplitude, independent
Bernstein identities, source/row custody, forged event orders and bounds,
analysis-cut event laundering, boolean/integer aliases, duplicate JSON keys,
bounded reads, same-buffer hash/parse custody and fail-closed replay. Two real
timestamp/size-matched bytecode counterexamples demonstrate ordinary import
loaders executing altered code while the source still hashes correctly. The
model bootstrap and auditor loader execute the verified source instead, even
with decoy preloaded project modules. Replacement between verification and
compilation or parsing also cannot change the retained buffer; a later read of
the altered path refuses. The mathematical model and saved witness are unchanged
by this verifier-custody hardening.

The older V41/V13 fixed-source proof was considered for broader multiplier
work, but it contains sine harmonic 4 rather than the relevant sine harmonic 3.
It is not used here. Five other unregistered multiplier sources are outside
this leaf and retain their separate proof and integration requirements.

## Programme and downstream implications

This leaf supplies three complete source-specific mathematical witnesses. It
does not rewrite the frozen historical 121/20/30 census, register new generic
V18/V26 routes, update the separate evidence inventory, or provide a universal
normalized event consumer. A later reviewed integration can register these
producers after the exact source head and landed main have qualified.

The 26-operation domain, original phase/parameter correlation, provenance,
canonical journal, material bodies and lineage, refusal/`UNCERTIFIED` semantics,
and conventional usable engineering STEP requirement remain intact. PB-007-01
and its dependent obligations remain open; MC-B and MC-1 remain
`NOT_ESTABLISHED`. No native geometry, topology, reconstruction, STEP or
production capability is claimed. No native or paid campaign runs here.

For OpenSimachinist research, the useful result is a source-bound ordered event
witness with explicit nonzero source-knot semantics. For future MSAC work, this
does not authorize an application slice or change saved manufacturing intent.
The remaining general terminating event coverage and proof-consumption
obligations still govern later integration.

## Reproduction and qualification

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_bernstein_sector_source_witnesses.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_frontier.py --contract --self-test
python3 tools/validate_repo.py
python3 tools/validate_machining_completeness.py --self-test
```

To regenerate the deterministic witness from the pinned originals:

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701_bernstein_sector_source_witnesses.py --write-report
```

The focused workflow has one bounded Python job, checks the literal PR head,
uses read-only repository permissions, and names the exact local and pinned
dependency paths. Separate technical review, applicable exact-head CI,
reviewed/synthetic/landed tree equality, an expected-head guarded merge and
independent merged-main checks remain the integration requirements. No claim
about a later workflow run or merge identity is embedded in this source artifact.
