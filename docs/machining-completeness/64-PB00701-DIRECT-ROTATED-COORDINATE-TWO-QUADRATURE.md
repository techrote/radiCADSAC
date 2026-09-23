# PB-007-01 v38 — direct rotated-coordinate two-quadrature authority

PB-007-01 **remains open**. MC-B and MC-1 remain `NOT_ESTABLISHED`; the machining-domain denominator remains frozen at **26 operations**.

V38 is a bounded exact extension of v37. It removes the nonconstant shared-factor prerequisite and operates directly on source-owned exact rational selected-harmonic quadratures `C_h(s)` and `S_h(s)`. It regenerates `A=(C+S)/2`, `B=(C-S)/2`, `A'=(C'+S')/2`, and `B'=(C'-S')/2` from source coefficients. Caller rotated-coordinate, derivative, sign, cell, bound, margin, root, or multiplicity metadata is non-authoritative.

On the preserved diagonal phase cell `-3/16+k/2 <= h*phi <= -1/16+k/2`, set `X=cos(theta)+sin(theta)` and `Y=cos(theta)-sin(theta)`. V38 uses only the established exact rational bounds `|X|<99/182`, fixed-sign `|Y|>2856/2197`, `|Y|<99/70`, and `2*pi>6`. The complete selected-harmonic derivative is retained exactly as

`A'(s)*X + B'(s)*Y + 2*pi*h*r*(A(s)*Y-B(s)*X)`.

Equivalently this is `C'(s)cos(theta)+S'(s)sin(theta)+2*pi*h*r[-C(s)sin(theta)+S(s)cos(theta)]`. Both selected amplitude derivatives remain materially represented by the rotated derivative pair; neither is discarded or accepted from caller authority.

MC-032 exact endpoint/Sturm authority proves `A(s)>0`, both phase-gap polynomials `A*2856/2197-sigma_B*B*99/182>0`, and every complete sign-orthant margin `6*|h*r|*P_sigma-sigma_Ap*(99/182)*A'-sigma_Bp*(99/70)*B'-sum sigma_i*R_i>0` on the complete closed span. Equality and exact resource refusal fail closed. No sampling, numerical trigonometry, binary-float authority, epsilon/tolerance, approximate minimization/root ordering, arbitrary subdivision/refinement depth, timeout, denominator cap, or resource budget becomes truth authority.

The primary acceptance source is the genuinely coprime pair `C_1=1+6s/5`, `S_1=11/10+6s/5`, phase interval `[-3/16,-1/16]`, plus a live non-anchor harmonic. Complete v37 authority is explicitly checked to block it because its canonical polynomial GCD is the constant `1`; v38 derives `A=21/20+6s/5`, `B=-1/20`, `A'=6/5`, and `B'=0` and certifies the complete event. A secondary coprime source `S_1=11/10+7s/6` exercises nonzero `A'` and `B'` simultaneously.

Adversarial controls cover both phase-rate directions and opposite diagonal cells; exact cell, `A>0`, phase-gap, and complete-margin equality with signed rational `1/1000000` neighbours; zero/open/left-endpoint/right-endpoint outcomes; zero quadratures and unsupported cells; forged rotated-coordinate/derivative/cell/bound/margin/root authority; source-coordinate mismatch; binary floats; exact resource refusal; and exact historical v30/v34/v35/v36/v37 precedence with v33 blocker evidence pinned.

All protected source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume material, cutter/holder, durable-body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain unchanged. No native, paid, production, or expensive campaign is authorized.

After verified v38 landing, the next repair must be chosen only from the residual PB-007-01 blocked family. It must remain a bounded exact theorem repair rather than a broad rediscovery pass or premature MC-B retry.
