#!/usr/bin/env node
// Independent Node.js decision path for RCS-019 canonicalizer conformance.
import fs from 'node:fs';
import os from 'node:os';

const I64_MIN = -(1n << 63n);
const I64_MAX = (1n << 63n) - 1n;
const MASK64 = (1n << 64n) - 1n;

function roundEven(n, d) {
  if (d <= 0n) throw new Error('denominator must be positive');
  const neg = n < 0n;
  let a = neg ? -n : n;
  let q = a / d;
  const r = a % d;
  if (2n * r > d || (2n * r === d && q % 2n === 1n)) q += 1n;
  return neg ? -q : q;
}
const accept = (fields = {}) => ({status: 'accepted', ...fields});
const reject = (code) => ({status: 'refused', code});
const ints = (xs) => xs.map(BigInt);

function canonicalQ(q0, policy) {
  let q = [...q0];
  if (q.some(v => v < I64_MIN || v > I64_MAX)) return reject('INTEGER_OVERFLOW');
  if (q.every(v => v === 0n)) return reject('ZERO_QUATERNION');
  const s = BigInt(policy.q15_scale);
  const e = BigInt(policy.q15_norm_tolerance_tokens);
  const n2 = q.reduce((a, v) => a + v*v, 0n);
  if (n2 < (s-e)*(s-e) || n2 > (s+e)*(s+e)) return reject('QUATERNION_NORM_OUT_OF_RANGE');
  const first = q.find(v => v !== 0n);
  if (first < 0n) q = q.map(v => -v);
  return accept({q: q.map(String)});
}

function exactRotation(q, p) {
  const [w,x,y,z] = q;
  const d = w*w+x*x+y*y+z*z;
  if (d === 0n) throw new Error('zero quaternion');
  const m = [
    [w*w+x*x-y*y-z*z, 2n*(x*y-w*z), 2n*(x*z+w*y)],
    [2n*(x*y+w*z), w*w-x*x+y*y-z*z, 2n*(y*z-w*x)],
    [2n*(x*z-w*y), 2n*(y*z+w*x), w*w-x*x-y*y+z*z],
  ];
  return m.map(row => {
    const n = row[0]*p[0] + row[1]*p[1] + row[2]*p[2];
    if (n % d !== 0n) throw new Error('nonintegral transform vector');
    return n / d;
  });
}

function graphResult(frames) {
  const orderIds = frames.map(f => f.id);
  if (new Set(orderIds).size !== orderIds.length) return reject('DUPLICATE_FRAME_ID');
  const ids = new Set(orderIds);
  if (frames.some(f => f.parent !== null && !ids.has(f.parent))) return reject('UNKNOWN_PARENT_FRAME');
  const placed = [];
  const waiting = new Map(frames.map(f => [f.id, f.parent]));
  while (waiting.size) {
    let changed = false;
    for (const id of orderIds) {
      if (!waiting.has(id)) continue;
      const parent = waiting.get(id);
      if (parent === null || placed.includes(parent)) {
        waiting.delete(id); placed.push(id); changed = true;
      }
    }
    if (!changed) return reject('FRAME_CYCLE');
  }
  return accept({topological_order: placed});
}

function sampleSegments(samples) {
  let prior = null;
  let group = [];
  const groups = [];
  const quantized = [];
  for (const s of samples) {
    const key = JSON.stringify([s.engaged, s.tool, s.setup, s.body]);
    quantized.push(String(roundEven(BigInt(s.x_num), BigInt(s.x_den))));
    if (prior === null || prior === key) group.push(s.id);
    else { groups.push(group); group = [s.id]; }
    prior = key;
  }
  if (group.length) groups.push(group);
  return accept({segments: groups, quantized_x_nm: quantized});
}

function interpolate(a, b, i, n) {
  return [
    a[0] + roundEven((b[0]-a[0])*BigInt(i), BigInt(n)),
    a[1] + roundEven((b[1]-a[1])*BigInt(i), BigInt(n)),
  ];
}
function reduceStraight(points) {
  if (points.length < 3) return [...points];
  const keep = [points[0]];
  for (let i=1; i<points.length-1; i++) {
    const a = keep[keep.length-1], b = points[i], c = points[i+1];
    const ux=b[0]-a[0], uy=b[1]-a[1], vx=c[0]-b[0], vy=c[1]-b[1];
    const cross=ux*vy-uy*vx, dot=ux*vx+uy*vy;
    if (cross===0n && dot>=0n) continue;
    keep.push(b);
  }
  keep.push(points[points.length-1]);
  return keep;
}

