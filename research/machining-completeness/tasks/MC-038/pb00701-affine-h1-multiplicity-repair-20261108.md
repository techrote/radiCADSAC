# MC-038 / PB-007-01: source-critical shared-zero multiplicity correction

**Research classification:** DETERMINISTIC_MODEL; restricted adversarial correction to the angular-drift H1 event certifier in PR #439. **Date:** 8 November 2026. **Status:** corrective research candidate, not an accepted proof obligation or MC-B gate. **Parent:** PR #439 at `e3264629c967189f5b843bbb7e73b80df2f3c56c`. See the independent technical REPAIR review in that PR. **Integration:** this change is isolated on a child branch and must be reviewed before adoption; #397 retains sole main-integration authority.

## Failure criterion and original false-positive test assertion

The former test `test_identity_zero_shared_amplitude_and_tangency_refusals` described the source with first-span `C=S=2t-1` as a multiple or tangential physical zero. In fact, with `theta=pi*t/4`,

`F(t)=(2t-1)(cos(theta)+sin(theta))`,

so `F(1/2)=0` but `F'(1/2)=2(cos(pi/8)+sin(pi/8))>0`. That is a **simple crossing**, NEGATIVE to POSITIVE. The classifier's `q_min=0` refusal is legitimate: nonvanishing amplitude is a sufficient-grammar precondition, not a physical root-multiplicity detector. The old comment claimed adversarial coverage that did not exist. The correction retains that example, labels it correctly, and checks its precise refusal reason.

A historical corroboration already identified by the previous source review is frozen `composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail0`, original source SHA-256 `f4c2d33cc4c5a52f355ff4ecc36ad6ee38af0ff0fa8c5159aaac5923a10125ff`: its first stationary piece `F=t-1/2` also has a *simple* zero where `q=0`. It is outside #439's admitted nonstationary phase and is **not** a newly discharged original source.

## Genuine even-multiplicity counterexample on the admitted source-time/phase layout

Take continuous, identically matched rational degree-one H1 coefficient laws over the true source knot at `t=1`, original time `[0,2]`, turns `beta=t/8`, `theta=pi*t/4`:

`C(t)=1-t`, `S(t)=t-1`; supplied clamped spline controls `C=[1,0,0,-1]`, `S=[-1,0,0,1]`; both knot vectors `[0,0,1,1,2,2]`.

Writing `u=t-1` gives the exact identity

`F(t)=sqrt(2)*u*sin(pi*u/4)`.

Within `u in [-1,1]`, the factors `u` and `sin(pi*u/4)` have matching sign. The sole physical zero is `u=0`; both open sides are **POSITIVE**. Its first derivative is zero, and its second derivative is `F''(1)=pi/sqrt(2)>0`, establishing multiplicity **exactly two**. The repaired suite requires explicit `REFUSED_NONTRUTH` with `IDENTITY_OR_SHARED_AMPLITUDE_ZERO_REFUSAL`. No passage from this source's failed sufficient grammar to a no-root certificate is permitted.

## Exact positive/negative perturbation bifurcation

Perturb both coefficients by the same rational `epsilon`:

`C(t)=1-t-epsilon`, `S(t)=t-1-epsilon`.

For `u=t-1`, another exact identity is

`F(t)=sqrt(2)*cos(pi*u/4)*(u*tan(pi*u/4)-epsilon)`.

The cosine factor stays strictly positive on the full `[-1,1]` domain. The even function `g(u)=u*tan(pi*u/4)` vanishes only at zero and strictly increases with `|u|` on `(0,1]`. Consequently:

- `epsilon=0`: exactly one root of order two at `t=1`, with positive signs on both sides.
- `epsilon=2^-120`: exactly two simple crossings on opposite sides, with signs POSITIVE, NEGATIVE, POSITIVE; these are not one double root.
- `epsilon=-2^-120`: no physical zeros and strictly positive throughout.

For a **strict rational isolator**, put `h=2^-50`. The exact inequalities `tan(pi*h/4)>pi*h/4>3h/4` and `3h^2/4 > 2^-120` imply `g(h)>epsilon`. Hence the positive-perturbation zeros lie strictly in `(1-h,1)` and `(1,1+h)`, separated by less than `2h=2^-49`. Their existence/order are analytic consequences, not floating-point root scan results. At either perturbed sign the source is deliberately **outside** #439's safely proved strict angular-drift bound, and the live classifier must refuse rather than misreport a root set.

The code adds assertions for this exact rational inequality and both typed refusals. This tests a scientifically meaningful root-bifurcation discriminator without broadening the theorem or increasing arithmetic caps.

## Scope, reproduction and historical safeguards

Relative to parent #439, this patch changes only its task-local Python tests/helper and adds this RAG note. The certificate producer, canonical historical receipt, frozen V54/V2 source files, proof/programme/authority registers, source-time grammar and production code are not modified. Parent workflow `.github/workflows/mc1-pb00701-affine-h1-angular-drift.yml` continues to run the exact-head self-tests, the full V54/V2 producing replay and repository-wide MC-1 static validation on the corrective PR. Reproduce the focused step at repository root:

`python3 research/machining-completeness/tasks/MC-038/pb00701_affine_h1_angular_drift_20261106.py --self-test --contract`

The historical census remains **121 original sources, 20 historical route refusals, 30 missing ordered premises, 50 preexisting original-specific complete witnesses**, with all deltas zero, newly closed historical IDs `[]` and additional PB/PO discharges **0**. PB-007-01/02/03/04 and PO-02/04/05/07/08 stay OPEN. **MC-B and MC-1 remain NOT_ESTABLISHED.** No native geometry, independent-oracle machining, STEP, full 26-operation coverage or production authorization follows.

**Acceptance gate:** independently recheck all mathematical claims and read actual literal-head focused/full-original/static CI before admitting the child correction. Do not merge into #439 or main in its writing session; retain this leaf as a Draft candidate if any check remains inconclusive.
