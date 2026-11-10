"""Direct source-matched current A1 producer event versus B1 adapter, research only.

Usage: python3 probe_current_a1_receipt_20261110.py --a1-dir /path/to/A1/isolator
No native/STEP execution or authenticated spline ancestry is implied.
"""
import argparse, hashlib, importlib.util, json, sys
from copy import deepcopy
from fractions import Fraction
from pathlib import Path

A1_HEAD = "098517a70e63cb8d5b8bab01b34118fa8439c942"
A1_BLOBS = {"algebraic_zero.py":"3c48045a218018c8c3134a1224011c7acc2307b1",
            "receipt_integrity.py":"77f0ba7700002b7a376dfcc2c29b820ea4def485"}
B1_BLOBS = {"phase_bridge.py":"dbcb2049d7e3de09f6430e632bee21ce836a1809",
            "producer_codec.py":"563c445c314309a6198395addbecb59b464182a0"}

def blob(path):
    data=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod

def run(a1dir):
    here=Path(__file__).resolve().parent
    blobs={}
    for directory,identities,label in ((a1dir,A1_BLOBS,"A1"),(here,B1_BLOBS,"B1")):
        for name,expected in identities.items():
            found=blob(directory/name)
            if found!=expected:
                raise RuntimeError(f"{label}/{name} source changed: {found} != {expected}")
            blobs[f"{label}/{name}"]=found
    previous=sys.modules.get("receipt_integrity")
    try:
        load("receipt_integrity",a1dir/"receipt_integrity.py")
        producer=load("_b1_exact_current_a1",a1dir/"algebraic_zero.py")
    finally:
        if previous is None: sys.modules.pop("receipt_integrity",None)
        else: sys.modules["receipt_integrity"]=previous
    source=producer.source([-1],cos=[[]],sin=[[1]],phase_rate=1)
    raw={"c0":list(map(str,source.c0)),
         "cos":[list(map(str,p)) for p in source.cos],
         "sin":[list(map(str,p)) for p in source.sin],
         "phase_offset":str(source.phase_offset),"phase_rate":str(source.phase_rate)}
    pin=producer.source_sha(source)
    actual=producer.rational_event(source,Fraction(1,2))
    assert actual["result"]=="EXACT_ZERO" and actual["source_sha256"]==pin
    assert producer.verify_rational_event(source,actual)
    assert producer.rational_event(source,0)["result"]=="EXACT_NONZERO"
    assert not producer.verify_rational_event(source,{**actual,"result":"EXACT_NONZERO"})
    altered=producer.source([-1],cos=[[]],sin=[[2]],phase_rate=1)
    assert not producer.verify_rational_event(altered,actual)

    from phase_bridge import PRODUCERS,Refusal,canonical,digest,prove_equivalent,verify
    from producer_codec import a1_envelope
    window=["0","1"] # research supplied; A1 does not authenticate the window
    env=a1_envelope(raw,window,source_pin=pin,window_pin=digest(window))
    assert env["origin_source_sha"]==pin
    assert env["producer_head"]==PRODUCERS["A1-470"][0]!=A1_HEAD
    assert canonical(env)["pi_phase"]==["0","1"]
    claim=prove_equivalent(env,deepcopy(env))
    assert verify(env,env,claim,pinned_source_hash=digest(env),pinned_target_hash=digest(env))
    unregistered=deepcopy(env);unregistered["producer_head"]=A1_HEAD
    try: canonical(unregistered)
    except Refusal as e: assert str(e)=="unreviewed producer revision"
    else: raise AssertionError("current unreviewed A1 head was admitted")
    modified=deepcopy(raw);modified["sin"][0][0]="2"
    try: a1_envelope(modified,window,source_pin=pin,window_pin=digest(window))
    except Refusal as e: assert str(e)=="source serialization/pin mismatch"
    else: raise AssertionError("mutated producer source accepted under old pin")
    return {"class":"DIRECT_CURRENT_A1_PYTHON_MODEL","a1_head":A1_HEAD,
            "source_git_blobs":blobs,"a1_real_receipt_verified":True,
            "a1_result":"EXACT_ZERO","source_sha256":pin,
            "altered_a1_receipt_refused":True,"b1_codec_matches_a1_serialization":True,
            "b1_adapter_stamps_historical_head":env["producer_head"],
            "b1_current_head_refused":True,"b1_source_swap_refused":True,
            "producer_head_authentication":False,"physical_window":"RESEARCH_INPUT",
            "a1_event_imported_as_b1_authority":False,"bspline_ancestry":False,
            "native_or_step":False}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--a1-dir",type=Path,required=True)
    print(json.dumps(run(p.parse_args().a1_dir.resolve()),sort_keys=True,indent=2))
