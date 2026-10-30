# MC-038 / PB-007-01 — exact source-coordinate sign at frozen V44 irrational cut

**Status:** bounded research candidate, 30 October 2026. Exact final-head CI/review/merge qualification outstanding. **Owner:** [MC-038 issue #100](https://github.com/techrote/radiCADSAC/issues/100). **Base:** main 300c867b16d0647498a600c18e7de79254329379 following [PR #315](https://github.com/techrote/radiCADSAC/pull/315). **Evidence:** deterministic model, not native geometry or physical oracle.

## Gap and falsifiable hypothesis

Historical [V45](pb00701_algebraic_child_map_model.py) constructs exact Q(alpha) child representations for the frozen V44 original rational source but **defers irrational-phase trig endpoints**. [PR #315](https://github.com/techrote/radiCADSAC/pull/315) transports monotonicity through that actual field and uses the preserved V46/atlas nonzero sign to allocate one physical root. This experiment tests an independent **nonzero sign witness** using only original rational-source trig enclosures and algebraic isolating intervals. A source/field mismatch, nonstrict enclosure or failed exact replay must never yield a certified sign.

Frozen V44 original source is [0,1], phase o=-1/8 and r=1/16 turns per unit, harmonics P1=-3/2+t+2t², Q1=-1/2-t+2t², P2=1/100000000, Q2=0. Canonical source SHA-256 d3b3a90024ea283dfd96811b8fc2b66ceff621b3b48defc44c77f85557adbba2. The V41/V45 proof cut alpha is the unique positive root of 2 alpha²−1=0, exact embedding initially isolated in (1/2,3/4). Historical V45 producer Git blob c055e7f392a921b386a1a99cc70b5004121ae7f6. Previous bridge producer Git blob 850fc287a92bc57420c51848f21e51b7571a07a9 transitively pins the corpus, original source/phase, domain, authority, exact V41/V46 cut identity and root atlas. Neither predecessor nor historical evidence is edited.

## Exact source-coordinate proof

For the exact original-source function

F(t) = sum_h [P_h(t) cos(2*pi*h*(o+r*t)) + Q_h(t) sin(2*pi*h*(o+r*t))],

rebuild a global rational first-derivative magnitude bound

M1 = sum_h [||P'_h|| + ||Q'_h|| + (44/7)*|h*r|*(||P_h||+||Q_h||)]

with coefficient l1 norms on a radius covering the original source. The bound follows from 2*pi < 44/7 and absolute sine/cosine bounds of one, then is checked against the independently constructed original-source span m1. No caller-provided derivative bound is trusted.

For the exact Sturm-isolated alpha in (l,u), choose rational q=(l+u)/2. The original rational-phase evaluator supplies an outward rational enclosure [A(q),B(q)] containing F(q). The mean-value theorem certifies

F(alpha) in [A(q)−M1*(u−l)/2, B(q)+M1*(u−l)/2].

A strictly positive lower endpoint or strictly negative upper endpoint is a valid independent physical nonzero sign certificate. Otherwise bisect the algebraic polynomial isolator, using exact endpoint signs and fresh Sturm uniqueness, and repeat. Only 0–32 bisections are admitted; unresolved sign is RESOURCE_REFUSAL. There is **no** irrational trig evaluation, binary-float estimate, epsilon sign test or fabricated algebraic-child zero solver.

The strict physical sign is calculated without the inherited V46/atlas sign. Only after computation is it compared against the preserved sign as a cross-check; disagreement is BLOCKED. A certified sign is not an independent complete-root proof and cannot replace the pinned source atlas.

## Controls, reproducibility, limitations

Adversarial tests cover actual V44/V45 source/field binding; every exact rational transport and Sturm bracket; positive and negative synthetic original-source polynomial functions; zero, near-zero and limited-budget refusals; invalid budget/domain; forged Lipschitz bound, field embedding, source identity, enclosure, signs and gate status; source pin drift; and malformed oversized/deep/cyclic reports.

Crucial exact-zero falsifier: F(t)=2t²−1 on [0,1] is exactly zero at this algebraic alpha. All midpoint/radius transported enclosures must include zero. This experiment deliberately refuses after exhausting its finite budget: it does not classify zero as a nonzero event, and a failure to decide does not disprove equality. A tiny nonzero value can also remain unresolved within finite resources or the underlying fixed trigonometric enclosure precision.

Run on exact checkout:

    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v44_irrational_cut_source_sign.py --contract --self-test

The focused workflow must check out literal PR head and print its SHA; mc1-static, exact-head technical review, source-tree comparison, expected-head merge and merged-main CI remain mandatory.

## Open theorem boundary

A successful frozen nonzero physical sign witness does not establish a general V41/V47 endpoint-zero/equality/multiplicity decision, arbitrary-source derivative/critical-point partition, multi-cut algebraic-field compositum or terminating child analytic event interface. Historical frozen v54 V44 stays BLOCKED, PB-007-01 stays OPEN, MC-B and MC-1 stay NOT_ESTABLISHED. All 26 supported machining operations, real manufacturing histories, journal, source/phase/provenance, disconnected bodies, lineage/certificates and usable conventional STEP remain mandatory. No native material, B-rep, STEP, paid campaign, production bootstrap or handoff is authorized by this result.
