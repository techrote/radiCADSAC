# MC-038 / PB-007-01 — exact two-span source-knot root-set composition

**Status:** bounded deterministic-model research candidate  
**Date:** 30 October 2026  
**Parent:** #100  
**Preselection:** https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6511778291  
**Exact base:** `6aeed5f5ae45c2d9f5ad917d34424f2c91bf485d`

## Live gap

PR #307 established exact span-local shadow evidence for frozen v54 case
`composite:DELEGATED_V6_CONSTANT_MODULATION:tail0`, but deliberately left the
shared physical source-knot root as two span-local endpoint records. It did not
claim either a global multi-span root count or source-knot deduplication.

The original frozen source is one exact source parameter
`source-time-t in [0,2]`, phase turns `t/4`, constant H1 cosine amplitude
1. Its two exact B-spline source spans meet at `t=1`.

## Theorem

This candidate composes the **root set**, not a global smooth derivative model.

First, the landed #307 source-bound replay must certify every span-local route.
Each route must expose a complete exact count of roots strictly inside its own
open source span.

The original local polynomial amplitude coordinates are then converted exactly
back to the original source coordinate. For a source span `[L,R]` with local
coordinate `s=(t-L)/(R-L)`, every rational polynomial `p(s)` is expanded
exactly as `p((t-L)/(R-L))`. Endpoint evaluations are independently checked
before the reconstructed source-coordinate analytic span is used.

The landed #298 `compose_knot` primitive then checks the two reconstructed
source spans at their common original source coordinate. It requires:

- the same exact source coordinate and affine phase;
- exact cyclotomic equality `F_L(k)=F_R(k)`, rather than sign-only continuity;
- exact ZERO status on both sides;
- exact left and right first-nonzero derivative orders;
- exact one-sided physical signs;
- one physical source-knot zero; and
- no global smooth multiplicity claim.

The two exterior source endpoints are also checked independently with #298.

For exactly two adjacent spans, the distinct closed-source root set is therefore

`left-open + right-open + exterior-left + exterior-right + one shared knot`.

The two local endpoint root records at the join are deduplicated because they
are the same original source parameter value and #298 proves the analytic values
coincide exactly there. Their one-sided derivative orders stay separate.

## Frozen result expected

For the pinned frozen source:

- left open-span roots: 0;
- right open-span roots: 0;
- exterior endpoint `t=0`: exact positive nonroot;
- exterior endpoint `t=2`: exact negative nonroot;
- shared source knot `t=1`: exact one physical zero;
- left/right one-sided orders: `[1,1]`;
- physical signs: `[+,-]`;
- event kind: `CROSSING`;
- exact global distinct closed-source root count: **1**.

The historical v54 disposition remains **BLOCKED**.

## Falsifiers

The verifier rejects/refuses:

- source-coordinate gap or overlap;
- source parameter mismatch;
- global affine-phase mismatch;
- exact discontinuity at the source join;
- nonzero or zero/nonzero-mismatched join;
- span-local #307 route not certified;
- missing or negative exact open-span root count;
- exact local-polynomial -> source-coordinate substitution mismatch;
- unresolved exterior point;
- source/report mutation;
- binary or noncanonical rational authority;
- forged root count/dedup/capability fields; and
- drift in the #307/#298 proof chain, corpus, domain or authority.

A synthetic exact join with left order 2 and right order 3 must remain one
physical root while retaining both one-sided orders separately. It is
deliberately **not** assigned a global smooth multiplicity.

## Custody

Direct pins:

- landed #307 span-local shadow model:
  `a6ad0144a241d1e914d8862f4f1e0c8600a1a923`;
- landed #298 exact rational-phase point/knot primitive:
  `9fc344e045fa800fb24d30902a641e534a1e197b`;
- exact trigonometric interval engine:
  `2320f92efe4316d865a89f6d848737e2c000ca4d`;
- frozen v54 corpus:
  `5841c331579489b25caef38cd412bdbf286f9134`;
- 26-operation domain:
  `23de82f5240a72509f7afe4acd5948b65bc4ff13`;
- no-production authority:
  `fa0233323a0804d8a5d3eb7cd892a274a6173fab`.

The #307 model rechecks its own transitive V27/V26/V6/#298/event-engine custody.

## Strict nonclaims

This is a bounded **two-span root-set composition theorem** only.

It does not:

- rewrite or admit the historical v54 case;
- claim a global analytic/smooth multiplicity at the source knot;
- claim a global multiple-root count at the nonsmooth join;
- generalize to more than two source spans or more than one source knot;
- certify unresolved span-local routes;
- solve algebraic V41 child-boundary composition;
- establish PB-007-01, MC-B or MC-1;
- qualify native material/topology/lineage, B-rep or usable engineering STEP; or
- authorize production.

The 26-operation domain and all protected
source/provenance/phase/canonical-journal/material/body/lineage/refusal/
UNCERTIFIED/conventional-STEP semantics remain unchanged.

## Reproduction and landing gate

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_two_span_source_knot_root_set.py --contract --self-test
```

Landing requires literal final-head focused success, `mc1-static`, distinct
technical/source review of that exact head, expected-head-protected merge,
reviewed/synthetic/landed tree identity, and actual merged-main focused/static
push success.
