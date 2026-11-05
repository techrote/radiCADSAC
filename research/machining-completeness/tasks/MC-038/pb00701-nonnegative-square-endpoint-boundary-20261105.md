# MC-038 / PB-007-01 — Exact original-source negative-endpoint boundary for direct nonnegative square coverage

**Date:** 5 November 2026 UTC. **Evidence class:** DETERMINISTIC_MODEL. **Result:** bounded source-matched falsification (candidate C), **not** a frozen-case closure or required PB-007 proof discharge.

**Repository:** [techrote/radiCADSAC](https://github.com/techrote/radiCADSAC). **Parent:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). **Exclusive disjoint research reservation:** [#324 / 6650503491](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6650503491). **Source-selection main:** \`2ab90bd3ec684f92830b9863ab870bdbe188c1b5\`.

## Falsifiable candidate, precise theorem scope and why this matters

Candidate **DIRECT_NONNEGATIVE_SQUARE_COMPONENT_COVERAGE_OF_ALL_FROZEN_V54_BLOCKED_ORIGINALS** would generalize positive moving/stationary squared-amplitude roots by directly representing **every one of the actual 50 historically blocked source functions**, unchanged in original physical sign, as a finite sum of real squares
\[
F(t)=\sum_{j=1}^m R_j(t)^2,\qquad R_j(t)\in\mathbb{R},
\]
on the original source-time domain. No additional negative sign, signed multiplier, residual or transformed output would be allowed. **A strictly negative original physical endpoint is a decisive falsifier.** The proof is elementary but critical: every real square is nonnegative at every point; their sum cannot equal a negative physical value.

This universal candidate is **not claimed by [concurrent PR #397](https://github.com/techrote/radiCADSAC/pull/397)**. That PR explicitly admits only a rational affine, two-span square-decomposition grammar and correctly makes no historical case-closure claim. This independent research challenges *only* an extrapolation to all source grammars, not the correctness of #397, its exact proof, or any actual accepted solver. It leaves signed multipliers, indefinite decompositions, other exact event methods and general analytic-event decidability untouched.

## Exact original-source physical expression

Each frozen source has an original parameter \`source-time-t\`, rational closed interval \([L,R]\), rational affine global phase in **turns** \(\beta(t)=b+rt\), and clamped original rational B-splines for each integer harmonic \(h\geq0\):
\[
F(t)=\sum_h C_h(t)\cos(2\pi h\beta(t))
       +\sum_h S_h(t)\sin(2\pi h\beta(t)).
\]

For a fully clamped degree-\(d\) original B-spline, the one-sided exterior value at \(L\) equals its **first original control**, and at \(R\) its **last original control**. The executable verifies the complete original knot vector, nondecreasing knots, exact \(d+1\) endpoint repetitions, matching source extent and canonical rational controls. It does not rely on a fabricated split-source or a numerical sample.

An endpoint \(e\in\{L,R\}\) is rationally decidable here only when \(4h\beta(e)\in\mathbb Z\) for **every harmonic channel** in the original source. Write \(q=(4h\beta(e))\bmod4\). Then the exact cosine sequence for \(q=0,1,2,3\) is \((1,0,-1,0)\) and sine is \((0,1,0,-1)\). Consequently, the literal original endpoint is a finite **rational sum** of original clamped controls multiplied by \(\{-1,0,1\}\). No approximation to \(\pi\), interval scan, floating-point threshold or root finder enters any accepted negative decision. Nonquarter-turn endpoints are explicitly **indeterminate** in this screen; no sign or root conclusion is inferred.

## Three independent physical-source anchors

| Actual frozen original source ID | Source SHA-256 | Exact original value |
|---|---|---|
| \`composite:DELEGATED_V6_CONSTANT_MODULATION:tail0\` | \`9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1\` | \(F(2)=-1\) |
| \`composite:PB00701_V14_EXACT_STRICT_DOMINANCE_MULTITERM_MULTIPLIER:tail100\` | \`bd10ad1d9503335b2d7f745c09805b82a421b8db7beea67329cf33d0c9d78ff2\` | \(F(0)=-5/6\) |
| \`composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail0\` | \`9abbed355812241cdef20f3ce3b3522619bdd682c3a73fb01828d8f95c72f0af\` | \(F(2)=-1/2\) |

For V6 tail0, original source-time \(t\in[0,2]\), actual knot \(t=1\) and \(\beta(t)=t/4\). Original cosine \(H_0=0,H_1=1\). Hence \(F(2)=\cos(\pi)=-1\). For V14 tail100, global phase at the original left endpoint is zero. The original harmonic cosine controls for \(H_0,H_1,H_3,H_5\) are \(0,-7/12,-1/12,-1/6\), giving \(-5/6\). For V8 tail0, original phase turns at \(t=2\) are \(3/4\): the right-endpoint sine \(H_1\) control \(1/2\) multiplies \(\sin(3\pi/2)=-1\), giving \(-1/2\). The complete receipt and independently recomputing verifier retain exact original source and row hashes, every negative case ID and all side contributions.

## Source-matched 50-original result and acceptance

The pinned *historical* original corpus Git blob is \`5841c331579489b25caef38cd412bdbf286f9134\` (\`pb00701-finite-owner-corpus-v54.json\`). The pinned existing complete-source evidence registry is blob \`e52d3baf3692a011cf86234eeaa992ef407d99fd\` (\`pb00701-post-v54-evidence-reconciliation-v2.json\`). The verifier checks each source, whole original row, exact ID, old disposition, original origin/phase/interval and the existing 50-case source-specific registration. There are 121 unique original IDs, 20 historical route refusals and 30 distinct missing ordered premises. The complete registry ID set equals the blocked ID set; those 50 cases already have source-specific witnesses.

On this **unchanged** population, the exact endpoint screen proves **22 distinct original blocked case IDs** have at least one strictly negative physical original endpoint: **10/20 historic uncertified-source routes**, and **12/30 historic missing-ordered-premise cases**. These are the specific IDs pinned in the machine receipt, not a new denominator. This is a **lower bound** on physically sign-negative originals, since the other endpoints may have nonquarter phases or be nonnegative at the endpoint while becoming negative inside. None of the 22 becomes a newly solved historical source or an accepted generic route. The original historical refusals remain frozen.

| Frozen measurement | Before | After | Delta |
|---|---:|---:|---:|
| Distinct original sources | 121 | 121 | 0 |
| Historical uncertified source routes | 20 | 20 | 0 |
| Missing ordered physical premises | 30 | 30 | 0 |
| Already complete source-specific witnesses | 50 | 50 | 0 |

Newly resolved historical IDs: **[]**. Only the proposed universal *direct real nonnegative-square* route is decisively excluded, because even **one** of these authenticated strict negatives cannot be such a sum.

## Termination, adversarial controls and custody

The algorithm makes at most **100 original endpoint checks** after reading a fixed 121-row corpus and 50 registered cases, with finite rational arithmetic and integer quarter-turn evaluation. The original control vectors and harmonics are finite; the proof of strict negativity is a complete exact arithmetic identity for each admitted endpoint. Bounded source input and rational bit-size checks fail **closed**, not as a truth value. All selected negative claims require exact literal original source SHA-256 and whole-row SHA-256 bindings to the pinned v2 registry.

The verifier challenges original-control mutation, global phase mutation, knot alteration, source parameter mutation, historical disposition mutation, forged negative ID sets, fictitious census reduction and production promotion. A nonquarter phase is refused for endpoint sign, and exact zero controls are not promoted to negative signs. A rational sign inequality at separation \(2^{-80}\) is only an arithmetic control: it does **not** claim to isolate any close physical roots or settle tangencies/identity-zero events. Those root obligations remain independent and open. Positive values on any checked endpoint are not zero-free certificates.

Reproduce from repository root:

\`\`\`sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_nonnegative_square_endpoint_boundary.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py
\`\`\`

A dedicated workflow checks literal-head checkout and runs all three. Retain any failed exact-head runs and correct source before a distinct-session review, guarded merge and merged-main requalification. No reviewer should infer separate-human approval from an AI-assisted owner-account comment.

## Nonclaims, dependencies and next required work

**Result C is a narrow negative-method result only.** It says nothing about whether signed carriers, rational polynomial root methods, general trigonometric-polynomial methods, conditioned derivative proofs or original-source piecewise analytic event algorithms could solve the 50 sources. It neither proves a generic impossibility nor discharges REQUIRED PB-007-01/02/03/04 or PO-02/04/05/07/08. MC-B and MC-1 remain **NOT_ESTABLISHED**. Evidence remains **DETERMINISTIC_MODEL**, not independent oracle, native geometry or actual engineering STEP.

This explicitly preserves the full **26 supported machining operations**, durable bodies, canonical intent journal, lineage, topology, conventional engineering STEP, and all native/expensive and production restrictions. No production repository, paid/native campaign or narrowed domain is authorized.

**Next critical-path mathematical direction:** retain physical signed germ and sign-transfer information while building genuinely general nonconstant-amplitude, multi-span physical event completion, including true source-knot sides, tangencies, close roots and identity-zero continua. #397's narrowly admitted positive sum-of-squares theorem can remain useful on its own grammar; it cannot be extrapolated to this observed signed frozen population without additional exact reasoning. Coordinate owner release before any integration or #100 comment.
