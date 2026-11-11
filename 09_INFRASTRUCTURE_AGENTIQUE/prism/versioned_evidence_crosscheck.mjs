/* Independent JavaScript audit for OMEGA-EVIDENCE-001.
 *
 * Reconstruct selected paths, 40 revision transitions and the index baseline
 * from frozen Git tree metadata; hash real Git blobs with SHA-256.
 * Re-verify *all* archived version-bound certificate dependencies at the
 * commit claimed by each original certificate.
 *
 * Different language and algorithmic implementation than Python. Shared
 * historical Git repository, not independent source authorship attestation.
 */
import fs from "node:fs";
import crypto from "node:crypto";
import cp from "node:child_process";

const [gitDir,ledgerFile]=process.argv.slice(2);
if(!gitDir||!ledgerFile)throw Error(
 "node versioned_evidence_crosscheck.mjs GIT_REPO LEDGER_JSON");

const data=JSON.parse(fs.readFileSync(ledgerFile,"utf8"));
const HEAD="49943b5a94413a530761350f04e896f76e8d620e";
if(data.frozen_source_commit!==HEAD)throw Error("source ref changed");
const cmd=(...args)=>{
 const res=cp.spawnSync("git",["-C",gitDir,...args],{
   maxBuffer:64*1024*1024,encoding:null});
 if(res.status!==0)throw Error(
   "Git error "+args.join(" ")+": "+res.stderr?.toString("utf8").slice(0,500));
 return res.stdout;
};
const commits=cmd("rev-list","--first-parent","--max-count=41",HEAD)
  .toString("utf8").trim().split("\n").reverse();
if(commits.length!==41||commits[40]!==HEAD||
   commits[0]!==data.source_start_commit)throw Error("wrong commit sequence");

const prefixes=["src/flask/","tests/","docs/"];
const suffixes=[".py",".rst",".md",".toml"];
function sourceTree(commit){
 const out=new Map();
 const rows=cmd("ls-tree","-r","-z",commit,"--",
   "src/flask","tests","docs");
 for(const item of rows.toString("utf8").split("\0")){
  if(!item)continue;
  const i=item.indexOf("\t");
  if(i<0)throw Error("invalid git tree");
  const [mode,type,oid]=item.slice(0,i).split(" ");
  const name=item.slice(i+1);
  if(type==="blob"&&prefixes.some(q=>name.startsWith(q))&&
      suffixes.some(q=>name.endsWith(q))){
    out.set(name,{mode,oid});
  }
 }
 return out;
}
const trees=commits.map(sourceTree);
const ranked=[...trees[0].keys()].sort((a,b)=>{
 const x=crypto.createHash("sha256").update(a).digest();
 const y=crypto.createHash("sha256").update(b).digest();
 return Buffer.compare(x,y)||(a<b?-1:a>b?1:0);
}).slice(0,128);
if(JSON.stringify(ranked)!==JSON.stringify(data.selected_paths))
 throw Error("Independent source-path selection mismatch");

