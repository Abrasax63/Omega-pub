import argparse, json, random, time, hashlib
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F
VOCAB=12

def data(seed,pairs,sizes,density=None):
    rng=random.Random(seed); records=[]; maxedges=max(sizes)**2
    for _ in range(pairs):
        n=rng.choice(sizes); nodes=rng.sample(range(VOCAB),n); x,y=rng.sample(nodes,2)
        order=[(a,b) for a in nodes for b in nodes]; rng.shuffle(order)
        d=rng.uniform(.2,.8) if density is None else density
        bg={e for e in order if e!=(x,y) and rng.random()<d}
        for present in (0,1):
            es=[e for e in order if e in bg or (present and e==(x,y))]
            assert ((x,y) in es)==bool(present)
            records.append((es,(x,y),present))
    edges=torch.zeros(len(records),maxedges,2,dtype=torch.long)
    mask=torch.zeros(len(records),maxedges,dtype=torch.bool)
    queries=torch.empty(len(records),2,dtype=torch.long);labels=torch.empty(len(records))
    for i,(es,q,y) in enumerate(records):
        if es: edges[i,:len(es)]=torch.tensor(es); mask[i,:len(es)]=True
        queries[i]=torch.tensor(q);labels[i]=y
    return edges,mask,queries,labels

class Net(nn.Module):
    def __init__(self,conditioned):
        super().__init__();self.conditioned=conditioned
        self.edge=nn.Sequential(nn.Linear(48,64),nn.ReLU(),nn.Linear(64,64),nn.ReLU())
        self.head=nn.Sequential(nn.Linear(88,64),nn.ReLU(),nn.Linear(64,1))
    def forward(self,edges,mask,query):
        e=F.one_hot(edges,VOCAB).flatten(-2).float()
        q=F.one_hot(query,VOCAB).flatten(-2).float()
        local=q[:,None,:].expand(-1,e.shape[1],-1) if self.conditioned else torch.zeros_like(e)
        h=self.edge(torch.cat((e,local),dim=-1))
        h=h.masked_fill(~mask.unsqueeze(-1),-torch.inf).amax(1)
        h=torch.where(mask.any(1,keepdim=True),h,torch.zeros_like(h))
        return self.head(torch.cat((h,q),dim=-1)).squeeze(-1)

def metrics(net,ds):
    net.eval();ls=[]
    with torch.no_grad():
        for e,m,q in zip(ds[0].split(64),ds[1].split(64),ds[2].split(64)):
            ls.append(net(e,m,q))
    logits=torch.cat(ls); y=ds[3];hits=(logits>=0)==y.bool()
    return dict(n=len(y),correct=int(hits.sum()),pairs=int(hits.reshape(-1,2).all(1).sum()),negative=int(hits[::2].sum()),positive=int(hits[1::2].sum()),loss=float(F.binary_cross_entropy_with_logits(logits,y)))

def main(out):
    torch.set_num_threads(2);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    test={'n8':data(80081,128,[8]),'n12':data(120081,128,[12]),'sparse':data(81081,64,[8],.05),'dense':data(82081,64,[8],.95)}
    report=[]
    for seed in (11,22,33):
        train=data(seed+10000,2048,[4,5,6]);schedule=[]
        for epoch in range(2):
            g=torch.Generator().manual_seed(seed+epoch);order=torch.randperm(2048,generator=g)
            schedule.extend(torch.stack((2*b,2*b+1),1).flatten() for b in order.split(16))
        for arm in ('control','conditioned'):
            torch.manual_seed(seed);net=Net(arm=='conditioned');opt=torch.optim.AdamW(net.parameters(),lr=.003)
            initial={k:v.detach().clone() for k,v in net.named_parameters()};losses=[];start=time.monotonic();net.train()
            for idx in schedule:
                e,m,q,y=[a[idx] for a in train];opt.zero_grad(set_to_none=True)
                loss=F.binary_cross_entropy_with_logits(net(e,m,q),y);loss.backward();opt.step();losses.append(float(loss.detach()))
            seconds=time.monotonic()-start
            delta=sum(float((v.detach()-initial[k]).square().sum()) for k,v in net.named_parameters())**.5
            path=out/f'{arm}-{seed}.pt';torch.save(net.state_dict(),path)
            r=dict(seed=seed,arm=arm,steps=len(schedule),parameters=sum(p.numel() for p in net.parameters()),delta_l2=delta,seconds=seconds,mean_loss_epoch1=sum(losses[:128])/128,mean_loss_epoch2=sum(losses[128:])/128,weight_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),test={k:metrics(net,v) for k,v in test.items()})
            report.append(r);print(json.dumps(r),flush=True);(out/'results.json').write_text(json.dumps(report,indent=2))
    passed=all(r['test'][k]['correct']>=231 and r['test'][k]['pairs']>=103 for r in report if r['arm']=='conditioned' for k in ('n8','n12'))
    print('PREREGISTERED_PASS',passed,flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);main(p.parse_args().out)
