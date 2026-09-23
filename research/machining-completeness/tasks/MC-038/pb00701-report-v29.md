# PB-007-01 v29 — exact 5-12-13 nested algebraic phase-cell projection certificate

## Decision

PB-007-01 **remains OPEN**. MC-B and MC-1 remain `NOT_ESTABLISHED`; the frozen machining-domain denominator remains 26 operations. V29 adds one exact sufficient route for residual multi-harmonic spans still blocked after complete v8–v28 authority. It does not alter protected source/audio/provenance or downstream semantics.

## Exact 1/16-turn authority

V29 uses nested rational-turn phase cells whose endpoints are `pi/8` from a quadrature maximum. On COS-dominant cells `[-1/16,1/16]+k` and `[7/16,9/16]+k`, the dominant endpoint magnitude is `cos(pi/8)=sqrt(2+sqrt(2))/2` and the transverse endpoint magnitude is `sin(pi/8)=sqrt(2-sqrt(2))/2`. The symmetric SIN-dominant cells are `[3/16,5/16]+k` and `[11/16,13/16]+k`.

The algebraic comparison is reduced exactly to rational arithmetic. The common inequality `sqrt(2)>238/169` follows by squaring positive quantities: `2>(238/169)^2`, equivalently `57122>56644`. Therefore

- `cos(pi/8)>12/13`, because `(2+sqrt(2))/4 > 144/169`;
- `sin(pi/8)<5/13`, because `(2-sqrt(2))/4 < 25/169`.

No floating-point trigonometry or approximate algebraic comparison participates in correctness.

For a fixed-sign dominant source component `D`, transverse component `T`, and retained residual polynomials `R_i`, v29 proves every finite sign orthant of

`6|hr|((12/13) sign(D)D - (5/13) sigma_T T) - sum sigma_i R_i`

strictly positive on closed `[0,1]` using MC-032 exact endpoint/Sturm authority. Together with `2*pi>6`, this proves a fixed nonzero complete derivative. Both selected-harmonic amplitude derivatives, harmonic-0 derivative, and all non-anchor harmonic derivative channels remain explicit residuals.

## Materially broader acceptance family

The deterministic acceptance source uses harmonic-0 constant `-19/10`, `C_1=9/5`, genuinely source-modulated `S_1=1+s/100`, tiny active `C_2=1/10000`, and phase `0 -> 1/16` turn. Complete v8–v28 remains blocked: in particular the v28 rational projection margin already fails at the left endpoint because `(6/7)S_1-(1/2)C_1 = 6/7-9/10 < 0`. V29 instead has `(12/13)S_1-(5/13)C_1 = 3/13 > 0` at the same endpoint, retains `S_1'=1/100` and the h=2 contribution as explicit residuals, and certifies the event with preserved exact endpoint/root semantics.

The adversarial boundary covers exact 1/16-turn cell endpoints and `±1/1000000` neighbours, exact projection equality and neighbours, exact residual-L1 equality and neighbours, positive/negative phase rates, S- and C-dominant orientations, positive/negative quadrature cells, an unsupported wider nested cell, forged caller algebraic/cell/separation/root metadata, binary floats, source-coordinate mismatch, exact resource refusal, historical v28 precedence, frozen 26-operation coverage, and false MC-B promotion. The complete v28 verifier is rerun, preserving the v27 certificate-cut composition and internal root/multiplicity semantics transitively.

## Residual blocker / next routing

PB-007-01 remains OPEN after v29. Residual spans include phase intervals outside the finite exact algebraic cells and coupled projections whose strict uniform separation cannot be reduced to current rational-polynomial sign authority. This is not an impossibility theorem.

The next repair should attempt an exact projective mixed-phase comparison only if it remains finitely terminating and reducible to current rational/algebraic sign authority. A useful target would avoid another merely nested fixed-angle bound by deriving a source-dependent projective cone whose separation polynomial can be certified directly. If that requires genuinely new transcendental minimization/zero theory, non-representable cuts, or approximate root ordering, record that theorem boundary rather than substituting numerical approximation or retrying MC-B.

Protected source/audio/provenance, canonical journal, exact time/path/phase, source uncertainty, positive-volume material, cutter/holder, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain unchanged. No native, paid, production, or expensive campaign ran.
