function run() {
  const start = Date.now();
  const pairs = n => Array.from({length:n},(_,a)=>Array.from({length:n-a-1},(_,i)=>[a,a+i+1])).flat();
  const forced = t => pairs(t.length).filter(([a,b])=>t[a]===t[b] || (t[a]===b && t[b]===a) || (t[a]===a && t[b]===b)).map(([a,b])=>[a,b,1]);
  function prefix(t,a) {
    const p=[a];
    for (let i=0;i<4;i++) p.push(t[p[i]]);
    return p;
  }
  function events(x,y) {
    return x.slice(0,4).flatMap((a,i)=>a===y[i]?[]:[[a,y[i],0]]);
  }
  function color(n, edges, pins = []) {
    const adj=Array.from({length:n},()=>[]), component=Array(n).fill(-1), c=Array(n).fill(0);
    for (const [u,v,p] of edges) { adj[u].push([v,p]); adj[v].push([u,p]); }
    // Resolve pinned components first to prevent arbitrary root colors from conflicting.
    for (const [root, value] of [...pins,...Array.from({length:n},(_,i)=>[i,0])]) {
      if (component[root] !== -1) continue;
      component[root]=root;
      c[root]=value;
      const todo=[root];
      while (todo.length) {
        const u=todo.pop();
        for (const [v,p] of adj[u]) {
          const want=c[u]^p;
          if (component[v]===-1) { component[v]=root; c[v]=want; todo.push(v); }
          else if (c[v]!==want) return null;
        }
      }
    }
    return pins.every(([v,b])=>c[v]===b)?component:null;
  }
  const ok=(s,[a,b,p])=>(((s>>a)^(s>>b))&1)===p;
  const allColors=(n,e)=>Array.from({length:1<<n},(_,i)=>i).filter(s=>e.every(row=>ok(s,row)));
  const leave=(e,i)=>e.filter((_,j)=>i!==j);
  const core=(e,sat)=>!sat(e)&&e.every((_,i)=>sat(leave(e,i)));
  function guard(t,cycle,p,l) {
    const a=prefix(t,p[0]),b=prefix(t,p[1]);
    const edges=[...forced(t),...events(a,b).slice(0,l)];
    const oracle=new Set(allColors(t.length,edges).map(s=>cycle.reduce((v,x,i)=>v+(((s>>x)&1)<<i),0)));
    const got=new Set(Array.from({length:1<<cycle.length},(_,i)=>i).filter(s=>color(t.length,edges,cycle.map((v,i)=>[v,(s>>i)&1]))!==null));
    if (got.size!==oracle.size || [...got].some(s=>!oracle.has(s))) throw Error("shadow mismatch");
  }
  guard([0,0,3,4,2],[2,3,4],[0,1],2);
  for(let k=0;k<4;k++) for(let l=2;l<=4;l++) guard([1,2,3,0,k],[0,1,2,3],[0,4],l);
  const adverse=[1,2,3,0,0], ae=events(prefix(adverse,0),prefix(adverse,4));
  const ff=forced(adverse);
  if(!core(ae,q=>allColors(5,[...ff,...q]).length!==0)) throw Error("negative control");
  const bases=[[1,2,3,4,0,6,7,8,9,15,11,12,13,14,15],[1,2,3,0,5,6,7,8,14,10,11,12,13,14,0]];
  const results=bases.map(base=>{
    let maps=0, tested=0, cores=0, privateFailures=0, disagreements=0, fixedMs=0, oracleMs=0;
    for(const a of [1,2,15,16]) for(const b of [1,2,15,16]) {
      const t=[...base,a,b], f=forced(t), q=color(17,f);
      if(!q) continue;
      maps++;
      const prefixes=t.map((_,i)=>prefix(t,i));
      const cohort=pairs(17).map(([a,b])=>[prefixes[a],prefixes[b]])
        .filter(([x,y])=>new Set([...x,...y]).size===10 && t[x[4]]===t[y[4]]);
      if (!cohort.length) continue;
      let tick=Date.now();
      const possible=allColors(17,f);
      oracleMs+=Date.now()-tick;
      for(const [x,y] of cohort) {
        tested++;
        const e=events(x,y), seq=[x.slice(0,4).map(u=>q[u]),y.slice(0,4).map(v=>q[v])];
        if(!seq.some((side,i)=>new Set(side).size===4 && side.every(u=>!seq[1-i].includes(u)))) privateFailures++;
        tick=Date.now();
        const baseline=core(e,f2=>color(17,[...f,...f2])!==null);
        fixedMs+=Date.now()-tick; tick=Date.now();
        const ref=core(e,f2=>possible.some(c=>f2.every(row=>ok(c,row))));
        oracleMs+=Date.now()-tick;
        cores+=Number(ref);
        disagreements+=Number(ref!==baseline);
      }
    }
    if(!tested) throw Error("empty cohort");
    return {maps,tested,cores,privateFailures,disagreements,fixedMs,oracleMs};
  });
  return {results,guards:13,elapsedMs:Date.now()-start};
}
console.log(JSON.stringify(run(),null,2));
