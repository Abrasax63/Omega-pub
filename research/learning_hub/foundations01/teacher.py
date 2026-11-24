"""Bounded teacher adapter. No model training or holdout access."""
import json
import hashlib

def admit(packet, sensor):
    if type(packet) is not dict or set(packet) != {"nodes","edges","triple"}:
        raise ValueError("INVALID_PROPOSAL")
    result = sensor.inspect_atom(packet)
    bits = result["bits"]
    if set(bits) != {"xy","yz","xz"} or any(type(v) is not bool for v in bits.values()):
        raise ValueError("INVALID_SENSOR")
    truth = bits["xy"] and bits["yz"] and not bits["xz"]
    if truth != result["violates_transitivity_for_this_triple"]:
        raise ValueError("ORACLE_DISAGREEMENT")
    edges = {tuple(e) for e in packet["edges"]}
    x,y,z = packet["triple"]
    independent = dict(xy=(x,y) in edges,yz=(y,z) in edges,xz=(x,z) in edges)
    if independent != bits:
        raise ValueError("MEMBERSHIP_DISAGREEMENT")
    canonical = json.dumps(packet,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    if hashlib.sha256(canonical.encode()).hexdigest() != result["input_sha256"]:
        raise ValueError("DIGEST_DISAGREEMENT")
    return {"prompt":"Read the relation and return JSON with xy,yz,xz and violates. "+canonical,
            "target":json.dumps(dict(bits,violates=truth),sort_keys=True),
            "input_sha256":result["input_sha256"],
            "provenance":"EXACT_SENSOR_SUPERVISION",
            "model_generated":False}
