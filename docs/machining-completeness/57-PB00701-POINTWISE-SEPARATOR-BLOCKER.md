# PB-007-01 v31 — exact pointwise separator synthesis blocker

**RAG: AMBER for the investigated repair; RED for the full PB-007-01 obligation.**

PB-007-01 remains OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`. The machining-domain denominator remains frozen at 26 operations. Complete v8–v30 authority retains strict precedence.

## Investigation result

V31 investigated removing v30's separate global Bernstein `D_floor/T_ceiling` conservatism inside the existing exact v29 1/16-turn algebraic phase cells. Existing authority is sufficient to verify a candidate rational separator but is not sufficient to synthesize the required separator for the general pointwise-safe source family under the issue's finite-termination contract.

For a supplied rational `m`, existing exact authority can independently prove `m>tan(pi/8)=sqrt(2)-1` using `(m+1)^2>2`, form both source polynomials `sign(D)D-m*T` and `sign(D)D+m*T`, and discharge strict positivity with MC-032 rational endpoint/Sturm authority. The diagnostic `D=1+2s`, `T=2+3s`, `m=5/12` demonstrates this: v30's separate global Bernstein ratio is `1/5`, while the two pointwise margins are `1/6+(3/4)s` and `11/6+(13/4)s` and are exactly positive.

That diagnostic separator is **not** promoted. Caller-supplied or fixed rational separators remain non-authoritative.

## Missing theorem/algorithm authority

The missing exact operation is source-owned algebraic separator synthesis. A general implementation needs to derive the critical-value equations for `sign(D)D/|T|`, isolate and order the relevant real algebraic critical values on closed `[0,1]`, compare the exact minimum with `sqrt(2)-1`, and construct a rational strictly between those algebraic values with a termination bound derived from canonical source data.

The current MC-032 Sturm stack decides sign/root questions for rational polynomials after all rational coefficients are known. It does not expose resultant/subresultant critical-value elimination, algebraic-number root isolation/ordering against `sqrt(2)-1`, or a qualified finite rational-between-algebraics constructor. Consequently a numerical minimum, sampling, approximate root ordering, unbounded continued fraction/bisection, or search stopped by denominator/depth/timeout/resource limits cannot be substituted.

A coefficient-correlated Bernstein interval can certify a partial subset, but it is not the general pointwise-safe source family required by #225 and therefore is not promoted as v31 authority.

## Fail-closed boundary

Exact separator equality and pointwise polynomial-margin equality fail closed. The diagnostics retain exact `70/169 < sqrt(2)-1 < 169/408` controls and `m=1/2` margin equality with signed `±1/1000000` rational neighbours. Unsupported exact algebraic ordering and exact-resource refusal remain refusal, not evidence.

## Next repair

The next prerequisite is an exact algebra package for rational-function critical points/values, real-algebraic isolation and ordering, and finite rational-between-algebraics separator synthesis. After that is qualified, PB-007-01 pointwise projective integration can resume without numerical or resource-bounded truth authority.

V27 certificate-cut composition, v29/v30 phase/projective authority, endpoint/root/multiplicity semantics, protected source/audio/provenance, canonical journal, exact time/path/phase, source uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain unchanged. No native, paid, production or expensive campaign is authorized.
