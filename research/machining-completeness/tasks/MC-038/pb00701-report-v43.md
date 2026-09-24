# PB-007-01 v43 — exact correlated closed-handoff derivative certificate

Status: **bounded exact handoff authority established; PB-007-01 remains OPEN; MC-B / MC-1 remain NOT_ESTABLISHED**.

## Why v43 exists

Verified v42 repaired the zero-adjacent closed-span failure that blocked the original v41 attempt, but #245 then exposed a second handoff problem. The existing v42 and v39 strict dominance certificates cannot both hold at one common closed endpoint: with `L=2856/2197` and `W=99/70`, their necessary overlap would require `(44/7)W^2 < 6L^2`, while the exact difference is

`(44/7)W^2 - 6L^2 = 100719037899/41389887175 > 0`.

The analogous v42→v19 strict-envelope handoff also cannot overlap because v42 requires the h0 derivative residual below `L|B'|`, whereas v19 requires it above an oscillatory derivative bound of at least `2|B'|`, and `L<2`.

V43 does not weaken either theorem. It replaces the need for overlapping certificates with one correlated certificate on the handoff child.

## Correlated theorem

For a selected harmonic,

`D=A'X+B'Y+2*pi*h*r*(A Y-B X)+retained residuals`,

with `X=cos(theta)+sin(theta)` and `Y=cos(theta)-sin(theta)`.

On a verified diagonal phase cell write `Y=d|Y|`, with

- `|Y| > L = 2856/2197`;
- `|X| < U = 99/182`;
- `|Y| < W = 99/70`.

V43 derives a weak closed sign for source-owned `A`: endpoint zeros are allowed, but an interior root is not. It chooses `eta` so `eta*h*r*A >= 0` and orients the derivative by `eta*d`. Then

`eta*d*D = eta*B'|Y| + 2*pi*eta*h*r*A|Y| + eta*d*X*A' - 2*pi*eta*d*X*h*r*B + residuals`.

The key difference from v42 is that the `A Y` phase term is retained as a **favorable correlated Y-channel contribution** whenever its exact source sign aligns with the orientation:

`2*pi*eta*h*r*A|Y| >= 6 L eta*h*r*A`.

The `B'Y` contribution is also retained with its source-derived weak sign: use `L eta B'` when favorable and `W eta B'` when adverse. `A'X`, `B X`, and every non-anchor derivative term remain adverse and are discharged by finite exact rational-polynomial sign orthants using `2*pi<44/7`. Strict equality fails closed.

## Genuine #245 handoff acceptance

The exact parent source uses

- `C_1=-3/10+17s/20`;
- `S_1=1/20+3s/20`;
- tiny non-anchor `C_2=1/100000000`;
- therefore `A_1=-1/8+s/2`, with the source-owned orientation root `s=1/4`;
- `B_1=-7/40+7s/20`, with a separate root at `s=1/2`;
- phase law `phi=-1/8+s/16`, wholly inside the supported diagonal cell.

Complete v42 blocks the parent. V43 also refuses to relabel the parent because `A` has an interior root.

Partition exactly at `s=1/4`:

- the closed left child `[0,1/4]` is certified by complete predecessor authority through v42;
- the closed right child `[1/4,1]` is still blocked by v42, but its local `A=3u/8` has a weak positive sign with an exact zero only at the handoff endpoint, so v43 certifies its complete derivative;
- historical v27 endpoint/root/multiplicity composition recombines both closed children into a certified parent event;
- the handoff endpoint is not a physical event root and contributes zero to the composed root count.

Thus the acceptance demonstrates exactly what #250 required: new closed-handoff authority needed by #245, rather than a standalone local inequality.

## Adversarial boundary

The executable suite covers exact strict-margin equality and rational neighbors, phase-cell endpoints and just-outside points, forward/reverse exact parameter direction, endpoint orientation zero and near-handoff sign controls, interior sign loss, exact resource refusal, forged caller metadata, binary-float rejection, retained non-anchor residuals, historical v42 precedence, proof-cut event neutrality, genuine physical-cut single counting, and the recorded v42/v39-v19 incompatibility regressions.

## Programme preservation

V43 is a bounded sufficient theorem. PB-007-01 remains OPEN; PB-007-02 remains dependent; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04/05/08 remain OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`; the frozen machining-domain denominator remains 26 operations.

Protected source/audio/provenance, canonical journal, exact time/path/phase, source uncertainty, positive-volume material, cutter/holder, durable-body/lineage, refusal/`UNCERTIFIED`, conventional STEP and downstream semantics are unchanged. No native, paid, production or expensive campaign is authorized.