function evaluate(v, policy) {
  const d=v.input;
  switch (v.operation) {
    case 'round_rational': return accept({integer:String(roundEven(BigInt(d.numerator),BigInt(d.denominator)))});
    case 'convert_length': {
      const scale = d.unit==='mm' ? 1000000n : d.unit==='inch' ? 25400000n : null;
      if (scale===null) return reject('UNKNOWN_UNIT');
      const x=roundEven(BigInt(d.numerator)*scale,BigInt(d.denominator));
      if (x<I64_MIN || x>I64_MAX) return reject('INTEGER_OVERFLOW');
      return accept({length_nm:String(x)});
    }
    case 'validate_i64': {
      const x=BigInt(d.value);
      return x<I64_MIN||x>I64_MAX ? reject('INTEGER_OVERFLOW') : accept({value:String(x)});
    }
    case 'canonicalize_q15': return canonicalQ(ints(d.q),policy);
    case 'apply_transform_chain': {
      let p=ints(d.point_nm);
      for (const t of d.transforms) {
        const q=ints(t.q), qc=canonicalQ([...q],policy);
        if (qc.status!=='accepted') return qc;
        p=exactRotation(q,p).map((x,i)=>x+BigInt(t.t_nm[i]));
        if (p.some(x=>x<I64_MIN||x>I64_MAX)) return reject('INTEGER_OVERFLOW');
      }
      return accept({point_nm:p.map(String)});
    }
    case 'validate_frame_graph': return graphResult(d.frames);
    case 'stable_timestamp_order': {
      const records=d.samples.map((s,i)=>({t:BigInt(s.time_ns),i,id:s.id}));
      records.sort((a,b)=>a.t<b.t?-1:a.t>b.t?1:a.i-b.i);
      return accept({ids:records.map(x=>x.id)});
    }
    case 'segment_samples': return sampleSegments(d.samples);
    case 'classify_arc': {
      const sw=BigInt(d.sweep_nrad)<0n?-BigInt(d.sweep_nrad):BigInt(d.sweep_nrad);
      const full=BigInt(policy.full_circle_nrad), low=BigInt(policy.min_arc_sweep_nrad), guard=BigInt(policy.full_circle_guard_nrad);
      const distance=full>sw?full-sw:sw-full;
      if (sw<low || distance<guard) return accept({representation:'polyline',reason:'ARC_SWEEP_AMBIGUOUS'});
      if (BigInt(d.certified_error_nm)>BigInt(d.allowed_error_nm)) return accept({representation:'polyline',reason:'FIT_BOUND_UNCERTIFIED'});
      return accept({representation:'arc'});
    }
    case 'choose_fit': return BigInt(d.certified_error_nm)<=BigInt(d.allowed_error_nm)
      ? accept({representation:d.candidate}) : accept({representation:'polyline',reason:'FIT_BOUND_UNCERTIFIED'});
    case 'equivalent_linear_sampling': {
      const a=ints(d.start_nm), b=ints(d.end_nm), outputs=[];
      for (const count of d.sample_counts) {
        const points=[];
        for (let i=0;i<count;i++) points.push(interpolate(a,b,i,count-1));
        outputs.push(reduceStraight(points));
      }
      const signature=JSON.stringify(outputs[0],(_,x)=>typeof x==='bigint'?String(x):x);
      const same=outputs.slice(1).every(o=>JSON.stringify(o,(_,x)=>typeof x==='bigint'?String(x):x)===signature);
      return accept({all_identical:same,representation:outputs[0].length===2?'line':'polyline',max_error_nm:'0'});
    }
    case 'equivalent_v_sampling': {
      const a=ints(d.start_nm), m=ints(d.mid_nm), b=ints(d.end_nm), outputs=[];
      for (const count of d.sample_counts) {
        const n=count-1;
        if (n%2) throw new Error('V path requires midpoint sample');
        const h=n/2, points=[];
        for(let i=0;i<=h;i++) points.push(interpolate(a,m,i,h));
        for(let i=1;i<=h;i++) points.push(interpolate(m,b,i,h));
        outputs.push(reduceStraight(points));
      }
      const encode=o=>o.map(p=>p.map(String));
      const sig=JSON.stringify(encode(outputs[0]));
      const same=outputs.slice(1).every(o=>JSON.stringify(encode(o))===sig);
      return accept({all_identical:same,representation:'polyline',points_nm:encode(outputs[0]),max_error_nm:'0'});
    }
    case 'noisy_line_trace': {
      let state=BigInt(d.seed)&MASK64;
      const radius=BigInt(d.noise_radius_nm), allowed=BigInt(d.allowed_error_nm), count=Number(d.sample_count);
      let worst=0n;
      for(let i=0;i<count;i++) {
        let y=0n;
        if(i!==0&&i!==count-1) {
          state=(6364136223846793005n*state+1442695040888963407n)&MASK64;
          y=state%(2n*radius+1n)-radius;
        }
        const a=y<0n?-y:y; if(a>worst) worst=a;
      }
      if(worst>allowed) return reject('FIT_BOUND_UNCERTIFIED');
      return accept({representation:'line',max_error_nm:String(worst),sample_count:count});
    }
    default: return reject('UNKNOWN_OPERATION');
  }
}

const args=process.argv.slice(2);
if (!args.length) { console.error('usage: independent_verify.mjs vectors.json [--output path]'); process.exit(2); }
const vectorPath=args[0];
let output=null;
const oi=args.indexOf('--output'); if(oi>=0) output=args[oi+1];
const suite=JSON.parse(fs.readFileSync(vectorPath,'utf8'));
const results=[], failures=[];
for(const v of suite.vectors) {
  const actual=evaluate(v,suite.policy);
  const ok=JSON.stringify(actual)===JSON.stringify(v.expected);
  results.push({id:v.id,family:v.family,actual,matches_expected:ok});
  if(!ok) failures.push({id:v.id,expected:v.expected,actual});
}
const payload={
  schema:'rcs-019-run-result/1.0',
  implementation:'node-independent-verifier/1.0',
  runtime:{node:process.versions.node,platform:`${os.platform()}-${os.release()}-${os.arch()}`},
  vector_schema:suite.schema,
  result_count:results.length,
  failure_count:failures.length,
  results,failures,
};
const text=JSON.stringify(payload,null,2)+'\n';
if(output) fs.writeFileSync(output,text); else process.stdout.write(text);
process.exit(failures.length?1:0);
