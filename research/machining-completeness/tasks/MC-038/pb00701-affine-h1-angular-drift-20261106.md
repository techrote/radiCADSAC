# MC-038 / PB-007-01: exact oriented affine H1 angular-drift event theorem

**Status:** bounded source-bound positive mathematical research, **not achieved A/B/C blocker closure or MC-B gate**. **Evidence:** DETERMINISTIC_MODEL. **Date:** 6 November 2026. Parent: MC-038 issue #100.

## Hypothesis, falsifiers, named obligation

PB-007-01 / PO-04, PO-05 and PO-08 remain OPEN. A finite exact rational angular-derivative witness can certify complete physical signed events for a new restricted **orientation-preserving** H1 coefficient pair, without discarding its sine channel or relying on numerical root scanning. Refuse unchanged premises whenever the original source, phase, amplitude nonvanishing, knot continuity, strict derivative sign, strict angular drift bound or endpoint sign is unproved. A failed sufficient condition is not mathematical nonmonotonicity or impossibility.

## Frozen original source identity, semantics and prior art

- Historical missing-ordered source: composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail0; source SHA-256 4d1ef1cbecceeb4a43b4e30fd37327fa204164cc9ce25dfe4f1744a052cebcc2; original [0,2], true knot 1, phase turns t/8; C1=t-1/2 on [0,1], C1=1/2 on [1,2], S1=1 throughout, H0=0.
- Historical V43-refused harvested source: harvested:verify_pb00701_v9:4e7b85fa122a; source SHA-256 a83ca0cd16c7822e6525f8f2d2df26a54f45b99807cadebc67f31fc49b066c10; original [0,1], no internal knot, phase turns t/8; C1=1, S1=t-1/2.

Frozen v54 Git blob 5841c331579489b25caef38cd412bdbf286f9134; original-source V2 register Git blob e52d3baf3692a011cf86234eeaa992ef407d99fd. The verifier reconstructs and checks all 121 original case identities, all 50 complete V2 source identities and complete selected original-source/row hashes. Both selected originals **already possess signed complete V2 witnesses**. Accepted V9 ratio-prefix composition predates this research. A second demonstration of their zero sets is not a new historical case closure.

## Admitted grammar and exact mathematical proof

Source time is [0,1] or [0,2] with physical knot t=1, original phase beta=t/8 turns, theta=pi*t/4. Only cosine and sine H1 coefficients C(t), S(t), each rational affine on the physical original source spans, are admitted, plus an optional identically zero H0. Exact original degree 0/1 B-spline controls and clamped physical knots must match, including knot continuity. No extra harmonics, unknown phase, other degrees, amplitude shared zero, zero endpoint/knot, continuum or unproved tangency are admitted.

On a unit original source span use local u=t-a. Define C=c0+dc*u, S=s0+ds*u, q=C^2+S^2, W=c0*ds-s0*dc. Compute exact q_min and q_max on [0,1] from rational endpoints plus the rational quadratic vertex -B/A when interior, where A=dc^2+ds^2 and B=c0*dc+s0*ds. Require q_min>0, so the H1 vector has a continuous orientation phi and F=C*cos(theta)+S*sin(theta)=sqrt(q)*cos(delta), delta=theta-phi. Differentiating exactly, delta'=pi/4-W/q.

Use the strict rational bounds 3<pi<22/7, so 3/4<pi/4<11/14. The following sufficient cases rigorously establish angular orientation:

- W<0: delta strictly increasing, with 0<delta'<11/14+(-W)/q_min.
- W>=0 and 3/4-W/q_min>0: delta strictly increasing, with 0<delta'<11/14.
- W>=0 and 11/14-W/q_max<0: delta strictly decreasing, with 0<abs(delta')<W/q_min-3/4.

Every admitted upper rational bound must be strictly below 3. Each span has source length 1, so its total strict angular drift is less than 3<pi. Thus strictly monotone delta can encounter **at most one** cosine zero per open span. If encountered, its derivative cannot vanish: sqrt(q)>0, sin(delta) is +1 or -1, and delta' has strict sign. Hence the root is simple, multiplicity 1, and flips the signed physical cell.

Signs at exact original source boundaries are **rational**, without floating-point trigonometry: F(0)=C(0); F(1) has sign C(1)+S(1) (positive factor sqrt(2)/2); F(2)=S(2). All must be nonzero for required boundaries. Opposite source-piece endpoint signs prove exactly one simple interior root, by continuity and the root bound. Equal nonzero signs prove none. The two-span original coefficient continuity and same physical phase permit maximal signed cells to join over a verified nonzero true knot. The root coordinate is a unique implicit open interval, not a fabricated rational root. Exact finite quadratic extrema and finitely many rational comparisons prove termination for accepted instances; arithmetic/budget refusal is NONTRUTH, never a no-root verdict.

The theorem is sufficient only for this restricted grammar. Identity zero, shared amplitude zeros, tangencies, unproven angular inequalities, zero knots/endpoints and other multiharmonic/phase cases remain OPEN outside its scope.

## Exact original predictions

Frozen V9 two-span source: first-span W=-1, q_min=1, q_max=5/4 and increasing delta with upper drift bound 25/14<3; the second span has W=0, q=5/4, increasing delta with upper bound 11/14. Exact physical signs at 0,1,2 are NEGATIVE,POSITIVE,POSITIVE. Thus exactly one simple root in (0,1), zero in (1,2), no knot root, and two maximal cells NEGATIVE then POSITIVE.

Frozen harvested V43-refused source: W=+1, q_min=1, q_max=5/4. Upper derivative bound 11/14-4/5=-1/70 proves decreasing delta; absolute drift bound is 1/4<3. Both endpoint signs are POSITIVE, hence no physical roots and one positive cell. This does not promote the historical generic V43 owner into a certified route.

## Adversarial controls and extremely close roots

Positive and negative tests include exact originals, rational phase/knots/source tampering, coefficient continuity, extra harmonics, changed degree, shared amplitude identity or tangency, zero physical endpoints and knot, very large rational denominators, duplicate JSON keys, deep nesting, giant integers, false production/PB claims and resource-bounded refusals.

One separate prospective two-span source has C=-1 and S=(1+epsilon)t for 0<=t<=1, then S=1+epsilon-(2+epsilon)(t-1) for 1<=t<=2, with epsilon=2^-120, h=2^-100 and original phase theta=pi*t/4. Endpoint/knot signs are NEGATIVE,POSITIVE,NEGATIVE. Each strict derivative certificate gives one simple root. Exact angle-sum inequalities establish F(1-h)<0 and F(1+h)<0, so the two distinct roots lie in (1-h,1) and (1,1+h), separated by <2^-99. The right-hand sign follows from sin(pi*h/4)<11h/14, cos(pi*h/4)>99/100, and a checked negative rational upper bound. No numerical scan or tolerance proves these events. This prospective control is not a new historical source.

## Reproduction, census and gates

From repository root run the exact original source verifier with --contract --self-test, the unchanged full v54/v2 producing reconciliation --contract, and tools/validate_machining_completeness.py. Dedicated GitHub Actions separately validates the literal exact-head Python theorem/controls, all 50 original V2 source witnesses and global MC-1 authority. The receipt uses strict canonical JSON comparison and bounded byte/nesting/numeric/duplicate-key decoding. Do not mistake green CI for native qualification.

The matched original historical census remains **121 frozen originals; 20 historical route refusals; 30 missing ordered owner premises; 50 complete V2 source-specific witnesses**, all before=after and **delta 0**, newly uniquely closed original IDs empty, required PB/PO discharges 0. This is a generic *restricted theorem candidate*, not achieved A/B/C without a genuinely newly missing owner-to-consumer source interface or full required obligation discharge.

PB-007-01/02/03/04, PO-02/04/05/07/08 OPEN. MC-B, MC-1 NOT_ESTABLISHED. DETERMINISTIC_MODEL, no native geometry/independent oracle/engineering STEP. All 26 machining operations, journal, durable body and topology semantics, original source provenance and independent conventional STEP obligations unchanged; no paid/native campaign or production authorized.
