"""Deterministic benchmark of duplicated API requests; mock only."""
from router import CallResidency

REQUESTS = ["A", "B", "A", "C", "A", "B", "D", "C", "E", "E", "F", "G"]

def run(optimized):
    router=CallResidency()
    outputs=[]
    for text in REQUESTS:
        payload={"model":"fixed-revision", "messages":[{"role":"user","content":text}], "temperature":0, "max_tokens":32}
        outputs.append(router.invoke(tenant="test",credential_scope="scope",endpoint="local-chat",
                                     model_revision="fixed-v1", payload=payload,
                                     backend=lambda p:{"content":p["messages"][0]["content"],"finish_reason":"stop"},
                                     replay_approved=optimized))
    return outputs,router.metrics()

if __name__ == "__main__":
    baseline,b=run(False)
    candidate,c=run(True)
    assert baseline==candidate
    print("FIXTURE synthetic deterministic, not model inference")
    print("baseline",b)
    print("optimized",c)
    print("identical outputs",baseline==candidate)
    print("calls avoided",b["backend_calls"]-c["backend_calls"])
