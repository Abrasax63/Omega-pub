/* Independent JS reimplementation of training/selection for BOTH tree learners.
 * Do not import Python model code. It independently re-trains all 10 official
 * folds using only 9 train folds each and compares exact per-instance solver
 * choices and objective to the preregistered Python run.
 *
 * This is a verification of a historical empirical replay, not a new trial.
 */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const [dir,resultPath]=process.argv.slice(2);
if(!dir||!resultPath)throw Error("node aslib_wpms_tree_independent.mjs DATA_DIR RESULT_JSON");
const hashes={
 "feature_values.arff":"4684f66e4111ce1dbef69e68a14367ce93293853",
 "algorithm_runs.arff":"45aec3038b4304714c8047ad79ff0171c59dc5c8",
 "cv.arff":"a81207d105555c96a7278ee915f3ff3bd93377b2",
};
function arff(name){
 const data=fs.readFileSync(path.join(dir,name));
 const header=Buffer.from("blob "+data.length+"\0");
 const sha=crypto.createHash("sha1").update(header).update(data).digest("hex");
 if(sha!==hashes[name])throw Error("Git blob mismatch "+name);
 return data.toString("utf8").split(/\r?\n/)
   .filter(x=>x && !x.startsWith("@") && !x.startsWith("%") && x.includes(","))
   .map(x=>x.split(","));
}
const feats=arff("feature_values.arff");
const runs=arff("algorithm_runs.arff");
const cv=arff("cv.arff");
const feature=new Map(feats.map(r=>[r[0],r.slice(2).map(Number)]));
const fold=new Map(cv.map(r=>[r[0],Number(r[2])]));
const solvers=[...new Set(runs.map(r=>r[2]))].sort();
const costs=new Map();
for(const [id,rep,algo,runtime] of runs){
 if(!costs.has(id))costs.set(id,new Map());
 costs.get(id).set(algo,Number(runtime));
}
if(feats.length!==630||runs.length!==11340||solvers.length!==18||fold.size!==630)
 throw Error("Unexpected WPMS population");
const py=JSON.parse(fs.readFileSync(resultPath,"utf8"));
const indexed=new Map(py.ledger.filter(x=>x.arm.startsWith("TREE_")||x.arm==="OMEGA_cost_lookahead2")
  .map(x=>[x.arm+"|"+x.instance,x]));
const indices=[...feature.keys()].sort();

function median(values){
 const sorted=values.slice().sort((a,b)=>a-b);
 const n=sorted.length;
 return n%2?sorted[Math.floor(n/2)]:
    (sorted[n/2-1]+sorted[n/2])/2;
}

let nCompared=0,nRootCompared=0;
let costDiffMax=0;
for(let k=1;k<=10;k++){
 const train=indices.filter(i=>fold.get(i)!==k);
 const test=indices.filter(i=>fold.get(i)===k);
 const m=37;
 const mean=[],std=[];
 for(let j=0;j<m;j++){
  const mu=train.reduce((v,id)=>v+feature.get(id)[j],0)/train.length;
  const st=Math.sqrt(train.reduce((v,id)=>
      v+(feature.get(id)[j]-mu)**2,0)/train.length)||1;
  mean.push(mu);std.push(st);
 }
 const vec=new Map([...train,...test].map(id=>[
   id,feature.get(id).map((x,j)=>Math.max(-10,Math.min(10,(x-mean[j])/std[j])))
 ]));
 const threshold=Array.from({length:m},(_,j)=>median(train.map(id=>vec.get(id)[j])));
 const bins=new Map(train.map(id=>[id,threshold.map((value,j)=>vec.get(id)[j]<=value)]));
 const cache=new Map();
 function leaf(items){
  const key=items.join("\u0000");
  if(cache.has(key))return cache.get(key);
  const totals=solvers.map(a=>{
   let sum=0;for(const id of items)sum+=costs.get(id).get(a);
   return sum;
  });
  let best=0;
  for(let j=1;j<totals.length;j++)if(totals[j]<totals[best])best=j;
  const result={loss:totals[best],tree:{type:"leaf",solver:solvers[best]}};
  cache.set(key,result);return result;
 }
 function split(items,j){
  const left=[],right=[];
  for(const id of items)(bins.get(id)[j]?left:right).push(id);
  return [left,right];
 }
 function depth1(items){
  let current=leaf(items);
  for(let j=0;j<m;j++){
   const [yes,no]=split(items,j);
   if(!yes.length||!no.length)continue;
   const a=leaf(yes),b=leaf(no);
   const loss=a.loss+b.loss;
   if(loss<current.loss-1e-9)current={
    loss,tree:{type:"split",feature:j,threshold:threshold[j],
               yes:a.tree,no:b.tree}
   };
  }
  return current;
 }
 function greedy(){
  const root=depth1(train);
  if(root.tree.type==="leaf")return root;
  const j=root.tree.feature;
  const [a,b]=split(train,j);
  const yes=depth1(a),no=depth1(b);
  return {loss:yes.loss+no.loss,
   tree:{type:"split",feature:j,threshold:threshold[j],
         yes:yes.tree,no:no.tree}};
 }
 function lookahead(){
  let current=leaf(train);
  for(let j=0;j<m;j++){
   const [a,b]=split(train,j);
   if(!a.length||!b.length)continue;
   const yes=depth1(a),no=depth1(b);
   const loss=yes.loss+no.loss;
   if(loss<current.loss-1e-9)current={
    loss,tree:{type:"split",feature:j,threshold:threshold[j],
               yes:yes.tree,no:no.tree}
   };
  }
  return current;
 }
 function predict(row,tree){
  while(tree.type==="split")tree=row[tree.feature]<=tree.threshold?tree.yes:tree.no;
  if(tree.type!=="leaf")throw Error("Bad node");
  return tree.solver;
 }
 const fitted={
   "TREE_greedy1":depth1(train),
   "TREE_greedy2":greedy(),
   "OMEGA_cost_lookahead2":lookahead()
 };
 const pf=py.folds[k-1];
 if(pf.fold!==k)throw Error("Wrong fold order");
 for(const [arm,fit] of Object.entries(fitted)){
  const expected=pf.train_loss[arm];
  const tol=Math.max(1e-5,Math.abs(expected)*1e-10);
  if(Math.abs(fit.loss-expected)>tol)
   throw Error("Train objective differs: "+arm+" fold "+k+" "+fit.loss+" vs "+expected);
  const actualRoot=fit.tree.feature??null;
  const label=arm==="TREE_greedy1"?"greedy1":arm==="TREE_greedy2"?"greedy2":"lookahead2";
  if(actualRoot!==(pf.tree_root_features[label]??null))
   throw Error("Root feature mismatch: "+arm+" "+k+" "+actualRoot);
  nRootCompared++;
  for(const id of test){
   const selected=predict(vec.get(id),fit.tree);
   const record=indexed.get(arm+"|"+id);
   if(!record || record.fold!==k || selected!==record.selected_solver)
    throw Error("Independent tree prediction mismatch: "+arm+" fold "+k+" "+id+
       " expected="+record?.selected_solver+" actual="+selected);
   nCompared++;
  }
 }
}
if(nCompared!==1890 || nRootCompared!==30)throw Error("Incomplete verification");
console.log("ASLIB_WPMS_INDEPENDENT_TREE_CHECK "+JSON.stringify({
 source_commit:py.source_commit,
 exact_per_instance_solver_choices:nCompared,
 independently_refit_training_objectives:nRootCompared,
 verification:"PASS",
 algorithm:"Independent JS cost-sensitive greedy and two-step lookahead"
}));
