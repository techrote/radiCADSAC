# B1-E7 — False identity-zero via hostile base-sign receipt

**10 November 2026 — DETERMINISTIC_MODEL, Draft/HOLD.** Scope is limited to
`research/experimental/certificate-algebra/core/**` on existing Draft
[#473](https://github.com/techrote/radiCADSAC/pull/473). Base accepted main:
`48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. Preregistered
[source lease](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6760741992).
All existing historical evidence and 26 supported operations are immutable.
MC-B/MC-1 remain NOT_ESTABLISHED and production_authorized=false.

## Precise independently reproducible falsifier

Pre-E7 `certificate_algebra.receipt` accepted a Python `str` subclass as a
certificate's `sign`, because it used `isinstance` and tuple membership;
`check_leaf` used ordinary Python `!=` on that untrusted value. Python's
rich-comparison dispatch invokes the subclass comparator even when the
authentic builtin sign is the left operand. This flaw is **upstream of** the
E6 `receipt_integrity.admit` guard: the latter protected E2–E5 *proposed
output* receipts, not their untrusted base certificate premises.

For the genuine rational source `p(u)=1` on `[0,1]`, Bernstein vector
`(1)` and true sign `POS`, build a genuine `base_record` with its
unmodified source snapshot hash. Replace *only* the receipt sign with
`AlwaysEqual("ZERO")`, a `str` subclass whose `__eq__` always returns
`True` and `__ne__` always returns `False`. The old `receipt` admits
it; the old `check_leaf` accepts `kind((1,)) != bad_sign` as false.
Consequently a purported `Verified` state may contain a false `ZERO`
certificate, and `events` can report an identity-zero interval for a
function that is everywhere 1. The *legitimate source hash is unchanged*:
this is not a digest collision or an attack on the identity of the source.

This is an **in-process Python object admission defect** in the research
model, not a counterexample to the Bernstein theorem, not a demonstration
against a trusted JSON decoder, and not evidence of a native/STEP problem.

## Corrective contract / theorem

E6's existing bounded primitive-tree scan is now exposed as
`receipt_integrity.validate` and applied **before** source and base
receipt parsing, base-array iteration and journal comparison.
`check_leaf` also rejects a directly constructed noncanonical in-process
`Certificate`. All admitted raw trees have exact builtin `dict`
(string keys), `list`, `str`, `int`, `bool`, or null nodes, and
remain subject to existing size/depth caps. Hostile subclass
`__eq__` cannot influence sign/hash comparisons inside verified
base replay. Reused E2–E5 guards retain their behavior.

**Conditional soundness law (infinite parameter family):**
For any finite admitted rational-polynomial piece whose source is
reconstructed exactly from an authenticated and externally pinned base
record, `verify_base` accepting a certificate implies its `sign`
equals `kind(bernstein(source_piece))`, because (1) both values must be
exact builtin strings, (2) Bernstein conversion is exact Fraction
arithmetic, and (3) the checker compares the actual vector and its sign
against the parsed certificate. By strict Bernstein-basis positivity on
the open unit interval, a POS/NEG certificate excludes interior roots;
ZERO attests polynomial identity-zero. The claim applies to infinitely
many rational sources, e.g. `1+c*u*(1-u)` for every rational `c>=0`,
but the **implementation** refuses inputs exceeding its explicit
degree, bit, node and recursion limits. This is a conventional input
validation + established Bernstein theorem, **not a newly discovered
general root-isolation theorem**.

Crucial remaining assumptions: external source pins are genuinely
independent; `Verified` constructed directly by a caller is not an
authenticated serialized token; genuine #462 B-spline structural knots
and arbitrary Boolean/topology operations are not inferred from
B1 partition seams; no simulation-work invalidation or native physics
law has been proved.

## Source-matched changes and bounded evidence

Modified existing owned `receipt_integrity.py` and
`certificate_algebra.py` and added only
`test_base_receipt_integrity.py` and this report. The new test file
has nine exact-module test methods, including true source pin,
hostile ZERO, forged source hash, a direct dataclass forgery, nonprimitive
source coefficient/key, journal mutation, real zero continuum, split
replay, cyclic input and 112 representatives of the infinite positive
Bernstein family. Expected safe outcome: every forged premise REFUSED;
ordinary complete zero sets unchanged.

**Executed independent CPython reduced-logic check:** 112/112 positive
Bernstein members accepted and 112/112 hostile sign substitutions
refused; cyclic receipt structure refused. Earlier independent
CPython check against the historical comparison predicates demonstrated
an actual `AlwaysEqual("ZERO")` bypass and resulting false identity-zero
classification. These reduced tests were **not execution of the full
published B1 module**; the authored nine test methods and complete
suite still require literal-head execution. No native, paid API or STEP
runs were made.

Reproduce from `research/experimental/certificate-algebra/core/`:

```sh
python3 -m unittest -v test_base_receipt_integrity.py test_receipt_integrity.py
python3 -m unittest discover -v -p 'test_*.py'
```

The additional validation costs O(number of primitive JSON tree nodes),
with stack space O(depth) and existing 131072-node, 32-depth budget.
Repeated base-source scans can increase research verifier time. No
measured throughput, memory, STEP or CyberSand speed benefit is claimed;
this code must never be inserted into a hot simulation path.

## Independent review, prior art and open seams

Request A3 to replay the *exact corrected B1 module* and independently
challenge remaining direct constructor and archive/journal input
boundaries. Request B5 to verify the consumer separates producer
custody from valid but attacker-supplied source hashes. Retain the
A3 [reported analogous A2 forgery](https://github.com/techrote/radiCADSAC/pull/471)
as parallel negative evidence, not a claim of module equivalence.

Established mathematics: Bernstein/de Casteljau positivity, as in
Bertot, Guilhot and Mahboubi (2011),
https://doi.org/10.1017/S0960129511000090.
Related source-time/knot covariance:
[#462](https://github.com/techrote/radiCADSAC/pull/462).
Existing bounded event isolation:
[#453](https://github.com/techrote/radiCADSAC/pull/453).
No accepted programme or proof authority is modified.

**Disposition: research GO for narrow premise hardening; integration
HOLD until full exact-head module tests and A3/B5 independent review.
No merge.** Historical 121 originals / 20 route refusals /
30 missing ordered premises / 50 complete witnesses, with zero
new original closures, remain unchanged.
