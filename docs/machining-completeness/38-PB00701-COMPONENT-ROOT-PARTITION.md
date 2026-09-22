# PB-007-01 v12 — exact finite component-root partition

## Contract

This document records a bounded constructive extension of PB-007-01 after v11. It applies only to an exact non-common **single-harmonic** span with exact rational-polynomial components `A` and `B`, `gcd(A,B)=1`, and nonzero exact-rational affine phase. It removes the requirement that one projective component be globally zero-free by building a finite exact rational component-root partition.

It does not narrow the supported machining domain and does not close PB-007-01.

## Root partition

Use MC-032 exact Sturm authority on `A*B`. Every distinct source root is isolated into a rational closed neighborhood containing exactly one root of exactly one component; endpoint roots receive exact rational one-sided neighborhoods. Internal partition boundaries are exact rational non-roots. The remaining complementary cells contain no component root. Coprimality forbids coincident `A/B` roots and any attempted coincidence fails closed.

The cells cover the complete source span exactly. No epsilon gap, sampled sign, approximate algebraic root, timeout or resource limit is correctness authority. Resource exhaustion remains `RESOURCE_REFUSAL`, not a truth value.

## Local delegation

For a cell `[l,r]`, reparameterize exactly with `s=l+(r-l)t`. Polynomial coefficients and affine phase are transformed using rational arithmetic only. Existing v10 dual-projective authority is attempted first. v11 phase-dominance authority may replace only the exact derivative-monotonicity residual it already owns. Tangent/cotangent poles, rational-turn boundary comparisons, endpoint semantics and multiplicity contracts remain unchanged.

Because every cell has at least one component with no root on its closed interval, every qualified cell has an exact zero-free tangent or cotangent denominator. If a local cell still cannot satisfy v10 or v11 derivative authority, v12 remains blocked rather than inventing a numerical decision.

## Component-root events

Write projective phase as `u=2*h*theta_turn`.

At an `A=0` root, the original event requires `u in Z`. At a `B=0` root, it requires `u in Z+1/2`. Nonzero rational affine phase makes every phase-lattice candidate source rational. Every candidate within the exact root-isolating neighborhood is evaluated against the component polynomial exactly. If none is a component root, the isolated component root is exactly a non-event; this includes algebraic-irrational roots without approximating them.

A qualified component-root event is simple. Multiple-root cancellation would force pi to equal an exact rational number (`-A'/(u'B)` or `B'/(u'A)`), contradicting irrationality of pi. This remains true when the component polynomial itself has a repeated root.

## Shared boundaries

Internal partition boundaries are non-component-roots but may be original-event roots. Adjacent v10/v11 cell decisions may both report the same boundary event. v12 maps cell-local endpoints back to the exact parent source parameter and deduplicates by exact rational source before aggregating distinct events. No tolerance-based identity is used.

## Gate state

PB-007-01 remains **OPEN**. PB-007-02 remains dependent; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04, PO-05 and PO-08 remain OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`.

The frozen 26-operation denominator and protected source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain unchanged. No native, paid, production or expensive campaign is authorized by this repair.
