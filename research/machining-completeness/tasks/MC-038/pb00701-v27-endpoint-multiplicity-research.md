# MC-038 / PB-007-01 — frozen V27 endpoint-multiplicity shadow composition

**Status:** bounded deterministic-model research candidate  
**Date:** 30 October 2026  
**Parent:** #100  
**Preselection:** https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6511501626  
**Exact base:** `2e41a4d152c7018c743e1e269383ffc8bbbee6ef`

## Live frozen blocker

The pinned v54 case
`composite:DELEGATED_V6_CONSTANT_MODULATION:tail0` is an actual frozen
original-source record:

- source parameter `source-time-t in [0,2]`;
- exact phase turns `t/4`;
- constant H1 cosine amplitude 1 over two exact B-spline spans.

Historical observation is deliberately unchanged:

1. first span: `DELEGATED_V6_CONSTANT_MODULATION / CERTIFIED`;
2. second span:
   `PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION / BLOCKED /
   V27_CHILD_LEFT_ENDPOINT_MULTIPLICITY_NOT_COMPOSABLE`.

The physical function is `F(t)=cos(pi*t/2)`. At the shared source knot
`t=1`, `F=0` and `F'=-pi/2`, so the root is simple. Landed V27 still
correctly refuses because its certified child route does not publish endpoint
multiplicity, and it will not invent multiplicity from a root count.

## Bounded theorem

For a currently certified V27 child whose exact endpoint relation is ZERO but
whose route omits endpoint multiplicity:

1. reconstruct the exact analytic child from V27's own rational polynomial
   cosine/sine amplitudes and exact affine phase;
2. bind that reconstruction to the child source, never caller-supplied root or
   multiplicity data;
3. use the pinned #298 cyclotomic/π-transcendence point-jet primitive at the
   exact rational endpoint;
4. require an exact point event and take its first nonzero derivative order as
   the analytic endpoint-root multiplicity;
5. if the child route already publishes multiplicity (or says all roots are
   simple), independently require the point-jet order to agree;
6. leave every existing open-root multiplicity requirement unchanged; and
7. compose children only with landed V27's exact internal-cut relation and
   matching-multiplicity rules.

Resource exhaustion or unresolved exact derivative sign is nontruth/refusal.

## Source-bound positive control

The verifier loads the exact frozen case from the pinned v54 corpus and first
requires current V27 to reproduce
`V27_CHILD_LEFT_ENDPOINT_MULTIPLICITY_NOT_COMPOSABLE`.

The shadow compositor then replays the affected V27 partition. Its missing left
endpoint multiplicity must be supplied by an exact point witness with:

- exact point status `EXACT_RATIONAL_POINT_EVENT`;
- phase turn `1/4`;
- first nonzero derivative order 1;
- negative first-derivative sign;
- right-side physical sign negative.

All shadow span routes must then be composable. This is a research view only;
the historical corpus stays BLOCKED.

A separate exact control uses
`F(u)=u^2 cos(2*pi*u/8)` to require order 2, proving the mechanism is not
hard-coded to simple roots.

## Discovered deeper blocker and bounded correction

The initial endpoint-only implementation was falsified as a complete frozen-case
closure. Literal-head runs 40977688272 and 40977783727 retained that negative
result: after the exact left-endpoint order-1 witness, V27 reaches its third
child `[2/3,1]`, where the predecessor V6 route blocks with
`TAN_HALF_POLE_REQUIRES_EXACT_WINDOW_PARTITION`.

That child has exact phase window `[5/12,1/2]`. The tan-half coordinate is
singular at the right endpoint, but the physical trigonometric source is not.
For this **constant-modulation, shorter-than-half-turn, endpoint-pole-only**
case, the research shadow uses the exact source-coordinate identity

`t'=t-p`, where `p=n+1/2` is the pole endpoint,

and transforms every harmonic coefficient by `(-1)^h`:

`cos(2πh(t'+p))=(-1)^h cos(2πh t')` and
`sin(2πh(t'+p))=(-1)^h sin(2πh t')`.

The frozen window therefore becomes `[-1/12,0]`; H1 cosine coefficient 1
becomes -1. The **unchanged pinned V6 rational-turn classifier** certifies that
normalized window, and the original child endpoints are still independently
rechecked by #298. Interior poles, width >= 1/2, multiple pole endpoints and
nonconstant modulation remain refused. No general pole partition theorem is
claimed.

## Falsifiers

The executable rejects/refuses:

- a nonzero endpoint being assigned multiplicity;
- a zero endpoint lacking an exact point event;
- route-published multiplicity disagreeing with the point jet;
- internal-cut left/right multiplicity mismatch;
- unavailable open-root multiplicity;
- source/phase/source-parameter/amplitude mutation;
- caller-supplied endpoint multiplicity/root authority;
- binary/noncanonical rational input;
- source-binding or endpoint-coordinate mismatch;
- jet resource exhaustion/unresolved sign;
- forged report or capability elevation; and
- drift in V27, its child classifier, #298, frozen corpus, domain or authority.

## Custody

Pinned blobs:

- V6 rational-turn exact classifier:
  `a1316ff0f71b2d7aa80807843a74fd8280779cb2`;
- V27 phase-sector compositor:
  `6211e658621af7100c2509dcafdaeaf348e48d46`;
- complete child classifier:
  `a303bba600fa83a1b55c8e113ce1ec7d06f68590`;
- #298 exact rational-phase point/jet:
  `9fc344e045fa800fb24d30902a641e534a1e197b`;
- #298 exact rational interval/trigonometric enclosure engine:
  `2320f92efe4316d865a89f6d848737e2c000ca4d`;
- V6 exact event-model bridge:
  `104c0e7a459cd7da5025853b246faff244a5948e`;
- MC-032 exact Sturm/event engine:
  `789a709c5141479a343035d1b7055dd4e53534e1`;
- frozen v54 corpus:
  `5841c331579489b25caef38cd412bdbf286f9134`;
- 26-operation domain:
  `23de82f5240a72509f7afe4acd5948b65bc4ff13`;
- no-production authority:
  `fa0233323a0804d8a5d3eb7cd892a274a6173fab`.

## Nonclaims

This is a **shadow composition theorem**, not a modification of V6/V27
production code. It does not rewrite or admit historical v54 dispositions,
certify arbitrary V27/V41 children, solve algebraic V41 child boundaries,
establish a general interior-pole/window-partition theorem, establish a global
smooth multiplicity across separate B-spline spans, or establish any global
multi-span root count/deduplication. The shared physical source-knot zero
therefore remains represented by two span-local endpoint records in this
research view; cross-span deduplication is explicitly unclaimed.

PB-007-01 remains uncertified; MC-B and MC-1 remain `NOT_ESTABLISHED`;
native material/topology/lineage, B-rep, usable conventional STEP and
production authorization remain unqualified.

## Reproduction and landing gate

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v27_endpoint_multiplicity.py --contract --self-test
```

Landing requires literal final-head focused success, `mc1-static`, distinct
technical/source review of that exact head, expected-head-protected merge,
reviewed/synthetic/landed tree identity, and actual merged-main focused/static
success.
