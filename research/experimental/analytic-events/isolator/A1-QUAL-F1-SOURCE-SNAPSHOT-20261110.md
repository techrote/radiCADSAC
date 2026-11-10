# A1-QUAL-008 — F1 rational/quadratic source snapshot coherence (10 Nov 2026)

Repository: https://github.com/techrote/radiCADSAC
Candidate PR: https://github.com/techrote/radiCADSAC/pull/470 — Draft/HOLD, do not merge
Published parent: `b46eeba40c09f61ef8ac6253d397964651fdea53`
Accepted main: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`
Scoped lease: https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6778044455

## Preregistered falsifier / published-parent execution

A1 F1's `rational_event` and `quadratic_event` evaluate a caller-owned frozen `Source` and then call `source_sha(s)`. A caller can use Python's `object.__setattr__` to change a frozen dataclass's field in the gap. With deterministic `sys.settrace` on the *actual* `source_sha()` call:

- Rational: H0=-1, C1=1, time t=0, phase a=0,b=1. Honest F=0. Replacing H0 with +1 makes F=2 (not zero). The original receipt remains EXACT_ZERO but hashes this nonzero source.
- Quadratic: H0=t²−2 and minimal polynomial t²−2. Honest order-1 roots ±sqrt(2). Replacing H0 with constant +1 eliminates both roots. The original receipt retains the old order-1 zero classification but hashes the nonzero source.
- Actual original `verify_rational_event` and `verify_quadratic_event` both returned True when the mutation was repeated at their internal digest call. Static verification of either unmutated source refused the mismatched digest.

The real original-parent falsifier **exited 1** with
```
RATIONAL REAL_VERIFY_UNDER_MUTATION True
QUADRATIC REAL_VERIFY_UNDER_MUTATION True
AssertionError: A1-F1 REAL VERIFIER ACCEPTED SOURCE-INCOHERENT RECEIPTS: (True, True)
```
All 22 original published Python parent/test/checker blobs were matched against the literal original head and the authored original suite executed **106/106 PASS**. Thus existing tests did not exercise this cross-stage source-rebinding failure. This finding does *not* refute the cyclotomic or Gelfond–Schneider zero theorem; it is an in-process certificate source-custody defect.

## Minimal repair and adversarial tests

`algebraic_zero._owned_source` constructs one validated, private, immutable exact-value `Source` at each public rational/quadratic event-entry. Evaluation, Fourier channel/valuation classification, cyclotomic reduction, and the SHA-256 receipt subsequently use that same captured object. `test_algebraic_zero.SourceSnapshotCoherenceTests` includes two actual imported-parent adversaries mutating the caller's `Source.c0` at the real `source_sha` function-entry, checking the old false receipt is refused and producer output remains coherently source-bound. Existing source grammar, zero/tangency/identity distinction, phase convention, limits and verdicts are unchanged.

This guarantees internal owned-Python-source consistency for the admitted exact immutable values, **not** a trusted external writer fence or authenticated physical B-spline source history. Adversarial mutation of an independent caller-owned container during initial snapshot capture may yield a coherent copied sample, not an authenticated atomic original.

## Reproduction and post-publish qualification contract

From the exact new commit (see PR #470 for literal SHA):
```sh
git checkout --detach <new-A1-head>
cd research/experimental/analytic-events/isolator
python3 -m unittest discover -s . -p 'test_*.py' -v
python3 -m unittest -v test_algebraic_zero.SourceSnapshotCoherenceTests
python3 challenge_sympy.py
```
Compare `git hash-object algebraic_zero.py test_algebraic_zero.py` with the published Git blob identities, and compare every other imported parent/test/checker Python file against the exact commit tree. The published-parent negative test must be run on its separately pinned old file; a patched-source run of an intentionally old-failure assertion is **not** a new failure.

Local corrected-source candidate before publish: **108/108** complete standard-library test methods PASS (zero skips); SymPy passed 32 cyclotomics / 209 rational comparisons / 31 typed budget refusals / 120 quadratic valuations. F1 7/7 adversarial hostile receipt substitutions refused; F6 compound negative rate/projective pole/order/multiplicity/sided-sign test PASS with all 4 false receipts refused; F4/F6/F7 source-interleaving replays PASS. Direct fresh head readback and independent A3 review remain separately required before any qualification claim or gate update.

## Verification matrix

| Claim | Disposition |
|---|---|
| Local bounded H0/H1/H2 exact algebraic point and companion theorem | Conditional/reused mathematical statements; not globally re-proved |
| Complete candidate suite and original imported modules | Locally 108/108 PASS **before publish**; mandatory literal new-head rerun |
| F1 rational/quadratic source/digest mutation | Original published verifier **FALSE ACCEPTANCE**; corrected actual-parent imported regressions PASS locally |
| F6 negative-phase/projective-pole/order/multiplicity and forged receipt controls | Local actual-parent PASS |
| Independent A3 exact-new-head second-source execution | PENDING, request explicit falsification |
| Authenticated original physical B-spline/time/phase ancestry | UNVERIFIED |
| Unrestricted H2/root multiplicity/tangency and arbitrary knots | NOT_ESTABLISHED |
| MC-B / MC-1, production | NOT_ESTABLISHED; `production_authorized=false` |

Historical census **121/20/30/50** and all **26 machining operations** remain immutable. This change is A1 research-only; no MC-038 sources, proof registry, A2/A3/B1, native/paid, production or shared authority changed. No merge or Ready transition.