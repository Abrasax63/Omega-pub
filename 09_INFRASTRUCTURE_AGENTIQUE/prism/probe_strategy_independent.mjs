/* OMEGA-PROBE-001 independent exact checker in JS/BigInt.
 *
 * Rebuild the 60-state universe, all five decision policies, expected cost
 * dynamic programs, fixed-order exhaustive optimizers, and all 1200 recorded
 * decisions from frozen JSON. No Python code reused; same public model.
 */
import fs from "node:fs";
const [modelFile,ledgerFile]=process.argv.slice(2);
if(!modelFile||!ledgerFile)
 throw Error("node probe_strategy_independent.mjs frozen.json result.json");
const input=JSON.parse(fs.readFileSync(modelFile,"utf8"));
const output=JSON.parse(fs.readFileSync(ledgerFile,"utf8"));
const worlds=[...Array(60).keys()];
const arms=["ZERO","GREEDY1","OMEGA_LOOKAHEAD2","FIXED_BEST","ADAPTIVE_DP_EXACT"];
const ALL=(1n<<60n)-1n;
const makeMask=p=>worlds.reduce((mask,w)=>mask|(w%p.m===p.r?1n<<BigInt(w):0n),0n);
const popcount=mask=>{let n=0;while(mask){mask&=mask-1n;n++;}return n;};
const idmask=(mask,w)=>((mask>>BigInt(w))&1n)!==0n;
const assert=(ok,msg)=>{if(!ok)throw Error(msg);};
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
let totalTraces=0,totalActions=0,totalIndependentExpectedStates=0;
for(const c of input.scenario_list){
 const p=c.probes,q=c.queries;
 const probes=p.map(makeMask),queries=q.map(makeMask);
 const n=p.length,allRem=(1<<n)-1;
 const size=belief=>popcount(belief);
 const unresolved=belief=>queries.filter(mask=>{
  const yes=size(belief&mask);
  return yes>0&&yes<size(belief);
 }).length;
 const stop=belief=>5*unresolved(belief)*size(belief);
 const cacheDP=new Map();
 function dp(belief,rem,horizon){
   const key=belief.toString()+":"+rem+":"+horizon;
   if(cacheDP.has(key))return cacheDP.get(key);
   let cost=stop(belief),action=null;
   if(rem!==0&&horizon!==0&&unresolved(belief)!==0){
    for(let i=0;i<n;i++){
      if(!(rem&(1<<i)))continue;
      const yes=belief&probes[i],no=belief^yes;
      if(yes===0n||no===0n)continue;
      const left=rem&~(1<<i),next=horizon<0?-1:horizon-1;
      const candidate=p[i].cost*size(belief)
        +dp(yes,left,next).cost+dp(no,left,next).cost;
      if(candidate<cost){cost=candidate;action=i;}
    }
   }
   const result={cost,action};
   cacheDP.set(key,result);
   return result;
 }
 const cacheFixed=new Map();
 function fixedVal(belief,order,pos){
   const key=belief.toString()+"/"+order.join(",")+"/"+pos;
   if(cacheFixed.has(key))return cacheFixed.get(key);
   let cost=stop(belief);
   if(pos<order.length&&unresolved(belief)!==0){
    const i=order[pos],yes=belief&probes[i],no=belief^yes;
    cost=(yes===0n||no===0n)
       ?fixedVal(belief,order,pos+1)
       :Math.min(cost,p[i].cost*size(belief)+fixedVal(yes,order,pos+1)
           +fixedVal(no,order,pos+1));
   }
   cacheFixed.set(key,cost);
   return cost;
 }
 function* permutations(a,start=0){
   if(start===a.length){yield a.slice();return;}
   for(let i=start;i<a.length;i++){
     // Keep Python's lexicographic order, not swap-generation order.
   }
 }
 function lexPerms(a){
   if(!a.length)return [[]];
   let res=[];
   for(const item of a){
     const remain=a.filter(x=>x!==item);
     for(const tail of lexPerms(remain))res.push([item,...tail]);
   }
   return res;
 }
 let bestFixed=stop(ALL),fixedOrder=[];
 for(const candidate of lexPerms([...Array(n).keys()])){
   const v=fixedVal(ALL,candidate,0);
   if(v<bestFixed){bestFixed=v;fixedOrder=candidate;}
 }
 const source=output.scenarios[c.id];
 assert(source!==undefined,"missing scenario "+c.id);
 assert(eq(source.best_fixed_probe_order,fixedOrder.map(i=>p[i].id)),
        "different optimal fixed probe order "+c.id);
 assert(source.fixed_schedule_optimum_loss_sum===bestFixed,
        "best fixed value mismatch");
 assert(source.full_adaptive_exact_loss_sum===dp(ALL,allRem,-1).cost,
        "full DP mismatch");
 assert(source.truncated_horizon1_initial_loss_sum===dp(ALL,allRem,1).cost,
        "greedy1 value mismatch");
 assert(source.truncated_horizon2_initial_loss_sum===dp(ALL,allRem,2).cost,
        "lookahead2 value mismatch");
 for(const arm of arms){
   const subset=output.ledger.filter(t=>t.scenario===c.id&&t.arm===arm);
   assert(subset.length===60,"not exactly 60 worlds/arm "+c.id+" "+arm);
   let sumLoss=0,sumCalls=0,sumResolved=0,sumCost=0,worst=0;
   for(let w=0;w<60;w++){
     const trace=subset.find(t=>t.world===w);
     assert(trace!==undefined,"missing world");
     let belief=ALL,rem=allRem,pos=0;
     let collectedCost=0,used=new Set();
     let j=0;
     while(true){
       let action=null;
       if(arm==="GREEDY1")action=dp(belief,rem,1).action;
       if(arm==="OMEGA_LOOKAHEAD2")action=dp(belief,rem,2).action;
       if(arm==="ADAPTIVE_DP_EXACT")action=dp(belief,rem,-1).action;
       if(arm==="FIXED_BEST"){
         while(pos<fixedOrder.length){
           const i=fixedOrder[pos],yes=belief&probes[i],no=belief^yes;
           if(unresolved(belief)===0)break;
           if(!yes||!no){pos++;continue;}
           const follow=p[i].cost*size(belief)
             +fixedVal(yes,fixedOrder,pos+1)
             +fixedVal(no,fixedOrder,pos+1);
           if(follow<stop(belief))action=i;
           break;
         }
       }
       if(action===null){
         assert(j===trace.trace.length,"extra probe when policy should stop");
         break;
       }
       assert(j<trace.trace.length,"recorded probe missing");
       assert(!used.has(action),"probe repeated");
       const yes=belief&probes[action],no=belief^yes;
       const answer=idmask(probes[action],w);
       const chosen=answer?yes:no;
       const step=trace.trace[j];
       assert(step.probe===p[action].id&&step.index===action&&
              step.answer===answer,"action or observation mismatch");
       assert(step.belief_size_before===size(belief)&&
              step.belief_size_after===size(chosen),
              "posterior belief drift");
       assert(step.cost===p[action].cost,"wrong verification price");
       assert(chosen!==0n,"hidden truth excluded from posterior");
       belief=chosen;
       rem&=~(1<<action);
       used.add(action);
       collectedCost+=p[action].cost;
       if(arm==="FIXED_BEST")pos++;
       j++;totalActions++;
     }
     const statuses=queries.map(mask=>{
        const yes=size(belief&mask);
        return yes===size(belief)?"entailed":yes===0?"refuted":"undetermined";
     });
     assert(eq(statuses,trace.truth_statuses),"wrong final answer");
     for(let k=0;k<q.length;k++){
       if(statuses[k]==="entailed")
          assert(idmask(queries[k],w),"false entailed certificate");
       if(statuses[k]==="refuted")
          assert(!idmask(queries[k],w),"false refuted certificate");
     }
     const pending=statuses.filter(s=>s==="undetermined").length;
     const loss=collectedCost+5*pending;
     assert(trace.cost===collectedCost&&trace.total_loss===loss&&
       trace.probe_calls===j&&trace.undetermined_queries===pending&&
       trace.resolved_queries===q.length-pending&&
       trace.final_belief_size===size(belief),"scoring mismatch");
     sumLoss+=loss;
     sumCalls+=j;
     sumResolved+=q.length-pending;
     sumCost+=collectedCost;
     worst=Math.max(worst,loss);
     totalTraces++;
   }
   const stat=source.arm_metrics[arm];
   assert(stat.sum_total_loss_exact===sumLoss&&
          stat.mean_loss===Math.round(sumLoss/60*1e6)/1e6&&
          stat.mean_probe_calls===Math.round(sumCalls/60*1e6)/1e6&&
          stat.mean_verification_cost===Math.round(sumCost/60*1e6)/1e6&&
          stat.mean_resolved_queries===Math.round(sumResolved/60*1e6)/1e6&&
          stat.worst_case_total_loss===worst&&stat.false_certificates===0,
          "mismatch in independent aggregate metrics");
 }
 totalIndependentExpectedStates+=cacheDP.size+cacheFixed.size;
}
assert(totalTraces===4*60*5,"expected 1200 complete traces");
console.log("OMEGA_PROBE_INDEPENDENT_JS_AUDIT "+JSON.stringify({
 result:"PASS",
 verified_traces:totalTraces,
 validated_actions:totalActions,
 independently_recomputed_policy_states:totalIndependentExpectedStates,
 best_fixed_order_independently_enumerated:true,
 exact_full_bellman_optimum_recomputed:true,
 misleading_certificates:0,
 real_scientific_problems_solved:0,
}));
