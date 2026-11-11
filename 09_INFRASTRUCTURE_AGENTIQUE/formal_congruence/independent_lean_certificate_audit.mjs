/* OMEGA-LEAN-001 independent finite-residue certificate auditor.

 * Recompute frozen 24 revision states and all 91 judgments from scratch.
 * Verify exact source versions, proof-support minimality, certificate keys,
 * historical applicability and Lean negative-control outcomes.
 *
 * Only Lean itself validates the typed proof terms. This JS auditor cannot
 * substitute for running the Lean 4 kernel; it protects the *global* guard
 * that Lean's ex-falso rule alone cannot provide.
 */
import fs from "node:fs";
import crypto from "node:crypto";

const [casesPath,resultsPath]=process.argv.slice(2);
if(!casesPath||!resultsPath)
  throw Error("node independent_lean_certificate_audit.mjs cases.json results.json");
const corpus=JSON.parse(fs.readFileSync(casesPath,"utf8"));
const log=JSON.parse(fs.readFileSync(resultsPath,"utf8"));
if(corpus.common_modulus!==60||log.frozen_cases_commit!==
  "de4a08399a0f99d420f13e360fbf1deed5785161")
  throw Error("frozen corpus mismatch");

const U=Array.from({length:60},(_,i)=>i);
const archive=log.historical_certificates;
const events=log.records;
const canonical=value=>
 Array.isArray(value)?value.map(canonical):
 value!==null&&typeof value==="object"?
 Object.fromEntries(Object.keys(value).sort().map(k=>[k,canonical(value[k])])):
 value;
const hash=value=>crypto.createHash("sha256")
 .update(JSON.stringify(canonical(value)),"utf8").digest("hex");
const models=items=>U.filter(n=>items.every(c=>n%c.m===c.r));
const category=(items,q)=>{
 const feasible=models(items);
 if(!feasible.length)return "inconsistent_environment";
 const n=feasible.filter(x=>x%q.m===q.r).length;
 return n===feasible.length?"entailed":n===0?"refuted":"undetermined";
};
const orderedPairs=ids=>{
 const pairs=[];
 for(let i=0;i<ids.length;i++)for(let j=i+1;j<ids.length;j++)
  pairs.push([ids[i],ids[j]]);
 return pairs;
};
const subset=(xs,ys)=>xs.every(x=>ys.includes(x));
let states=0,judgments=0,checkedProofApplications=0,
 contradictions=0,restored=0,alternatives=0,refuted=0,unknown=0,entailed=0;