const deps=new Map();
for(let i=0;i<ranked.length;i++){
 const id=String(i).padStart(3,"0");
 deps.set("single:"+id,[ranked[i]]);
 deps.set("pair:"+id,[ranked[i],ranked[(i+1)%ranked.length]]);
 deps.set("triple:"+id,[ranked[i],ranked[(i+1)%ranked.length],
                         ranked[(i+2)%ranked.length]]);
}
if(deps.size!==data.n_compound_assertions)throw Error("claim count mismatch");
const digests=new Map();
function hashBlob(oid){
 if(digests.has(oid))return digests.get(oid);
 if(!/^[0-9a-f]{40}$/.test(oid))throw Error("bad blob oid");
 const h=crypto.createHash("sha256")
   .update(cmd("cat-file","blob",oid)).digest("hex");
 digests.set(oid,h);
 return h;
}
const initial=new Map(ranked.map(p=>[p,hashBlob(trees[0].get(p).oid)]));
const current=new Map(initial);
const archive=new Map();
for(const [id,paths] of deps){
 archive.set(id,[{
  certified_at_commit:commits[0],
  digests:paths.map(p=>[p,current.get(p)]),
 }]);
}
const checksum=(obj)=>JSON.stringify(obj);
let checkedEvents=0,checksumFailures=0,materialChanges=0;
let remainingFalse=0,changedRelevantTotal=0;
for(let idx=1;idx<=40;idx++){
 const prior=trees[idx-1],next=trees[idx];
 const changed=new Set();
 for(const p of ranked){
  const a=prior.get(p),b=next.get(p);
  if(!a||!b||a.oid!==b.oid||a.mode!==b.mode)changed.add(p);
 }
 const python=data.events[idx-1];
 if(python.step!==idx||python.previous_commit!==commits[idx-1]||
    python.commit!==commits[idx]||
    python.n_portfolio_changed_paths!==changed.size)
    throw Error("event metadata mismatch on step "+idx);
 const diff=new Set(cmd("diff","--no-renames","--name-only","-z",
   commits[idx-1],commits[idx]).toString("utf8")
   .split("\0").filter(Boolean).filter(p=>ranked.includes(p)));
 if(changed.size!==diff.size||[...changed].some(p=>!diff.has(p)))
   throw Error("tree-vs-diff inconsistency "+idx);
 changedRelevantTotal+=changed.size;
 for(const p of changed){
   current.set(p,next.has(p)?null:"missing");
 }
 const pending=ranked.filter(p=>current.get(p)===null&&next.has(p))
    .sort((a,b)=>{
      if(changed.has(a)!==changed.has(b))return changed.has(a)?-1:1;
      return a<b?-1:a>b?1:0;
    });
 const scheduled=pending.slice(0,8);
 const selectedPython=python.decisions["dependency_index_8"]
  .chosen_for_verification;
 if(checksum(scheduled)!==checksum(selectedPython))
   throw Error("different verification choices at step "+idx);
 for(const p of scheduled) current.set(p,hashBlob(next.get(p).oid));

 let correct=0,wrong=0,pendingClaims=0,unavailable=0;
 let untouchedCorrect=0,untouchedWrong=0;
 for(const [id,paths] of deps){
  const vals=paths.map(p=>current.get(p));
  if(vals.includes("missing"))unavailable++;
  else if(vals.includes(null))pendingClaims++;
  else{
   const valid=paths.every(p=>{
    const t=next.get(p);
    return t!==undefined&&current.get(p)===hashBlob(t.oid);
   });
   valid?correct++:wrong++;
  }
  const naiveValid=paths.every(p=>{
    const t=next.get(p);
    return t!==undefined&&initial.get(p)===hashBlob(t.oid);
  });
  naiveValid?untouchedCorrect++:untouchedWrong++;

  if(vals.every(v=>v!==null&&v!=="missing")){
   const signature=paths.map(p=>[p,current.get(p)]);
   const hist=archive.get(id),last=hist[hist.length-1];
   if(checksum(last.digests)!==checksum(signature))
    hist.push({certified_at_commit:commits[idx],digests:signature});
  }
 }
 const score=python.scores["dependency_index_8"];
 const expected={
  correct_current:correct,
  false_current:wrong,
  pending:pendingClaims,
  unavailable,
 };
 for(const [key,val] of Object.entries(expected)){
  if(score[key]!==val||
     python.scores["omega_ledger_8"][key]!==val)
   throw Error("JavaScript vs Python policy score at step "+idx+
     " key="+key+" expected="+val+" got="+score[key]);
 }
 const noRefresh=python.scores["no_refresh"];
 if(noRefresh.correct_current!==untouchedCorrect||
    noRefresh.false_current!==untouchedWrong||
    noRefresh.pending!==0||noRefresh.unavailable!==0)
    throw Error("Naive baseline incorrectly evaluated at step "+idx);
 const full=python.scores["full_reverify"];
 if(full.correct_current+full.unavailable!==deps.size||
    full.false_current!==0||full.pending!==0)
    throw Error("Full scan must be complete at step "+idx);
 const historyCount=[...archive.values()].reduce((a,v)=>a+v.length,0);
 if(historyCount!==score.preserved_certificate_versions)
   throw Error("versioned certificate count mismatch "+idx);
 if(score.false_current!==0)throw Error("stale claim emitted current");
 checkedEvents++;
 materialChanges+=changed.size;
 remainingFalse+=noRefresh.false_current;
}
const records=data.archived_omega_certificates;
const currentHist=[...archive.entries()].reduce((out,[id,recs])=>{
 out[id]=recs;return out;},{});
const recordIds=Object.keys(records).sort();
if(checksum(recordIds)!==checksum([...deps.keys()].sort()))
 throw Error("historical certificate ID set differs");
let archived=0,previousCommitReferenced=0,sourceRevalidations=0;
const treeFor=new Map(commits.map((sha,i)=>[sha,trees[i]]));
for(const key of recordIds){
 const expected=archive.get(key),fromPython=records[key];
 if(checksum(expected)!==checksum(fromPython))
   throw Error("independent certificate archive mismatch for "+key);
 for(const item of fromPython){
  const tree=treeFor.get(item.certified_at_commit);
  if(!tree)throw Error("archive references unknown source commit");
  if(item.certified_at_commit!==HEAD)previousCommitReferenced++;
  for(const [path,digest] of item.digests){
   if(!tree.has(path)||hashBlob(tree.get(path).oid)!==digest)
      throw Error("historical certificate invalid for own Git version");
   sourceRevalidations++;
  }
  archived++;
 }
}
if(checkedEvents!==40||archived===0||sourceRevalidations===0)
 throw Error("incomplete independent audit");
console.log("OMEGA_VERSIONED_EVIDENCE_JS_AUDIT "+JSON.stringify({
 verification:"PASS",
 source_head:HEAD,
 events_independently_replayed:checkedEvents,
 sampled_paths:ranked.length,
 inspected_changes_in_portfolio:materialChanges,
 no_refresh_false_current_claim_steps:remainingFalse,
 archived_certificates_independently_reconstructed:archived,
 versioned_source_dependencies_rehashed:sourceRevalidations,
 historical_certificates_reference_prior_commits:previousCommitReferenced,
 indexed_policy_false_current_claim_steps:0,
 compare_source:"Git diff and Git tree/blob independent from Python policy",
}));
