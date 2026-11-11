/* Second-path P5 public-calibration prompt audit.

Uses Node crypto and direct inspection of frozen source JSON; no imports from
Python fair preflight or Omega planner. Verifies all 144 requests, zero
information asymmetry, no hidden labels or simulated model execution.
*/
import fs from "node:fs";
import crypto from "node:crypto";
import cp from "node:child_process";
const [sourcePath,packetPath]=process.argv.slice(2);
if(!sourcePath||!packetPath)
  throw Error("node p5_abc_fair_independent.mjs cases.json packet.json");
const data=JSON.parse(fs.readFileSync(sourcePath,"utf8"));
const p=JSON.parse(fs.readFileSync(packetPath,"utf8"));
const actualBlob=cp.spawnSync("git",["hash-object",sourcePath],{encoding:"utf8"});
if(actualBlob.status!==0||
   actualBlob.stdout.trim()!=="3eb87dc5b8851dd30c753cb54e0d03659c62441b")
  throw Error("source JSON blob does not match frozen commitment");
const canonical=x=>Array.isArray(x)?x.map(canonical):
 (x!==null&&typeof x==="object"?
 Object.fromEntries(Object.keys(x).sort().map(k=>[k,canonical(x[k])])):x);
const bytes=x=>JSON.stringify(canonical(x));
const hash=x=>crypto.createHash("sha256").update(bytes(x),"utf8").digest("hex");
const assert=(ok,msg)=>{if(!ok)throw Error(msg);};
const arms=["A","B","C"],conditions=["intact","perturbed"];
const mission={github:"documentary",http:"documentary",
  uri:"computational",python:"computational"};
const roles={documentary:["refuter","bibliographer"],
  computational:["refuter","computational"]};
assert(p.status==="PREFLIGHT_ONLY_P5_LIVE_NOT_RUN", "false run status");
assert(p.real_model_calls===0&&p.human_independent_graders===0&&
       p.real_token_counts===null&&!p.external_holdout_evaluated,
       "phantom model or grading data");
assert(p.case_count===24&&p.prompt_count===144&&p.requests.length===144,
       "24 × 2 × 3 input population incomplete");
const ids=new Set(data.cases.map(x=>x.id));
assert(ids.size===24,"frozen case count drift");
let groups=0,checked=0,changedPrimary=0;
const forbidden=[
 "truth","gold","answer_key","correct_answer","reference_answer",
 "secondary_note_is_fabricated","spoof_primary_in_adversarial",
 "is_spoofed","condition","expected","label","head_sha"
];
function walk(x){
 if(Array.isArray(x))return x.forEach(walk);
 if(x&&typeof x==="object"){
  for(const [k,v] of Object.entries(x)){
   assert(!forbidden.includes(k),"grade key leaked "+k);
   walk(v);
  }
 }
}
for(const item of data.cases){
 assert(mission[item.domain],"unknown public domain");
 for(const condition of conditions){
  const matches=p.requests.filter(x=>x.case_id===item.id&&
                                        x.condition===condition);
  assert(matches.length===3,"missing group "+item.id+"/"+condition);
  assert(matches.map(x=>x.arm).join(",")==="A,B,C","wrong arm order");
  const core=matches.map(x=>x.request.input.shared);
  assert(bytes(core[0])===bytes(core[1])&&bytes(core[1])===bytes(core[2]),
         "unequal shared case information");
  const instructions=matches.map(x=>x.request.instructions);
  assert(instructions[0]===instructions[1]&&
         instructions[1]===instructions[2],"unequal common instructions");
  let expectedPrimary=item.truth;
  if(condition==="perturbed"&&item.spoof_primary_in_adversarial){
    expectedPrimary=!expectedPrimary;
    changedPrimary++;
  }
  const shared=core[0];
  assert(shared.question===item.question&&
         shared.task_domain===item.domain&&
         shared.mission_type===mission[item.domain]&&
         shared.reference_url_not_opened===item.reference,
         "public source context drift");
  assert(shared.observations.length===2&&
         shared.observations[0].claim_text===(
         expectedPrimary?"Cette affirmation est vraie.":
           "Cette affirmation est fausse."),"primary simulated claim drift");
  const secondary=shared.observations[1].claim_text;
  assert(secondary.includes(item.secondary_note_claim?"est vraie":"est fausse"),
         "secondary note changed");
  assert(!Object.hasOwn(shared,"condition"),"condition visible to models");
  assert(matches[0].request.input.strategy!==matches[1].request.input.strategy &&
         matches[1].request.input.strategy!==matches[2].request.input.strategy,
         "no strategic treatment");
  assert(bytes(matches[2].adaptive_roles)===bytes(roles[mission[item.domain]]),
         "Omega planner role selection changed");
  assert(matches[1].fixed_roles.length===5,
         "fixed B not five perspectives");
  for(const row of matches){
    assert(Object.keys(row.request.input).sort().join(",")==="shared,strategy",
           "privileged C-only context");
    walk(row.request);
    assert(row.shared_sha256===hash(row.request.input.shared)&&
           row.prompt_sha256===hash(row.request),"invalid prompt hashes");
    assert(row.model_calls===0,"model execution invented");
    checked++;
  }
  groups++;
 }
}
assert(changedPrimary===8,"unexpected simulated primary perturbations");
assert(groups===48&&checked===144,"coverage mismatch");
assert(p.synthetic_preflight_schedule.length===48,"bad schedule count");
for(const order of p.synthetic_preflight_schedule)
  assert(order.arms.slice().sort().join(",")==="A,B,C","bad arm schedule");
console.log("OMEGA_P5_ABC_FAIR_JS_AUDIT "+JSON.stringify({
 result:"PASS",
 calibration_cases:24,
 conditions:2,
 source_toggles_simulated:8,
 identical_evidence_groups:48,
 prompts_independently_checked:checked,
 C_extra_facts:0,
 real_llm_calls:0,
 blinded_model_comparison_executed:false,
}));
