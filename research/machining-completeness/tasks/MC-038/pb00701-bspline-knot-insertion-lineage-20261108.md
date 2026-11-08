# MC-038 / PB-007-01 — exact B-spline knot-insertion lineage and physical-event invariance

Status: **new bounded research-only deterministic-model candidate, Draft / no merge** (8 November 2026). Parent: [#458](https://github.com/techrote/radiCADSAC/pull/458) at \`7c3d2f8aa510ab61d04ae7eb6611e77983ba397e\`, relying on independently qualified #453, #455, #457. Owner integration of accepted \`main\` is separately reserved under #397. This leaf owns only its new code/report/workflow; it must not promote any MC-1 or PB obligation.

## Problem and falsifier

The exact rational spline compiler in #458 treats knots of the **supplied** control/knot vector as structurally genuine, whereas a spline can be **refined** by inserting a knot without changing any coefficient function. An inserted knot is genuine in the new representation, but its coordinate was *not* present in the pre-edit knot vector. It is not evidence of a knot in a frozen historical original, even when its refined certificate is mathematically complete.

**Hypothesis:** One exact rational interior Boehm insertion in one coefficient field H0/C1/S1/C2/S2 preserves all five polynomial coefficient functions, hence the complete moving H0/H1/H2 physical root set and signs. Original/refined identities must remain distinct where their source documents differ, and a typed receipt must identify pre-edit structural knots separately from newly introduced ones.

**Falsifiers:** A changed coefficient polynomial on any newly partitioned span, changed certified physical root count, incorrect pre-edit knot membership, receipt substitution or promotion to historical provenance; malformed/over-budget source and uncertified physical events must refuse without a truth certificate.

## Exact algorithm and proof

For a clamped rational degree-\(p\) spline with knot vector \(U=(u_i)\), controls \(P_0,\ldots,P_n\), interior insertion \(t\), old multiplicity \(s\), and last span index \(k\) with \(u_k\le t<u_{k+1}\), the updated knot vector inserts \(t\) immediately after \(u_k\). The new controls are

\[
P_i'=\begin{cases}
 P_i & i\le k-p,\\
 (1-\alpha_i)P_{i-1}+\alpha_i P_i & k-p+1\le i\le k-s,\\
 P_{i-1} & i\ge k-s+1,
\end{cases}
\qquad
\alpha_i=\frac{t-u_i}{u_{i+p}-u_i}.
\]

The denominator is required strictly positive. This is the exact Boehm/de Boor single-knot insertion identity; the degree-zero case reduces to duplicating the owning piece's control. All arithmetic is \`fractions.Fraction\`; canonical rational encoding, control count and maximum multiplicity are rechecked by the preexisting #458 parser.

**Independent proof check:** Both pre-edit and post-edit vectors are independently lowered by #458's rational Cox–de Boor/Newton polynomial compiler. For **every** resulting new source span, this leaf identifies exactly one covering old span and compares all five full rational power-basis coefficient tuples for literal equality. That check covers the entire source interval, not sample points. It independently catches an implementation error in the Boehm recurrence or in span allocation. Since the five coefficient functions and unchanged affine phase are identical at every \(t\), the full physical function

\[
F(t)=H_0(t)+C_1(t)\cos(\pi\beta(t))+S_1(t)\sin(\pi\beta(t))
+C_2(t)\cos(2\pi\beta(t))+S_2(t)\sin(2\pi\beta(t))
\]

is identical before/after refinement; root locations, zero multiplicities and signed open physical cells cannot change. Both parent complete event certificates are separately replayed using #458's verifier. Their rational partition boundaries **need not** be bit-for-bit identical: splitting a source span may change certificate subdivision while preserving the exact mathematical event set. The bounded producer nevertheless checks that both complete certified physical root counts agree.

## Source/provenance contract

One insertion is accepted per receipt; no unbounded plan iteration. The consumer fixes and verifies the supplied source SHA-256 before/after, derived polynomial-piece SHA-256 before/after, typed insertion point and field, old/new field multiplicities, pre-edit/post-edit **supplied** structural knot witnesses, complete independently certified physical events and the exhaustive span-refinement equality witness.

A coordinate absent from a field's pre-edit vector has \`new_coordinate_in_field=true\`; insertion at an already existing internal knot increments multiplicity but has \`new_coordinate_in_field=false\`. The new source vector may have more structural knots even though its physical function is unchanged. **Neither SHA-256 nor this transcript proves membership in the frozen V54 historical original corpus.** A supplied document is only that supplied document.

Mutation controls reject fraudulent original-corpus membership, invented historical closure, boolean/integer confusion, changed source digest/field/refinement proof or nested event certificates. The source-to-refined transformation, source identities, lineage claims and exact polynomial-refinement witnesses are deterministically reconstructed during verification. Both supplied parent event certificates are independently replay-verified against their respective source identities rather than regenerated by costly event search; a valid alternate certified partition is permissible.

## Bounded admission and negative results

Uses #458's degree \(\le3\), at most four combined source spans, 24 controls per coefficient, bounded rational input and H0/H1/H2 moving-affine phase. This leaf admits only an interior single insertion with available multiplicity; exceeding support, going past the four-piece union bound, a contact that the parent's complete certifier cannot prove after splitting, or an exhausted proof budget are typed **NONTRUTH refusals**. A failed post-insertion proof is not evidence that knot insertion changed the mathematical function.

The positive fixtures include insertion into a genuine degree-two double-knot source with moving H1/H2 second-order tangency, and a degree-zero constant coefficient insertion. Repeated seeded rational tests independently challenge degree 0–3 basis invariance, including pre-existing source knots and inserted coordinates. This is a research representation/provenance result, not a native-geometry measurement, independent STEP oracle, general NURBS-weight algorithm, knot deletion, B-rep topology or manufacturing implementation.

Frozen V54 before/after **121 originals / 20 historical route refusals / 30 missing ordered premises**. Frozen V2 retains **50 already complete source-specific witnesses**. Newly closed original IDs [], required PB/PO discharges 0; MC-B and MC-1 remain \`NOT_ESTABLISHED\`, production unauthorized. The new proof does not make either frozen corpus a more complete historical corpus.

## Reproduction and handoff

Run from repository root:

\`\`\`sh
python3 research/machining-completeness/tasks/MC-038/pb00701_bspline_knot_insertion_lineage_20261108.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/pb00701_genuine_bspline_knot_bridge_20261108.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py
\`\`\`

The dedicated literal-head Actions workflow runs these checks and inherited second-order/zero-knot/generic event tests. Keep Draft/unmerged until all terminal workflows have been inspected and a **separate-session source-critical mathematical review** has admitted the corrected head. Main integration must respect existing ownership and dependency order.