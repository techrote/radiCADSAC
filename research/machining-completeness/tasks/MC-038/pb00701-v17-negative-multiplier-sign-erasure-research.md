# MC-038 / PB-007-01 — Original V17 negative multiplier: physical-sign erasure falsified

**Status:** source-bound mathematical C research, draft integration pending independent final-head review.  
**Date:** 4 November 2026. **Evidence class:** `DETERMINISTIC_MODEL` only.  
**Original source:** [frozen v54 corpus](pb00701-finite-owner-corpus-v54.json), case
`composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail100`.  
**Original canonical SHA-256:** `e85d997c9f4d828b1b748c964b375c21e4acef1b1e9046e074b1f7e29011d08f`.  
**Original whole-row SHA-256:** `41e86bc30392515873fb55bdd844d154236a81426fd3639c3bd5491dad30f05a`.  
**Preimplementation hypothesis and exclusive write set:** [MC-038 #100 preregistration](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6645534225), [coordination claim](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6645535069).

## Exact negative hypothesis and scope

The precise proposed (and *unsound*) composition shortcut is
`NONVANISHING_MULTIPLIER_PRESERVES_CARRIER_PHYSICAL_SIGNS`:
after establishing that an exact trigonometric multiplier is nowhere zero,
copy all physically ordered carrier sign cells and root crossing orientations
to the multiplied **physical source**, without consuming the multiplier's
signed nonzero certificate.

This is **not** an allegation that the accepted V17 producer actually commits
that error. The accepted whole-source v2 witness already records the correct
negative sign. This leaf supplies an independently legible original-source
counterexample and an adversarial anti-regression contract for a possible
future generic category-3 consumer. It does not introduce a new original
source witness, alter the old owner or repair every possible multiplier route.

**Named obligation:** PB-007-01, with downstream PO-04/05/08 implications for
ordered physical event/sign transfer; PB-007-02/03/04 and other POs remain
unproved. The actual historical V54 classification was
`BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE`: its child spans were
marked `CERTIFIED`, but the original owner did not produce an accepted
source-wide ordered physical view. This historical state remains untouched.

## Source semantics and independently exact factorization

The original parameter is `source-time-t`, closed source interval `[0,2]`,
real knot `t=1`, turns `beta(t)=t/4` and phase angle
`theta(t)=pi*t/2`. All five present channels have degree-one, two-piece
fully clamped B-splines with knots `[0,0,1,1,2,2]`.
The source has C0, C1, C3, S1, S3; no other harmonics.

| Physical channel | Controls over `[0,1]` | Controls over `[1,2]` |
|---|---|---|
| cosine H0 | `0,0` | `0,100` |
| cosine H1 | `1,-3/2` | `-3/2,-3/2` |
| cosine H3 | `-1/3,1/6` | `1/6,1/6` |
| sine H1 | `-3/2,1` | `1,1` |
| sine H3 | `-1/6,1/3` | `1/3,1/3` |

Every channel matches across the *true* knot. Do not split, rename or
renormalize the physical source by a manufactured chart boundary.

On the first closed original source piece, set

\[
a(t)=t-\tfrac13,\quad b(t)=\tfrac23-t,\quad
R(t)=a(t)\cos\theta(t)+b(t)\sin\theta(t),
\quad M(t)=-2+\sin(2\theta(t)).
\]

The exact trigonometric product identities

\[
\sin(2\theta)\cos\theta=(\sin3\theta+\sin\theta)/2,\qquad
\sin(2\theta)\sin\theta=(\cos\theta-\cos3\theta)/2
\]

give the physical Fourier coefficients

\[
C_1=-2a+b/2,\quad C_3=-b/2,\quad
S_1=-2b+a/2,\quad S_3=a/2.
\]

Substitution reproduces **all original** first-piece B-spline controls
coefficientwise. Therefore the **original physical** function, not a
surrogate, obeys `F(t)=M(t)*R(t)` for `0<=t<=1`.
Since `-1<=sin(2theta)<=1`, `-3<=M<=-1<0`. On this
piece the tighter interval is `[-2,-1]`. Thus nonvanishing
preserves the *root set*, but reverses **every** nonzero physical sign and
simple-root derivative orientation.

Three exact source samples already falsify sign erasure:

| Source time | Carrier `R` | Multiplier `M` | Physical `F` |
|---|---|---|---|
| `0` | `-1/3` | `-2` | `2/3` |
| `1/2` | `sqrt(2)/6` | `-1` | `-sqrt(2)/6` |
| `1` | `-1/3` | `-2` | `2/3` |

No floating sign test is involved.

## Complete zero-set and sign proof on the *same* original source

We prove the original full [0,2] event set so that the negative claim cannot
depend on hidden events or chart-endpoint duplication.

On `0<=t<1/3`, both `cos(theta)>0` and `b(t)>0`.
Factor

\[
R(t)=b(t)\cos\theta(t)\,[\tan\theta(t)-q(t)],\qquad
q(t)=\frac{1/3-t}{2/3-t}.
\]

Here `q'(t)=-1/[3(2/3-t)^2]<0` and
`(tan theta)'=(pi/2)sec^2(theta)>0`. Consequently the bracketed
difference is strictly increasing, and *any* root is simple and unique.
At `t=1/6`, `tan(pi/12)=2-sqrt(3)<1/3=q(1/6)`;
the radical inequality follows exactly from `3>(5/3)^2`.
At `t=1/4`, `tan(pi/8)=sqrt(2)-1>1/5=q(1/4)`;
this follows from `2>(6/5)^2`. Thus precisely one simple root
`r1 in (1/6,1/4)` occurs, with carrier changing negative→positive.

On `[1/3,2/3]`, `a,b>=0`, with at least one strictly positive
and both sine/cosine positive, so `R>0`. Under reflection `t -> 1-t`,
`a` and `b` swap and `theta` maps to `pi/2-theta`.
Hence `R(1-t)=R(t)`; precisely one further simple root
`r2=1-r1 in (3/4,5/6)` occurs, with carrier positive→negative.
There are no additional first-piece roots, no endpoint roots and no
identity-zero component. Multiplying by `M<0` changes physical signs
to **`+,-,+`**, with simple physical-root derivative signs
**`-,+`**, and no multiple roots or tangencies on this original.

The true knot is continuous and `F(1)=2/3>0`, so it is not an event.
On the second original piece the exact source has H0=`100(t-1)`,
constant C1=`-3/2`, C3=`1/6`, S1=`1`, S3=`1/3`.
Differentiating and using the trigonometric envelopes gives

\[
|F'(t)-100|\le
\frac\pi2\left(\frac32+\frac12+1+1\right)
=2\pi<\frac{44}{7}.
\]

Thus `F'(t)>656/7>0`, for all `1<t<2`; the tail starts
strictly positive and has no zero. At `t=2`, exact value
`F(2)=304/3>0`. All sign cells are in **original source time**,
the two implicit root brackets are not root coordinates, and the knot
is not double-counted.

## Negative conclusion and refusal boundary

A consumer that copies carrier signs would report `-,+,-` on the
first piece and invert both physical crossing orientations. The actual
physical signs are `+,-,+`, established independently above. Thus
the precisely specified sign-erasing shortcut **cannot discharge
category-3 ordered physical sign transfer** even on this frozen,
rational-degree-one H1/H3 original. A correct consumer must apply the
multiplier's source-bound sign (or a logically equivalent exact physical
one-sided jet) to each cell and crossing.

