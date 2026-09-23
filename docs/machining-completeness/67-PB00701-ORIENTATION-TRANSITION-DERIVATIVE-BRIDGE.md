# PB-007-01 v42 — exact rotated-coordinate orientation-transition derivative bridge

## Scope

This bounded repair supplies the missing local theorem exposed by #245 / closed PR #246. Cutting a closed source span at an exact zero of `A=(C+S)/2` or `B=(C-S)/2` does not make the adjacent closed child admissible under complete v39/v40, because those routes require strict orientation and strict phase-gap positivity at both closed endpoints. v42 therefore proves the complete physical derivative through an orientation transition rather than changing endpoint topology.

PB-007-01 remains open. MC-B and MC-1 remain `NOT_ESTABLISHED`; the domain remains the frozen 26 operations.

## Exact construction

For a selected harmonic define

`A=(C+S)/2`, `B=(C-S)/2`, `X=cos(theta)+sin(theta)`, `Y=cos(theta)-sin(theta)`.

The physical derivative is retained exactly:

`D=A'X+B'Y+2*pi*h*r*(A Y-B X)`

plus every non-anchor derivative residual. On a supported diagonal phase cell, existing exact authority provides a fixed sign for `Y` and rational bounds

- `|Y| > 2856/2197`,
- `|X| < 99/182`,
- `|Y| < 99/70`.

v42 derives strict sign of source-owned `B'` with MC-032 endpoint/Sturm authority. It orients the complete derivative by `sign(B')*sign(Y)` and proves every finite sign orthant of

`|B'|*(2856/2197) - |A'|*(99/182) - (44/7)*|h*r|*(|A|*(99/70)+|B|*(99/182)) - sum_i |R_i| > 0`.

The exact rational theorem `2*pi < 44/7` is the same upper bound already recorded by the v29 nested phase-cell authority for adverse phase terms. No numerical trigonometry, sampling, epsilon neighborhood, tolerance, or arbitrary subdivision cap is used.

The selected `C'` and `S'` channels are consumed only through the regenerated rotated identity. Selected phase channels remain jointly represented by `A Y-B X`; every non-anchor residual remains explicit.

## Acceptance source

The primary exact source uses

- `A=s-1/2`, with a simple interior zero at `s=1/2`;
- `B=10(s-1/3)`, with an interior zero at `s=1/3` and strict `B'=10`;
- therefore `C=-23/6+11s` and `S=17/6-9s`;
- phase law `phi=-1/8+s/1000`, wholly inside the supported diagonal cell.

Complete v40 remains blocked because neither whole-span signed-A nor signed-B orientation is available. The v42 full-derivative bridge is strictly positive on the complete closed source span and proves the event decision without creating a proof cut or physical event.

## Boundary and adversarial contract

Tests cover the exact orientation zero, both strict `B'` orientations, loss of strict `B'`, phase-cell boundaries and just-outside rational neighbors, forward/reverse phase laws, the opposite diagonal projection cell, non-anchor residual retention, forged proof metadata, exact resource refusal, historical v40 precedence, strict-margin fail-close behavior, and MC-B/MC-1 non-promotion.

Proof bookkeeping never changes root/event multiplicity. Any exact resource refusal remains non-truth and propagates fail-closed.

## Protected semantics

Source/audio/provenance semantics, journal semantics, exact time/path/phase semantics, material and cutter/holder semantics, body/lineage semantics, refusal semantics, conventional STEP semantics, and downstream semantics are unchanged. The v42 theorem is proof-only authority for PB-007-01 and does not authorize production or expensive execution.

## Relationship to #245

v42 is a prerequisite repair for #245. It establishes a closed transition neighborhood theorem that #245 can later compose with strictly oriented children. It does not by itself complete #245, PB-007-01, MC-B, or MC-1.
