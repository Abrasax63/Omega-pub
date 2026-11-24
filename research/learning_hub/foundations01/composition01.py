"""COMPOSITION01: learned composition of membership logits, matched arms."""
import argparse, hashlib, json, random, time
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F
from structure01 import Net,data,metrics,VOCAB

SEEDS=(11,22,33)
ARMS=("frozen","finetune","scratch")
PREVIOUS={"11":"3bfa1765e3876f70abaea6d5c00fe24f4ed38fea79e6be317a3a81af60742f5b",
          "22":"21fce57ab60a74e2af7061602fa84635f411d66eac8c85b1fe6114564259615e",
          "33":"46f7c5dc8705838c0395e9462912035f7695ed64058ec3e95eba9918082940de"}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def composition_data(seed,families,sizes):
    rng=random.Random(seed); records=[]
    for _ in range(families):
        n=rng.choice(sizes); nodes=rng.sample(range(VOCAB),n); x,y,z=rng.sample(nodes,3)
        queries=((x,y),(y,z),(x,z))
        order=[(a,b) for a in nodes for b in nodes];rng.shuffle(order)
        density=rng.uniform(.2,.8)
        bg={e for e in order if e not in queries and rng.random()<density}
        for motif in range(8):
            bits=[int(c) for c in format(motif,"03b")]
            es=[e for e in order if e in bg or e in [q for q,b in zip(queries,bits) if b]]
            a,b,c=[q in es for q in queries]
            assert [int(a),int(b),int(c)]==bits
            records.append((es,queries,[int(a and b),int(a and b and not c)]))
    E=torch.zeros(len(records),max(sizes)**2,2,dtype=torch.long)
    M=torch.zeros(len(records),max(sizes)**2,dtype=torch.bool)
    Q=torch.empty(len(records),3,2,dtype=torch.long)
    Y=torch.empty(len(records),2)
    for i,(es,qs,ys) in enumerate(records):
        if es: E[i,:len(es)]=torch.tensor(es);M[i,:len(es)]=True
        Q[i]=torch.tensor(qs);Y[i]=torch.tensor(ys)
    return E,M,Q,Y

class Composer(nn.Module):
    def __init__(self,member,frozen):
        super().__init__()
        self.member=member
        self.head=nn.Sequential(nn.Linear(3,32),nn.ReLU(),nn.Linear(32,2))
        if frozen:
            for p in self.member.parameters():p.requires_grad_(False)
    def forward(self,e,m,q):
        b,k=q.shape[:2]
        e=e[:,None].expand(-1,k,-1,-1).reshape(b*k,e.shape[1],2)
        m=m[:,None].expand(-1,k,-1).reshape(b*k,m.shape[1])
        scores=self.member(e,m,q.reshape(b*k,2)).reshape(b,k)
        return self.head(scores.sigmoid())

def prior(seed,out):
    torch.manual_seed(seed);net=Net(True);opt=torch.optim.AdamW(net.parameters(),lr=.003)
    ds=data(seed+10000,2048,[4,5,6]);net.train()
    for epoch in range(2):
        g=torch.Generator().manual_seed(seed+epoch);order=torch.randperm(2048,generator=g)
        for batch in order.split(16):
            ids=torch.stack((2*batch,2*batch+1),1).flatten()
            e,m,q,y=[a[ids] for a in ds];opt.zero_grad(set_to_none=True)
            loss=F.binary_cross_entropy_with_logits(net(e,m,q),y)
            loss.backward();opt.step()
    sets={"n8":data(80081,128,[8]),"n12":data(120081,128,[12]),"sparse":data(81081,64,[8],.05),"dense":data(82081,64,[8],.95)}
    checks={k:metrics(net,v) for k,v in sets.items()}
    if any(v["correct"]!=v["n"] for v in checks.values()):raise ValueError("PRIOR_REPRODUCTION")
    path=out/f"conditioned-{seed}.pt";torch.save(net.state_dict(),path)
    return {k:v.detach().clone() for k,v in net.state_dict().items()},dict(sha256=sha(path),previous_sha256=PREVIOUS[str(seed)],hash_match=sha(path)==PREVIOUS[str(seed)],checks=checks)

