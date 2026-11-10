# B5 — Open-cell positivity does not preserve square-lift zeros across a knot

**10 November 2026 · Research-only · Draft/HOLD.** Source-critical, exact-rational interop falsifier, **not** a defect in either authored theorem, a new machining/solver acceptance result, or a claim of original mathematical novelty.

## Exact inspected source and governance

- Accepted [radiCADSAC main](https://github.com/techrote/radiCADSAC/commit/48222d6c40b15ad42cc36d56e6d25f3b284e7fc9) `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`; [CyberSand main](https://github.com/techrote/cybersand/commit/d4b18e7f06839b35c8f6a66195206da0f33c5fa3) `d4b18e7f06839b35c8f6a66195206da0f33c5fa3`. Both verified through live branch resources. Inspected both `AGENTS.md`, radiCADSAC current-authority, DR-0026, MC-1 protocol, #100/#324, #397/#453/#462, CyberSand's authoritative native World and pressure/worker policy.
- [A1 #470](https://github.com/techrote/radiCADSAC/pull/470), head `42da787b96a815418e26d2f055f1770dcfd466a6`: [`square_lift.py`](https://github.com/techrote/radiCADSAC/blob/42da787b96a815418e26d2f055f1770dcfd466a6/research/experimental/analytic-events/isolator/square_lift.py) Git blob `7f429a5732e23d19c607efb428bbcec6ed1629e7`. Its `positive()` requires **every** Bernstein coefficient to be strictly positive. That is a sufficient proof of positive multiplier on the **closed** cell.
- [B1 #473](https://github.com/techrote/radiCADSAC/pull/473), head `4ecf9087a642456a486d53402e6588ab801ccdc4`: [`certificate_algebra.py`](https://github.com/techrote/radiCADSAC/blob/4ecf9087a642456a486d53402e6588ab801ccdc4/research/experimental/certificate-algebra/core/certificate_algebra.py) Git blob `d366679ccbd1f57a3c8058857162e74df8efd178`. Its `kind(b) == "POS"` allows nonnegative Bernstein coefficients with at least one positive. This proves strict positivity only **inside** the cell; endpoint zeros are permitted and correctly represented by B1. [B1 product-cone](https://github.com/techrote/radiCADSAC/blob/4ecf9087a642456a486d53402e6588ab801ccdc4/research/experimental/certificate-algebra/core/product_cone.py) remains a *rational-polynomial* algebra, not a proof of arbitrary H1/H2 compositions.
- [B2 #556](https://github.com/techrote/cybersand/pull/556) `f0585227`, [B3 #555](https://github.com/techrote/cybersand/pull/555) `acf7ce6e`, [B4 #554](https://github.com/techrote/cybersand/pull/554) `23742c8c`; source-typing and native admission remain separate unresolved requirements. All remain Draft.
- At the inspected literal heads: 17/17 ordinary radiCADSAC CI workflows successful for A1/A2/B1/B5; two CyberSand docs/source checks successful and two native/GDExtension workflows intentionally skipped per B2/B3/B4 head. **These workflows do not establish independent execution of standalone research scripts or native parity.**

## Exact interop counterexample and proof

For **every integer k >= 3**, let `u=t-k`, `c=k+1/2`, and
`G(t)=sin(pi*t)-t*cos(pi*t)` on `[k,k+1]`. Choose the genuinely piecewise C0 multiplier

- `P_L(u)=1/2-u` on `[0,1/2]`: Bernstein coefficients `(1/2,0)` on the normalized half-cell;
- `P_R(u)=u-1/2` on `[1/2,1]`: Bernstein coefficients `(0,1/2)`.

Both are **valid B1 `POS` pieces**: positive in each *open* half-cell and C0 at their shared seam. But `P(c)=0`, while `G(c)=(-1)^k != 0` follows exactly from half-integer trigonometry. Therefore `F(t)=P(t)G(t)^2` has an **additional knot zero** `F(c)=0` not present in G. Because `P'_L(c)=-1` and `P'_R(c)=+1`, the new zero has opposite sided first derivatives and a derivative jump of **+2**, a non-crossing C0 contact. This is a direct falsifier of any *proposed* coercion `B1.POS -> A1.CLOSED_STRICT_POSITIVE_MULTIPLIER`.

It is **not** a counterexample to B1 (which preserves endpoint zero facts), nor A1 (which deliberately refuses these non-strict Bernstein vectors). It is not based on numeric root sampling: the identities hold for an infinite integer family. The included [independent stdlib checker](test_closed_positivity_seam.py) uses exact `Fraction` Bernstein conversions and k=3..32 adversarial controls; its **2/2 tests executed locally and passed**. It reconstructs the visible predicate logic; neither author's exact module was imported or executed.

Reproduce from the repository root:

```sh
python3 -m unittest -v research/experimental/ab-campaign/integration/test_closed_positivity_seam.py
```

## Proposed bounded reusable law and required falsifier

Use a separate **`CLOSED_NONVANISHING_MULTIPLIER`** proof premise, with authenticated original producer, phase/physical-coordinate normalization and **both sides of every seam and external endpoint**. Only under `m(t) != 0` everywhere on the domain does `Z(mG²)=Z(G)`. For a merely nonnegative `m`, `Z(mG²)=Z(m) union Z(G)`; any new knot zero requires its own sided-germ certificate. The strict closed Bernstein cone `all(b_i>0)` is a *sufficient* condition, not a complete positivity decision procedure. It is classical Bernstein/zero-set reasoning; the contribution here is an explicit source-typed interop falsifier.

**One next high-value adversary:** ask A3/B1 to replay this knot-zero case with the **actual pinned A1 and B1 modules**: B1 should accept the two `POS` leaves, A1 must refuse them as square-lift multipliers, and any bridge retaining the unmodified G root list must refuse. Also distinguish independently held original spline-control/window pins from self-asserted envelopes. No author changes or gate promotions are prescribed by this report.

## Compact source-critical discovery/performance matrix

| Lane | Result, prior art and falsifier | Disposition |
| --- | --- | --- |
| A1 | Restricted algebraic-time events, [H2 square-lift](https://github.com/techrote/radiCADSAC/pull/470) with transcendental contact; classical algebra/transcendence, not general isolation. Closed-vs-open positivity is an interop trap | Theorem conditional GO; adapter HOLD |
| A2 | Exact local rational-phase cyclotomic jets/knot germs, standard annihilator/transcendence ingredients; A3's bounded-reversal fix at [#471](https://github.com/techrote/radiCADSAC/pull/471) not independently fully tested | Conditional GO; source/producer HOLD |
| A3 | Independent adversarial root, source-size and phase challenges | Next challenge: actual producer-to-joined-knot case |
| B1 | Classical Bernstein C1/C2, exact rational product and phase-unit bridge; **`POS` is open-cell, not closed-domain nonvanishing**. External pin custody and native B-spline producer authenticity missing | Scoped GO; interop HOLD |
| B2 | Conditional synchronous bounded-radius sparse research; deep-freeze corrected, exact-module test and native dependency closure pending. **3.089x high-churn abstract cost** retained | Runtime HOLD |
| B3 | Conditional one-writer quantity conservation; source snapshot/historical-only receipt corrected. B4's **unsigned-IN seed** counterexample and ABA/native authority outstanding | Consumer HOLD |
| B4 | Existing #470 historical bench-canvas collider-packet stage p50 **94.41%/94.07%**; full-simulation p50 only **2.49%/1.04%** and zero-packet negative control changes, no new native gain | Historical stage GO only |
| B5 | Conditional complete-dependency proof and new exact boundary-interoperability falsifier; no live consumer | Draft/HOLD |

## Stop, invariants and scope

The common theorem seam is **proof-premise completeness at the consumer**: open-cell sign is not closed-domain nonvanishing; successful handoff steps do not prove valid initial states; locally immutable worker packets do not establish externally authenticated effects or complete nonlocal dependency coverage. `UNKNOWN=>RECOMPUTE` requires a complete authoritative barrier; missing authority means `BLOCKED`. Do not put a proof engine in CyberSand's per-cell hot path.

**Newly accepted original machining cases: 0. New independently qualified CyberSand native tick reductions: 0.** Frozen historical **121/20/30/50**, **26** operations, MC-B/MC-1 `NOT_ESTABLISHED`, `production_authorized=false`. No changes to protected source, MAT-AUTH, default Water FreeMass, World/Rapier ownership, worker fence, physical hash, saved state or material laws. No guarded research merge without distinct independent review and exact-head tests.
