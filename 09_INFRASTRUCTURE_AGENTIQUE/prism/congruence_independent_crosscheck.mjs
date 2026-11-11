/* Independent JavaScript finite-model auditor for CONG-001.

 * Recomputes every global congruence judgment and every minimal proof
 * justification using only residues 0..59; DOES NOT import Python CRT
 * or the Python finite-model baseline.
 * This validates a constructed model, not general scientific evidence.
 */
import fs from "node:fs";
const [casesFile,ledgerFile]=process.argv.slice(2);
if(!casesFile||!ledgerFile)throw Error(
  "node congruence_independent_crosscheck.mjs frozen_cases.json ledger.json");
const input=JSON.parse(fs.readFileSync(casesFile,"utf8"));
const ledger=JSON.parse(fs.readFileSync(ledgerFile,"utf8"));
const universe=Array.from({length:60},(_,i)=>i);

function feasible(items){
  return universe.filter(x=>items.every(p=>x%p.m===p.r));
}
function classify(items,claim){
  const possible=feasible(items);
  if(!possible.length)return "inconsistent_environment";
  const yes=possible.filter(x=>x%claim.m===claim.r).length;
  return yes===possible.length?"entailed":yes===0?"refuted":"undetermined";
}
function compatiblePair(a,b){
  return feasible([a,b]).length>0;
}
function subsets(names){
  const out=[];
  for(let i=0;i<names.length;i++)out.push([names[i]]);
  for(let i=0;i<names.length;i++)
    for(let j=i+1;j<names.length;j++)out.push([names[i],names[j]]);
  for(let i=0;i<names.length;i++)
    for(let j=i+1;j<names.length;j++)
      for(let k=j+1;k<names.length;k++)out.push([names[i],names[j],names[k]]);
  return out;
}
function subset(a,b){return a.every(x=>b.includes(x));}
function supports(premises,q,kind){
  const names=Object.keys(premises).sort();
  const candidates=subsets(names);
  const smallest=[];
  for(const group of candidates){
    if(smallest.some(old=>subset(old,group)))continue;
    if(classify(group.map(k=>premises[k]),q)===kind)
      smallest.push(group);
  }
  return smallest;
}
const byScenario=new Map(input.scenarios.map(s=>[s.id,s]));
const eventsByScenario=new Map();
for(const e of ledger.results){
  if(!eventsByScenario.has(e.scenario))eventsByScenario.set(e.scenario,[]);
  eventsByScenario.get(e.scenario).push(e);
}
let judged=0,proofPaths=0,contradictions=0,alternativeStates=0,versions=0;
for(const scenario of input.scenarios){
  const events=eventsByScenario.get(scenario.id);
  if(!events||events.length!==scenario.events.length+1)
    throw Error("missing frozen states "+scenario.id);
  let current=new Set(scenario.initial);
  const histories=ledger.certificates_archive.find(a=>a.scenario===scenario.id);
  if(!histories||histories.archive.length!==events.length)
    throw Error("historical archive missing");
  const allSupports={};
  for(const [id,q] of Object.entries(scenario.queries)){
    allSupports[id]={
      entailed:supports(scenario.premises,q,"entailed"),
      refuted:supports(scenario.premises,q,"refuted"),
    };
  }
  for(let t=0;t<events.length;t++){
    const row=events[t];
    const op=t?scenario.events[t-1]:null;
    if(op){
      if(op.op==="activate")current.add(op.id);
      else if(op.op==="retract")current.delete(op.id);
      else throw Error("illegal frozen op");
    }
    const active=[...current].sort();
    if(JSON.stringify(row.active_premises)!==JSON.stringify(active))
      throw Error("active-state mismatch");
    const world=active.map(id=>scenario.premises[id]);
    const isConflict=feasible(world).length===0;
    const conflictPairs=[];
    for(let i=0;i<active.length;i++)
      for(let j=i+1;j<active.length;j++)
        if(!compatiblePair(scenario.premises[active[i]],
                           scenario.premises[active[j]]))
          conflictPairs.push([active[i],active[j]]);
    if(isConflict&&!conflictPairs.length)throw Error("conflict without pair");
    const hist=histories.archive[t];
    if(hist.version!==t||JSON.stringify(hist.active)!==JSON.stringify(active))
      throw Error("historical revision drift");
    for(const [key,q] of Object.entries(scenario.queries)){
      const expected=classify(world,q);
      const actual=row.omega[key];
      if(expected!==actual.status || expected!==row.baseline[key].status
          || expected!==row.truth[key] || expected!==hist.results[key].status)
        throw Error("wrong global logical verdict: "+scenario.id+" "+t+" "+key);
      if(JSON.stringify(actual.conflicts)!==JSON.stringify(conflictPairs))
        throw Error("wrong conflicting premise cores");
      const minimal=isConflict?[]:
        allSupports[key][expected]?.filter(s=>subset(s,active))??[];
      if(JSON.stringify(actual.proofs)!==JSON.stringify(minimal))
        throw Error("missing / forged minimal proof alternatives");
      for(const proof of actual.proofs){
        if(!subset(proof,active)||
           classify(proof.map(x=>scenario.premises[x]),q)!==expected)
          throw Error("false or stale proof certificate");
        proofPaths++;
      }
      if(actual.proofs.length>=2)alternativeStates++;
      if(isConflict){contradictions++;if(actual.proofs.length)
        throw Error("explosion under contradictory premises");}
      judged++;versions++;
    }
  }
}
const expectedJudgments=Object.values(ledger.summaries)
  .reduce((n,s)=>n+s.judgments,0);
if(judged!==expectedJudgments||judged!==276)
  throw Error("coverage mismatch "+judged);
if(proofPaths!==Object.values(ledger.summaries)
  .reduce((n,s)=>n+s.active_certificate_paths,0))
  throw Error("proof-path count mismatch");
console.log("CONG001_INDEPENDENT_JS_AUDIT "+JSON.stringify({
  result:"PASS",
  mathematical_model:"all 60 residues independently enumerated",
  judgments_recomputed:judged,
  active_supports_independently_checked:proofPaths,
  contradictory_query_states:contradictions,
  queries_with_two_or_more_proofs:alternativeStates,
  historical_query_versions_checked:versions,
  generalized_claim_of_omega_superiority:false,
}));