def evaluate(net,ds):
    net.eval();parts=[]
    with torch.no_grad():
        for e,m,q in zip(ds[0].split(64),ds[1].split(64),ds[2].split(64)):
            parts.append(net(e,m,q))
    logits=torch.cat(parts);y=ds[3]
    hits=(logits>=0)==y.bool();joint=hits.all(1)
    return dict(n=len(y),joint=int(joint.sum()),path_correct=int(hits[:,0].sum()),
                violation_correct=int(hits[:,1].sum()),complete_families=int(joint.reshape(-1,8).all(1).sum()),
                per_motif=[int(x) for x in joint.reshape(-1,8).sum(0)],
                loss=float(F.binary_cross_entropy_with_logits(logits,y)))

def main(out):
    torch.set_num_threads(2);out=Path(out);out.mkdir(parents=True,exist_ok=False)
    composition={"n8":composition_data(8800321,64,[8]),"n12":composition_data(12000321,64,[12])}
    retention={"n8":data(8800441,128,[8]),"n12":data(12000441,128,[12])}
    records=[]
    for seed in SEEDS:
        state,proof=prior(seed,out)
        train=composition_data(seed+551000,256,[4,5,6])
        schedule=[]
        for epoch in range(8):
            order=torch.randperm(256,generator=torch.Generator().manual_seed(seed+epoch))
            schedule.extend((8*b[:,None]+torch.arange(8)).flatten() for b in order.split(8))
        for arm in ARMS:
            torch.manual_seed(seed);member=Net(True)
            if arm!="scratch":member.load_state_dict(state)
            torch.manual_seed(seed+900);net=Composer(member,arm=="frozen")
            before={k:metrics(member,v) for k,v in retention.items()}
            initial={k:v.detach().clone() for k,v in net.named_parameters()}
            opt=torch.optim.AdamW((p for p in net.parameters() if p.requires_grad),lr=.003)
            losses=[];start=time.monotonic();net.train()
            for idx in schedule:
                e,m,q,y=[a[idx] for a in train];opt.zero_grad(set_to_none=True)
                loss=F.binary_cross_entropy_with_logits(net(e,m,q),y)
                if not bool(torch.isfinite(loss)):raise ValueError("NONFINITE")
                loss.backward();opt.step();losses.append(float(loss.detach()))
            elapsed=time.monotonic()-start
            delta={prefix:sum(float((v.detach()-initial[k]).square().sum()) for k,v in net.named_parameters() if k.startswith(prefix))**.5 for prefix in ("member","head")}
            if arm=="frozen" and delta["member"]!=0:raise ValueError("FROZEN_CHANGED")
            if delta["head"]<=0:raise ValueError("HEAD_NOT_TRAINED")
            after={k:metrics(member,v) for k,v in retention.items()}
            tests={k:evaluate(net,v) for k,v in composition.items()}
            passed=all(v["joint"]>=487 and min(v["per_motif"])>=58 for v in tests.values())
            retained=arm!="scratch" and all(after[k]["correct"]>=before[k]["correct"]-5 for k in before)
            path=out/f"composition-{arm}-{seed}.pt";torch.save(net.state_dict(),path)
            r=dict(seed=seed,arm=arm,steps=len(schedule),examples_per_epoch=len(train[3]),
                   exposures=sum(len(i) for i in schedule),parameters=sum(p.numel() for p in net.parameters()),
                   trainable=sum(p.numel() for p in net.parameters() if p.requires_grad),
                   loss_by_epoch=[sum(losses[i:i+32])/32 for i in range(0,len(losses),32)],
                   delta_l2=delta,seconds=elapsed,weights_sha256=sha(path),prior=proof,
                   retention_before=before,retention_after=after,composition=tests,
                   composition_pass=passed,retention_pass=retained)
            records.append(r);print(json.dumps(r),flush=True)
            (out/"results.json").write_text(json.dumps(records,indent=2))
    verdict={a:dict(composition=all(r["composition_pass"] for r in records if r["arm"]==a),
                    retention=all(r["retention_pass"] for r in records if r["arm"]==a)) for a in ARMS}
    print("COMPOSITION01_RESULT",json.dumps(verdict),flush=True)
    (out/"verdict.json").write_text(json.dumps(verdict,indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);main(p.parse_args().out)