const summaries={calibration:{},test:{}};
const count=(key,split,delta=1)=>{
 summaries[split][key]=(summaries[split][key]||0)+delta;
};
const seen=new Set();
for(const scenario of corpus.scenarios){
 let active=new Set(scenario.initial);
 let versions=JSON.parse(JSON.stringify(scenario.sources));
 const statesFor=events.filter(x=>x.scenario===scenario.id);
 if(statesFor.length!==scenario.events.length+1)
   throw Error("missing revisions "+scenario.id);
 for(let step=0;step<statesFor.length;step++){
  if(step>0){
   const action=scenario.events[step-1];
   if(action.op==="activate")active.add(action.id);
   else if(action.op==="retract")active.delete(action.id);
   else if(action.op==="replace")versions[action.id]=structuredClone(action.value);
   else throw Error("unexpected event");
  }
  const row=statesFor[step];
  if(row.step!==step||row.split!==scenario.split)
    throw Error("revision metadata mismatched");
  const current=Object.fromEntries([...active].sort().map(id=>[id,versions[id]]));
  if(JSON.stringify(row.active)!==JSON.stringify(current))
    throw Error("stale or forged current source versions");
  const full=Object.values(current);
  const globallyConsistent=models(full).length>0;
  if(globallyConsistent!==row.consistent)
    throw Error("inconsistency guard differs from finite universe");
  const pairs=orderedPairs(Object.keys(current)).filter(([a,b])=>
    models([current[a],current[b]]).length===0);
  if(JSON.stringify(row.conflicting_pairs)!==JSON.stringify(pairs))
    throw Error("conflict core differs from independent enumeration");
  states++;
  count("states",scenario.split);
  for(const [qid,q] of Object.entries(scenario.goals)){
   const out=row.queries[qid];
   if(!out)throw Error("missing goal");
   const verdict=category(full,q);
   if(verdict!==out.status)
    throw Error("invalid global verdict "+scenario.id+" "+step+" "+qid);
   if(!globallyConsistent&&(out.proof_keys.length||
      out.status!=="inconsistent_environment"))
    throw Error("logical explosion was promoted");
   const validProofKeys=[];
   for(const key of out.proof_keys){
     const prior=archive[key];
     if(!prior||prior.query_id!==qid||prior.kind!==verdict||
        JSON.stringify(prior.query)!==JSON.stringify(q))
       throw Error("forged or mislabeled proof certificate");
     const names=prior.source_ids;
     if(!names.length||names.length>3||!subset(names,Object.keys(current)))
       throw Error("inactive or overlarge source used");
     const assumed=names.map(x=>current[x]);
     if(JSON.stringify(assumed)!==JSON.stringify(prior.premises))
       throw Error("certificate from outdated source version");
     if(category(assumed,q)!==verdict)
       throw Error("invalid modular proof support");
     for(let drop=0;drop<names.length;drop++){
       const sub=names.filter((_,i)=>i!==drop).map(x=>current[x]);
       if(category(sub,q)===verdict)
         throw Error("redundant, nonminimal proof support");
     }
     const exact={
       scenario:scenario.id,goal:qid,statement:q,kind:verdict,
       support:names.map(x=>({source:x,...current[x]}))
     };
     if(hash(exact)!==key)throw Error("certificate hash changed");
     if(seen.has(key))restored++;
     seen.add(key);
     validProofKeys.push(key);
     checkedProofApplications++;
   }
   // Independently enumerate every minimal support of size up to 3.
   const ids=Object.keys(current);
   const supportSets=[];
   for(let i=0;i<ids.length;i++)supportSets.push([ids[i]]);
   for(let i=0;i<ids.length;i++)for(let j=i+1;j<ids.length;j++)
     supportSets.push([ids[i],ids[j]]);
   for(let i=0;i<ids.length;i++)for(let j=i+1;j<ids.length;j++)
     for(let k=j+1;k<ids.length;k++)
       supportSets.push([ids[i],ids[j],ids[k]]);
   const minimal=[];
   if(globallyConsistent&&["entailed","refuted"].includes(verdict)){
     for(const subsetIds of supportSets){
       if(minimal.some(previous=>subset(previous,subsetIds)))continue;
       if(category(subsetIds.map(x=>current[x]),q)===verdict)
         minimal.push(subsetIds);
     }
   }
   const found=validProofKeys.map(key=>archive[key].source_ids);
   if(JSON.stringify(found)!==JSON.stringify(minimal))
     throw Error("missing viable proof paths or incorrect support ordering");
   if(out.proof_keys.length>=2){alternatives++;count("multiple_support_cases",scenario.split);}
   if(verdict==="entailed")entailed++;
   if(verdict==="refuted")refuted++;
   if(verdict==="undetermined")unknown++;
   if(verdict==="inconsistent_environment")contradictions++;
   count(verdict,scenario.split);
   count("judgments",scenario.split);
   count("active_proof_paths",scenario.split,out.proof_keys.length);
   judgments++;
  }
 }
}
if(states!==24||judgments!==91)
 throw Error("frozen state/claim count mismatch "+states+" "+judgments);
for(const split of ["calibration","test"])
 for(const [key,value] of Object.entries(summaries[split]))
   if(log.summaries[split]?.[key]!==value)
     throw Error("independent summary disagrees "+split+" "+key);
if(seen.size!==Object.keys(archive).length||
   seen.size!==log.unique_historical_verified_implications)
 throw Error("lost or fabricated history entries");
const costs=log.lean_check_counts;
if(JSON.stringify(costs.strong_atms_index)!==
   JSON.stringify(costs.omega_proof_ledger))
 throw Error("Omega cost differs from strong index");
for(const mode of Object.keys(costs)){
 const rec=costs[mode];
 if(rec.checked_theorem_declarations!==3*rec.compiled_proof_chains)
   throw Error("theorem chain count mismatch");
 if(rec.compiled_files>states)
   throw Error("multiple compiles in one state undocumented");
}
const controls=log.negative_kernel_tests;
if(controls.forged.lean_compiled||
   controls.missing_source.lean_compiled||
   !controls.ex_falso_is_derivable.lean_compiled)
 throw Error("Lean negative/contradictory assumption controls failed");
console.log("OMEGA_LEAN_INDEPENDENT_AUDIT "+JSON.stringify({
 result:"PASS",
 n_states:states,
 n_judgments:judgments,
 implications_rechecked_from_modular_models:checkedProofApplications,
 unique_versioned_certificates:seen.size,
 repeated_certificates_reused_at_later_states:restored,
 conditional_ex_falso_compiles_but_global_claim_is_blocked:true,
 atms_and_omega_verified_leancall_parity:true,
 independence_scope:"JS finite arithmetic versus Lean4 actual proof kernel",
 no_superiority_claim:true,
}));
