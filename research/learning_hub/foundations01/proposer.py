"""Admit raw model proposals; never execute generated code."""
import json
from teacher import admit

PROMPT = ('Invent a binary relation on 3 to 4 named nodes and a triple to inspect. '
          'Return only JSON with nodes, edges, triple. Edges are pairs of node names. '
          'Do not include answers.')

def collect(raw_outputs, sensor):
    accepted, rejected, seen = [], [], set()
    for index, raw in enumerate(raw_outputs):
        try:
            if not isinstance(raw,str) or len(raw)>4096:
                raise ValueError("INVALID_SIZE")
            packet=json.loads(raw)
            row=admit(packet,sensor)
            key=(len(packet["nodes"]), tuple(sorted(tuple(e) for e in packet["edges"])),tuple(packet["triple"]))
            if key in seen:
                raise ValueError("DUPLICATE")
            seen.add(key)
            row.update(model_generated=True, provenance="MODEL_PROPOSAL_EXACT_TEACHER_LABEL", proposal_index=index)
            accepted.append(row)
        except (ValueError,TypeError,KeyError) as exc:
            rejected.append({"index":index,"reason":str(exc)})
    return {"accepted":accepted,"rejected":rejected,"attempts":len(accepted)+len(rejected)}
