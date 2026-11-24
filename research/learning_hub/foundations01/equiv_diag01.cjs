// EQUIV-DIAG01: isolated inference diagnostics, no training or model calls.
function insist(ok, msg) { if(!ok) throw Error(msg); }

function rng(seed) { insist(Number.isInteger(seed)&&seed>0&&seed<=4294967295,"seed"); let x=seed>>>0;return ()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return (x>>>0)/4294967296;}; }

function shuffle(xs,r) { const a=xs.slice();for(let i=a.length-1;i>0;i--){let j=Math.floor(r()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a; }

function combinations(xs) { return xs.flatMap((a,i)=>xs.slice(i+1).map(b=>[a,b])); }

function permutations(xs) { return xs.length===0?[[]]:xs.flatMap((x,i)=>permutations(xs.filter((_,j)=>j!==i)).map(p=>[x,...p])); }

function same(a,b) { return JSON.stringify([...a].sort())===JSON.stringify([...b].sort()); }

function generate(seed) {
 const r=rng(seed), nodes=[0,1,2,3,4,5,6], past=nodes.slice(0,4), future=nodes.slice(4), allEdges=combinations(nodes), perms=permutations(nodes), seen=new Set(), questions=[],labels=[];
 const pick=a=>a[Math.floor(r()*a.length)];
 let attempts=0, count=0;
 while(count<32){
  insist(++attempts<=30000,"generator exhausted");
  const e=allEdges.filter(()=>r()<.2+.5*(count%4)/3);
  const adj=(a,b)=>e.some(([u,v])=>(u===a&&v===b)||(u===b&&v===a));
  const feasible=s=>!combinations(s).some(([u,v])=>adj(u,v));
  const choices=combinations(past).filter(feasible);
  const mask=s=>future.filter(v=>s.some(u=>adj(u,v)));
  const ext=s=>Array.from({length:8},(_,i)=>future.filter((_,j)=>i&(1<<j))).filter(f=>feasible([...s,...f])).map(f=>f.join(","));
  const overlap=(a,b)=>a.filter(x=>b.includes(x)).length;
  const candidates=[];
  for(const a of choices)for(const b of choices)for(const d of choices){
   if(a===b||a===d||b===d)continue;
   const ma=mask(a), mb=mask(b), md=mask(d);
   if(ma.length>0&&ma.length<future.length&&same(ma,mb)&&!same(ma,md)&&ma.length===md.length&&overlap(a,b)===overlap(a,d)) candidates.push([a,b,d]);
  }
  if(!candidates.length)continue;
  // Exact uncolored graph canonical form (7! permutations), not a WL approximation.
  let canon=null;
  for(const p of perms){const k=allEdges.map(([u,v])=>adj(p[u],p[v])?"1":"0").join("");if(canon===null||k<canon)canon=k;}
  if(seen.has(canon))continue;seen.add(canon);
  const [a,b,d]=pick(candidates), ma=mask(a);
  insist(same(ext(a),ext(b))&&!same(ext(a),ext(d)),"extension oracle");
  for(const s of [a,b,d])for(const v of future)insist(mask(s).includes(v)===!feasible([...s,v]),"singleton oracle");
  const names=shuffle(Array.from({length:90},(_,i)=>"v"+(i+10)),r).slice(0,7);
  const ren=s=>shuffle(s.map(i=>names[i]),r);
  const order=shuffle(nodes,r), nodeNames=order.map(i=>names[i]);
  const ed=shuffle(e.map(x=>ren(x)),r), fs=ren(future), ps=ren(past), as=ren(a);
  const packet=view=>({nodes:nodeNames,...(view==="edges"?{edges:ed}:{matrix:order.map(u=>order.map(v=>Number(adj(u,v))))}),past:ps,future:fs});
  const add=(task,view,j,prompt,truth,cls=null)=>{
   const id=`d${String(count).padStart(2,"0")}-${task}-${view}-${j}`;
   questions.push({id,prompt});labels.push({id,task,view,pair:count,truth,cls});
  };
  const vp=pick(ma), vn=pick(future.filter(v=>!ma.includes(v)));
  const promptData=(s,data)=>s+" "+JSON.stringify(data);
  for(const view of ["edges","matrix"]){
   const convention=view==="matrix"?" Matrix rows and columns follow nodes order.":" Edges are undirected.";
   const intro="Undirected graph. A set is independent if no two of its vertices share an edge."+convention;
   [vp,vn].forEach((v,j)=>add("membership",view,j,promptData(intro+" Is future vertex v blocked, i.e. does adding it to the independent set A make A non-independent? Answer exactly Yes or No.",{...packet(view),A:as,v:names[v]}),j===0?"Yes":"No",j===0));
   [b,d].forEach((s,j)=>{
    const bs=ren(s), mb=mask(s);
    add("reconstruct",view,j,promptData(intro+" Return exactly a JSON array containing two arrays: blocked future vertex names for A, then blocked future vertex names for B. A vertex is blocked if adding it destroys independence. No explanation.",{...packet(view),A:as,B:bs}),[ma.map(v=>names[v]).sort(),mb.map(v=>names[v]).sort()],j===0);
    add("end_to_end",view,j,promptData(intro+" A and B are independent sets. Do they allow exactly the same collection of independent future extensions? Answer exactly Yes or No.",{...packet(view),A:as,B:bs}),j===0?"Yes":"No",j===0);
   });
  }
  [b,d].forEach((s,j)=>add("compare_masks","explicit",j,promptData("Do these two sets contain exactly the same vertex names? Ignore order. Answer exactly Yes or No.",{A:ren(ma),B:ren(mask(s))}),j===0?"Yes":"No",j===0));
  count++;
 }
 insist(questions.length===448&&labels.length===448&&seen.size===32,"dataset counts");
 return {questions:shuffle(questions,r),labels:shuffle(labels,r),meta:{seed,graphs:count,attempts,vertex_count:7,exact_graph_dedup:true,training_authorized:false,synthetic_public_generator:true}};
}

function correct(raw,truth) {
 if(typeof raw!=="string")return false;
 if(typeof truth==="string")return raw===truth;
 try{const x=JSON.parse(raw);return Array.isArray(x)&&x.length===2&&x.every((a,i)=>Array.isArray(a)&&a.every(v=>typeof v==="string")&&new Set(a).size===a.length&&same(a,truth[i]));}catch{return false;}
}

function score(labels,records) {
 insist(Array.isArray(records)&&records.length===labels.length,"prediction count");
 const map=new Map();for(const p of records){insist(typeof p.id==="string"&&typeof p.raw==="string"&&!map.has(p.id),"duplicate or malformed prediction");map.set(p.id,p.raw);}
 const groups={};
 for(const l of labels){insist(map.has(l.id),"missing prediction");const key=l.task+"/"+l.view;(groups[key]??=[]).push({...l,hit:correct(map.get(l.id),l.truth),raw:map.get(l.id)});}
 const result={};
 for(const [key,g] of Object.entries(groups)){
  insist(g.length===64&&g.filter(x=>x.cls).length===32,"group balance");
  const pairs=new Map();for(const x of g){if(!pairs.has(x.pair))pairs.set(x.pair,[]);pairs.get(x.pair).push(x);}
  insist(pairs.size===32&&[...pairs.values()].every(p=>p.length===2&&p[0].cls!==p[1].cls),"pair balance");
  const hits=g.filter(x=>x.hit).length,positive=g.filter(x=>x.cls&&x.hit).length,negative=g.filter(x=>!x.cls&&x.hit).length,both=[...pairs.values()].filter(p=>p.every(x=>x.hit)).length;
  const binary=typeof g[0].truth==="string";
  const yes=binary?g.filter(x=>x.raw==="Yes").length:null,no=binary?g.filter(x=>x.raw==="No").length:null;
  result[key]={n:g.length,correct:hits,positive,negative,pairs_both:both,yes,no,invalid_binary:binary?64-yes-no:null,pass:hits>=48&&positive>=24&&negative>=24&&both>=20};
 }
 return {groups:result,promotion_authorized:false,training_authorized:false};
}

function selftest() {
 const d=generate(24681357);
 const exact=d.labels.map(l=>({id:l.id,raw:typeof l.truth==="string"?l.truth:JSON.stringify(l.truth)}));
 const oracle=score(d.labels,exact);insist(Object.values(oracle.groups).every(g=>g.pass&&g.correct===64),"oracle fixture");
 for(const raw of ["Yes","No","invalid","[[],[]]"]){let s=score(d.labels,exact.map(x=>({...x,raw})));insist(Object.values(s.groups).every(g=>!g.pass),"constant shortcut accepted");}
 let rejected=0;
 for(const bad of [exact.slice(1),[...exact.slice(1),exact[1]],[...exact.slice(1),{id:"not-in-corpus",raw:"Yes"}]]){try{score(d.labels,bad);}catch{rejected++;}}
 insist(rejected===3,"coverage guard");
 const repeat=generate(24681357);insist(JSON.stringify(d)===JSON.stringify(repeat),"not deterministic");
 insist(!correct('[["v1","v1"],[]]',[["v1"],[]]),"duplicate names");
 return {fixture_only:true,questions:d.questions.length,graphs:d.meta.graphs,groups:Object.keys(oracle.groups).length,constant_controls:4,invalid_record_controls:rejected,deterministic:true,model_calls:0};
}

if (require.main === module) {
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
 const sha=s=>crypto.createHash("sha256").update(s).digest("hex");
 const read=f=>JSON.parse(fs.readFileSync(f,"utf8"));
 const write=(f,v)=>fs.writeFileSync(f,JSON.stringify(v,null,2)+"\n",{flag:"wx"});
 const [cmd,a,b]=process.argv.slice(2);
 if(cmd==="selftest") console.log(JSON.stringify(selftest(),null,2));
 else if(cmd==="freeze"){
  const d=generate(Number(a));fs.mkdirSync(b);
  const q=d.questions.map(x=>({...x,prompt_sha256:sha(x.prompt)}));
  write(path.join(b,"questions.json"),q);write(path.join(b,"labels.json"),d.labels);
  write(path.join(b,"manifest.json"),{...d.meta,questions_sha256:sha(fs.readFileSync(path.join(b,"questions.json"))),labels_sha256:sha(fs.readFileSync(path.join(b,"labels.json")))});
 } else if(cmd==="score"){
  const m=read(path.join(a,"manifest.json")),qfile=path.join(a,"questions.json"),lfile=path.join(a,"labels.json");
  insist(sha(fs.readFileSync(qfile))===m.questions_sha256&&sha(fs.readFileSync(lfile))===m.labels_sha256,"frozen digest mismatch");
  const qs=read(qfile), pred=read(b), hashes=new Map(qs.map(x=>[x.id,x.prompt_sha256]));
  insist(pred.every(x=>hashes.has(x.id)&&x.prompt_sha256===hashes.get(x.id)),"prompt hash mismatch");
  console.log(JSON.stringify(score(read(lfile),pred),null,2));
 } else throw Error("Usage: selftest | freeze SEED OUTDIR | score FROZEN_DIR PREDICTIONS.json");
}
module.exports={generate,score,selftest};
