# MC-038 / PB-007-01 — exact V44 higher-harmonic root-coordinate falsification

**7 November 2026 · Source-bound C negative result · DETERMINISTIC_MODEL · Draft research, no merge or capability claim.**

## Objective and precisely bounded proposed route

Reject the proposed *direct event-coordinate substitution*:

> Delete the tiny nonzero H2 cosine term from the exact historical V44 source; isolate the resulting H1-only root, then consume that same root coordinate as the exact physical zero of the unchanged original H1+H2 source.

The shortcut is not asserted to exist in a currently accepted V44 implementation. This investigation tests **that precisely specified candidate route**; it does not refute the historical V44 source-specific root proof, a legitimate perturbation-certified interval method, or the possibility of a general terminating analytic event theorem.

**Named obligations:** PB-007-01 and dependent PO-04/05/08 ordered physical zero identity, root multiplicity, and sign transfer. Parent [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). The *historical* V44 route refusal specifically states \`ALGEBRAIC_ORIENTATION_COORDINATE_CERTIFIED_BUT_EXACT_CONSUMPTION_AUTHORITY_MISSING\`. We do not close this source route by finding another already-known zero.

**Authority:** [AGENTS.md](../../../..//AGENTS.md), [DR-0026](../../../../docs/decisions/DR-0026-machining-completeness-programme.md), [current authority](../../../../handoffs/current-authority.json), [MC-1 programme](../../../../docs/machining-completeness/00-PROGRAMME.md), [execution protocol](../../../../docs/machining-completeness/07-EXECUTION-PROTOCOL.md), [roadmap](../../../../docs/machining-completeness/12-ROADMAP.md), [current-state ledger](../../../../docs/machining-completeness/77-MC038-CURRENT-IMPLEMENTATION-STATE.md) and [frozen frontier](pb00701-post-v54-frontier-audit.md). Accepted main at research start \`48222d6c40b15ad42cc36d56e6d25f3b284e7fc9\`. Existing PR #397 alone owns main integration; the separately running \`Continue radiCADSAC\` worker and existing PRs have no overlapping write set.

## Authenticated historical source and input semantics

**Case ID:** \`harvested:verify_pb00701_v44:ffaea08e30c9\`.

- Source-spec SHA-256 \`d3b3a90024ea283dfd96811b8fc2b66ceff621b3b48defc44c77f85557adbba2\`.
- Whole frozen-row SHA-256 \`7423adadf8c52ff28d47d9f63effbc5a2a7a630bdaf7efe6f8eeb1d2a85c5600\`.
- Immutable V54 corpus Git blob \`5841c331579489b25caef38cd412bdbf286f9134\`; original V2 reconciliation blob \`e52d3baf3692a011cf86234eeaa992ef407d99fd\`.
- **Original parameter** \`pb00701-v44-algebraic-orientation\`, domain [0,1]. This is **not** relabeled \`source-time-t\`.
- One true clamped quadratic source span, knot vector [0,0,0,1,1,1] for H1; zero *internal* source knots. H2 cosine is degree zero, knot vector [0,1], control \`1/100000000\`.
- Affine phase in turns \(\beta(t)=-1/8+t/16\); physical angle \(\theta(t)=2\pi\beta(t)=-\pi/4+\pi t/8\).
- H1 cosine degree-two Bernstein controls \((-3/2,-1,3/2)\); H1 sine controls \((-1/2,-1,1/2)\).

The exact controls expand (not approximate) to

\[
C(t)=-\tfrac32+t+2t^2,\qquad
S(t)=-\tfrac12-t+2t^2,\qquad \epsilon=\tfrac1{100000000}.
\]

Thus the actual original physical event function and the proposed reduced function are

\[
F_\epsilon(t)=C(t)\cos\theta(t)+S(t)\sin\theta(t)
                  +\epsilon\cos(2\theta(t)),\qquad
F_0(t)=C(t)\cos\theta(t)+S(t)\sin\theta(t).
\]

The accepted V2 register already contains a **COMPLETE_SOURCE_SPECIFIC** zero-set witness for this same original case, retaining the old V54 refusal. This investigation may not double-count its preexisting proof as a newly resolved original.

## Exact falsification, sign order and termination proof

For \(0\le t\le1\), \(-\pi/4\le\theta(t)\le-\pi/8\). In particular \(\cos\theta>0\); for **every** strict interior \(t\), \(\cos(2\theta)>0\), though \(\cos(2\theta(0))=0\). Divide the physical function by its positive \(\cos\theta\), and define

\[
G(t)=C(t)+S(t)\tan\theta(t),\qquad
H(t)=\frac{\cos(2\theta(t))}{\cos\theta(t)}
     =2\cos\theta(t)-\sec\theta(t).
\]

Then \(F_\epsilon(t)=0\) iff \(G_\epsilon(t)=G(t)+\epsilon H(t)=0\). In the strict interior, \(0<H(t)<1\). This already proves that an H1-only zero \(r_0\) cannot be a zero of the original \(F_\epsilon\) for any nonzero \(\epsilon\): \(G_\epsilon(r_0)=\epsilon H(r_0)\ne0\).

The result is stronger: **both zero sets contain exactly one simple root, and the two exact source coordinates are strictly ordered**. This follows without any numerical scan.

1. \(C'=1+4t\), \(S'=4t-1\). Since \(-1\le\tan\theta<0\), for \(t\le1/4\), \(C'+S'\tan\theta\ge1\), while for \(t\ge1/4\), \(C'+S'\tan\theta\ge C'-S'=2\). Also \(S(t)\ge-5/8\), \(\sec^2\theta\le2\), \(0<\theta'=\pi/8<1/2\). Therefore
   \[
   G'=C'+S'\tan\theta+S\sec^2\theta\,\theta'
   >1-\frac{5\pi}{32}>\frac38.
   \]
2. \(H'=\theta'(-\sin\theta)(2+\sec^2\theta)\) satisfies \(0<H'<2\). For any rational \(|\epsilon|\le1/100\),
   \[
   G_\epsilon'>\frac38-\frac2{100}=\frac{71}{200}>\frac13.
   \]
   This proves strict monotonicity and rules out multiple roots, order-two tangencies and identity zero *within this fixed admitted grammar*.
3. \(G_\epsilon(0)=-1\), because \(H(0)=0\); \(G_\epsilon(1)>1-1/100>0\). Continuity and strictly positive derivative prove exactly **one interior simple zero** for the H1-only and for every admitted nonzero-\(\epsilon\) source, with physical signs **NEGATIVE, POSITIVE**.
4. Let \(r_\epsilon\) and \(r_0\) denote these unique source-parameter roots. If \(\epsilon>0\), then \(G_\epsilon(r_0)=\epsilon H(r_0)>0\), hence \(r_\epsilon<r_0\). If \(\epsilon<0\), the strict order reverses. If \(\epsilon=0\), they coincide. The mean-value theorem, \(H<1\), and \(G_\epsilon'>1/3\) give
   \[
   0<|r_\epsilon-r_0|<3|\epsilon|\quad(\epsilon\ne0).
   \]

For the **actual frozen original** \(\epsilon=1/100000000>0\), the exact event order is therefore

\[
0<r_{\mathrm{full}}<r_{\mathrm{H1-only}}<1.
\]

Both roots are simple, but **the H1-only coordinate is not an exact root of the original V44 physical function**. The number of roots is the same; this falsification is about **exact source-bound root identity/consumption**, not a change in root count, or proof that small harmonics cannot be treated by any rigorously bounded perturbation method.

For a separate *prospective* rational \(\epsilon=2^{-300}\), the distinct roots are closer than \(3\,2^{-300}<2^{-298}\), yet remain unequal by the same proof. Finite numerical precision cannot justify treating them as identical. The \(\epsilon=0\) positive control returns exact coincidence; negative epsilon reverses the root ordering. These perturbed coefficients are **not** additional historical original IDs.

**Termination and refusal:** This theorem uses a finite analytic inequality chain, rational arithmetic and the standard \(3<\pi<4\), with no bisection, sign-change scan, iteration count or runtime cap used as a truth criterion. The verifier checks the exact original source hashes, finite rational bounds and all 50 prior IDs. It emits an **implicit unique simple root** with an open rational domain bracket (0,1), not a fabricated rational coordinate. Other harmonic grammars, tangencies, identity-zero requests and \(|\epsilon|>1/100\) are explicitly **NONTRUTH refusals**; no unproved universal statement follows.

## Reproduction and machine evidence

Run on this branch:

~~~sh
python3 research/machining-completeness/tasks/MC-038/pb00701_v44_h2_root_coordinate_20261107.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py
~~~

The [machine-readable receipt](pb00701-v44-h2-root-coordinate-20261107.json) preserves all **50** exact previously unresolved case IDs, original spec/row hashes and unchanged dispositions; checks equal pinned Git blobs and the replayed V2 evidence union. No frozen v54 test or V2 source is modified.

| Matched frozen measure | Before | After | Delta |
|---|---:|---:|---:|
| Original sources | 121 | 121 | 0 |
| Historical uncertified routes | 20 | 20 | 0 |
| Missing ordered premises | 30 | 30 | **0** |
| Already COMPLETE_SOURCE_SPECIFIC in V2 | 50 | 50 | 0 |
| REQUIRED PB/PO discharges | 0 | 0 | 0 |

**New historical closures: none.** The V44 original had prior complete V2 evidence. C is achieved only against the precisely stated *discard-and-reuse* route. It is not an A reduction, a B full required proof discharge, a criticism of a current accepted V44 theorem, or an independent native geometry/engineering STEP oracle.

## Retained blockers and downstream implications

PB-007-01/02/03/04 and PO-02/04/05/07/08 remain **OPEN**. The missing general analytic event/isolation theorem and original-source consumer remain unproved, especially source-knot, endpoint, tangency, identity-zero and multiharmonic exact sign transfer. A defensible next method is a **validated perturbation bracket and unique-root consumer** that preserves original H2 in the final equation, not coordinate substitution from a reduced model. That route would require its own proof and source-level review.

MC-B and MC-1 remain \`NOT_ESTABLISHED\`; all **26** supported lathe/mill operations, native material/topology, durable journal/bodies, engineering STEP, and explicit separate production authorization remain unaffected. No proof/programme authority or shared current-state ledger is changed. This is additive research and the original retained negative evidence survives.
