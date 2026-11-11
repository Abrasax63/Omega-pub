/* Independent JavaScript audit of ASlib MaxSAT-WPMS-2016 CV.
 * Intentionally does not import the Python benchmark. Reads only the already
 * downloaded, SHA-verified source bytes and the Python output for comparison.
 * The KNN feature transform and fixed k values were preregistered.
 */
import fs from "node:fs";
import path from "node:path";

const argv=process.argv.slice(2);
if (argv.length!==2) throw Error("node aslib_wpms_independent_crosscheck.mjs DATA_DIR RESULT_JSON");
const [dir,resultPath]=argv;

function arff(name){
  const t=fs.readFileSync(path.join(dir,name),"utf8");
  return t.split(/\r?\n/).filter(s=>s && !s.startsWith("@")
      && !s.startsWith("%") && s.includes(",")).map(s=>s.split(","));
}
const F=arff("feature_values.arff");
const R=arff("algorithm_runs.arff");
const C=arff("cv.arff");
const Q=arff("feature_costs.arff");

const features=new Map(F.map(r=>[r[0],r.slice(2).map(Number)]));
const fold=new Map(C.map(r=>[r[0],Number(r[2])]));
const cost=new Map(Q.map(r=>[r[0],Number(r[2])]));
const performances=new Map(),stat=new Map(),algos=[...new Set(R.map(r=>r[2]))].sort();
for (const [id,rep,algo,runtime,status] of R){
  if (!performances.has(id)){performances.set(id,new Map());stat.set(id,new Map());}
  performances.get(id).set(algo,Number(runtime));
  stat.get(id).set(algo,status);
}
const ids=[...fold.keys()],summary=Object.fromEntries(
  ["SBS","KNN5","KNN15","VBS_oracle"].map(s=>[s,{sum:0,solved:0,n:0}])
);
if (ids.length!==630||algos.length!==18||R.length!==11340||F.length!==630) throw Error("input data mismatch");

function measure(method,id,alg,charged){
  const rec=summary[method];
  rec.sum += performances.get(id).get(alg)+(charged?cost.get(id):0);
  rec.solved += stat.get(id).get(alg)==="ok"?1:0;
  rec.n++;
}
function chosen(rows){
  let best=null,score=Infinity;
  for(const alg of algos){
    let curr=0;
    for(const id of rows)curr+=performances.get(id).get(alg);
    curr/=rows.length;
    if(curr<score-1e-11){score=curr;best=alg;}
  }
  return best;
}

for(let f=1;f<=10;f++){
  const train=ids.filter(id=>fold.get(id)!==f).sort();
  const test=ids.filter(id=>fold.get(id)===f).sort();
  const mu=[],sigma=[];
  for(let j=0;j<37;j++){
    const mean=train.reduce((s,id)=>s+features.get(id)[j],0)/train.length;
    mu.push(mean);
    sigma.push(Math.sqrt(train.reduce((s,id)=>s+(features.get(id)[j]-mean)**2,0)
      /train.length)||1);
  }
  const vec=new Map([...train,...test].map(id=>[id,
    features.get(id).map((x,j)=>Math.max(-10,Math.min(10,(x-mu[j])/sigma[j])))]));
  const sbs=chosen(train);
  for(const id of test){
    measure("SBS",id,sbs,false);
    measure("VBS_oracle",id,chosen([id]),false);
    const testVector=vec.get(id);
    const neighbors=train.map(i=>{
      const point=vec.get(i);
      let sum=0;
      for(let j=0;j<37;j++)sum+=(testVector[j]-point[j])**2;
      let small=0;
      for(let j=0;j<8;j++)small+=(testVector[j]-point[j])**2;
      return {id:i,dist:sum,dist8:small};
    });
    const ranked=neighbors.slice().sort((a,b)=>a.dist-b.dist||
      (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
    const ranked8=neighbors.slice().sort((a,b)=>a.dist8-b.dist8||
      (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
    for(const k of [5,15])
      measure("KNN"+k,id,chosen(ranked.slice(0,k).map(x=>x.id)),true);

  }
}
const python=JSON.parse(fs.readFileSync(resultPath,"utf8"));
const check={};
for(const [method,record] of Object.entries(summary)){
  const expected=python.scores[method];
  if(!expected)throw Error("missing python result "+method);
  const mean=record.sum/record.n;
  if (record.n!==630 || record.solved!==expected.solved ||
      Math.abs(mean-expected.mean_PAR10_plus_features)>0.00001)
    throw Error(method+" independent crosscheck failure: "+JSON.stringify({
      independent_mean:mean,python_mean:expected.mean_PAR10_plus_features,
      independent_solved:record.solved,python_solved:expected.solved}));
  check[method]={mean:Math.round(mean*1e6)/1e6,solved:record.solved};
}
console.log("ASLIB_WPMS_INDEPENDENT_JS_CROSSCHECK "+JSON.stringify({
  verified_methods:check,scenario_commit:python.source_commit,
  result:"AGREES_WITH_PYTHON_WITHIN_1E-5"
}));