The conclusion does **not** falsify multiplication-based transfer
including the exact factor sign, or an alternative complete event
theorem. It does not infer any mathematical impossibility from bounded
refinement failure. This source and both roots were already completely
represented in the accepted v2 source-specific register, so this is
**zero new original-source closure** and no required PB-007 proof
obligation discharge.

## Machine evidence, adversaries and finite cost

- [Executable exact source-bound verifier](verify_pb00701_v17_negative_multiplier_sign_erasure.py):
  hashes the unchanged frozen Git blob, validates its 121 unique case IDs,
  exactly twenty historical route-refused and thirty missing-order
  dispositions, the chosen canonical source and row SHA-256, full controls,
  actual phase/knot/interval, and the matching 50-ID v2 register. Checks
  physical Fourier reconstruction, exact radical bracket inequalities,
  knot and tail bounds, and the saved claim/zero-delta receipt.
- [Machine-readable receipt](pb00701-v17-negative-multiplier-sign-erasure.json):
  two simple physical events with strict rational isolators, physical and
  carrier sign orientations, refused shortcut, before/after population
  identity and explicit nonpromotions.
- Run `python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v17_negative_multiplier_sign_erasure.py --contract --self-test`.
  Tests reject changed harmonic controls, phase, knot, interval, source
  ID, historic refusal, root multiplicity/sign/bracket, forged blocker
  closure or capability promotion. Separate prospective rational controls
  cover order-two tangency, a pair of roots only `2^-99` apart and the
  all-zero identity; none enters the frozen denominator.
- The verifier is bounded by two small read-only JSONs (121/50 records,
  350kB per input), exact rational operations and at most fifteen
  deliberate adversarial mutations. Root finiteness and signs follow from
  the analytic argument above, not from resource bounds, a scan or timeout.
  Full v2 producer replay and static registry checks are run separately
  by focused CI.

| Unchanged population | Before | After | Delta |
|---|---:|---:|---:|
| Frozen original source cases | 121 | 121 | 0 |
| Historical route refusals | 20 | 20 | 0 |
| Historical missing ordered premises | 30 | 30 | 0 |
| Preexisting complete source-specific witnesses | 50 | 50 | 0 |

Changed historical IDs: `[]`. Current evidence is **DETERMINISTIC_MODEL**,
not native geometry, independent geometry oracle or engineering STEP. No
changes to the 26 supported operations, source journal, durable bodies,
topology, raw failures, native/paid permits or production authorization.
PB-007-01/02/03/04 and PO-02/04/05/07/08 remain OPEN; MC-B and MC-1
remain `NOT_ESTABLISHED`.

**Next critical path:** independently validate and integrate this scoped C
only after exact-head review and CI, then pursue a **reusable**
nonconstant-amplitude multi-span event and physical source-side sign
composition theorem with explicit multiplier sign and zero-jet premises.
