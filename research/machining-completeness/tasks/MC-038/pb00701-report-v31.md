# PB-007-01 v31 — pointwise projective-separator synthesis investigation

Issue: #225  
Parent integration gate: MC-038 / #100  
Source baseline: `c5b11f6a168bcf4108b05f1432466ac9a30c763d`

## Decision

PB-007-01 remains **OPEN**. V31 does not add executable event-certification authority. The requested pointwise source-dependent separator route reaches a precise theorem/algorithm boundary in the current exact stack, so the correct outcome is a fail-closed blocker rather than an approximate separator or another fixed-slope theorem. MC-B and MC-1 remain `NOT_ESTABLISHED`; the machining-domain denominator remains frozen at 26 operations.

## What existing authority can prove

V30 already proves exact strict positivity of a rational polynomial margin once a rational separator `m` is supplied, using finite sign orthants and MC-032 endpoint/Sturm authority. It also compares a supplied rational exactly against `tan(pi/8)=sqrt(2)-1` using `(m+1)^2 > 2`.

The diagnostic source

`D(s)=1+2s`, `T(s)=2+3s`

makes the remaining gap concrete. Exact Bernstein data are `[1,3]` and `[2,5]`, so v30's separate global sufficient ratio is only `1/5` and blocks. Nevertheless the diagnostic rational `m=5/12` is exactly above `sqrt(2)-1`, because `(17/12)^2-2=1/144`, and both exact margins are strictly positive:

- `D-(5/12)T = 1/6 + (3/4)s`;
- `D+(5/12)T = 11/6 + (13/4)s`.

MC-032 certifies both. This shows that the unresolved step is not polynomial positivity for a known rational separator.

## Precise missing operation

The repository does not currently expose a qualified finite source-owned operation that computes the exact admissible separator interval for the general pointwise-safe case. The missing chain is:

1. construct the exact critical-value problem for `sign(D)D(s)/|T(s)|`, including transverse zeros and both signs;
2. eliminate/source-isolate its algebraic critical values by resultant/subresultant or equivalent exact authority;
3. order those real algebraic values on closed `[0,1]` against `sqrt(2)-1`;
4. construct a rational `m` strictly between the algebraic phase boundary and the exact minimum with a termination bound derived from canonical integer/rational source data;
5. feed that source-derived `m` into the already-qualified finite orthant/Sturm residual proof.

Current MC-032 authority performs the final decision for a **supplied rational polynomial margin**. It does not provide the critical-value isolation/root-ordering/rational-between-algebraics synthesis required by steps 1–4.

A coefficient-correlated Bernstein construction is a useful partial sufficient family, but it is not the general pointwise-safe synthesis requested by #225. Promoting a diagnostic fixed rational, sampled minimum, numerical trigonometry, unbounded continued fraction/bisection, or a rational search stopped by denominator/depth/timeout/resource budget would violate the acceptance contract.

## Boundary checks

The focused diagnostics retain exact controls: `70/169 < sqrt(2)-1 < 169/408`; exact separator-margin equality at `m=1/2` fails closed; `m=1/2 ± 1/1000000` gives the expected strict inside/outside behaviour for `D=1,T=2`; exact resource refusal remains non-truth-valued; and the complete v30 historical verifier still runs before the v31 blocker checks.

## Routing

The next dependency-ready corrective work is therefore a prerequisite exact-algebra package: qualify rational-function critical-point/critical-value construction, real-algebraic root isolation and ordering against `sqrt(2)-1`, and a finite rational-between-algebraics constructor. Only after that authority exists should the pointwise v31 integration be retried. PB-007-01 itself remains open throughout.

Protected source/audio/provenance, canonical journal, exact time/path/phase, source uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, conventional STEP semantics, v27 certificate-cut composition, v29/v30 phase/projective authority and endpoint/root/multiplicity semantics are unchanged. No native, paid, production or expensive campaign is authorized.
