let S={},TOKEN="",view="mission";
const $=q=>document.querySelector(q), esc=x=>String(x??"—").replace(/[&<>]/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[m]));
const card=(title,body,cls="")=>'<article class="card '+cls+'"><h3>'+esc(title)+'</h3>'+body+'</article>';
const pill=(x,c="")=>'<span class="pill '+c+'">'+esc(x)+'</span>';
function summary(){
 const g=S.git?.summary||{}, w=S.weaknesses||[], caps=S.capabilities||{}, f=S.fleet_truth?.nodes||[];
 return '<div class="grid">'+
 card("Mission",'<div class="metric">'+esc(S.hyperloop?.status||"ACTIVE")+'</div><p class="muted">Observe → Residual → Verify → Improve → Repeat</p>')+card("Acceleration",'<div class="metric">'+esc(S.acceleration_score??0)+'/100</div><p class="muted">Verified-progress adaptive score · event L'+esc(S.event_engine?.acceleration_level??0)+' · poll '+esc(S.event_engine?.poll_seconds??"—")+'s</p>')+
 card("Git",'<div class="metric">'+Object.values(g).reduce((a,b)=>a+(+b||0),0)+'</div><p class="muted">'+Object.entries(g).map(([k,v])=>k+":"+v).join(" · ")+'</p>')+
 card("Residual Pressure",'<div class="metric">'+esc(S.hyperloop?.residual_pressure??S.weaknesses?.[0]?.priority??0)+'</div><p>'+w.slice(0,3).map(x=>pill(x.kind,"warn")).join("")+'</p>')+
 card("Fleet",'<div class="metric">'+esc(f.length||3)+'/3</div><p class="muted">WorkerTruth / Reality federation</p>')+
 card("Semantic Live Feed",(S.feed||[]).slice().reverse().map(x=>'<div class="feed-item"><time>'+new Date((x.ts||0)*1000).toLocaleTimeString()+'</time>'+esc(x.node||S.role)+' · '+esc(x.worker||"")+' · '+esc(JSON.stringify(x.git||{}))+'</div>').join("")||'<span class="muted">No deltas yet</span>',"wide feed")+
 card("Capabilities",Object.entries(caps).slice(0,10).map(([k,v])=>pill(k+": "+(typeof v==="object"?JSON.stringify(v):v))).join(""),"");
}
function reality(){
 return '<div class="grid">'+card("Reality State",'<pre>'+esc(JSON.stringify({system:S.system,hyperloop:S.hyperloop,legacy:S.legacy_cockpit},null,2))+'</pre>',"wide")+
 card("Node",'<div class="metric">'+esc(S.role)+'</div><p>'+pill(S.node)+'</p>')+
 card("Semantic Feed",'<div class="feed">'+(S.feed||[]).slice().reverse().map(x=>'<div class="feed-item">'+esc(JSON.stringify(x))+'</div>').join("")+'</div>',"full")+'</div>';
}
function caps(){return '<div class="grid">'+card("Capability Graph",'<pre>'+esc(JSON.stringify(S.capabilities||{},null,2))+'</pre>',"wide")+
 card("Actions",pill("git_sync")+pill("morph_refresh")+pill("workertruth_refresh"))+'</div>'}
function residuals(){let w=S.weaknesses||[];return '<div class="grid">'+card("Weakness Atlas",'<table><tr><th>Residual</th><th>Priority</th><th>Route</th></tr>'+w.map(x=>'<tr><td>'+esc(x.kind)+'</td><td>'+esc(x.priority)+'</td><td>'+esc(x.route)+'</td></tr>').join("")+'</table>',"full")+'</div>'}
function evidence(){return '<div class="grid">'+card("WorkerTruth",'<pre>'+esc(JSON.stringify(S.worker_truth||{},null,2))+'</pre>',"wide")+card("Fleet Truth",'<pre>'+esc(JSON.stringify(S.fleet_truth||{},null,2))+'</pre>',"full")+'</div>'}
function git(){let g=S.git||{};return '<div class="grid">'+card("Git Summary",'<div class="metric">'+esc(Object.values(g.summary||{}).reduce((a,b)=>a+(+b||0),0))+'</div><p>'+Object.entries(g.summary||{}).map(([k,v])=>pill(k+": "+v,k.startsWith("HOLD")?"warn":"")).join("")+'</p>')+card("Git State",'<pre>'+esc(JSON.stringify(g,null,2))+'</pre>',"wide")+'</div>'}
function evolution(){let f=S.fleet_projection||[],r=S.reports||{},w=S.weaknesses||[];return '<div class="grid">'+card("Acceleration",'<div class="metric">'+esc(S.acceleration_score??0)+'/100</div><p class="muted">Adaptive verified-progress score</p>')+card("Fleet Projection",'<table><tr><th>Role</th><th>Node</th><th>Result</th></tr>'+f.map(x=>'<tr><td>'+esc(x.role)+'</td><td>'+esc(x.node)+'</td><td>'+esc(x.result)+'</td></tr>').join("")+'</table>',"wide")+card("Mutable Reports",Object.entries(r).map(([k,v])=>pill(k+": "+Math.round((v.bytes||0)/1024)+" KB")).join(""))+card("Residual Frontier",w.slice(0,8).map(x=>pill(x.kind+" · "+x.priority,"warn")).join(""),"wide")+
card("Event Morphogenesis",'<pre>'+esc(JSON.stringify(S.event_engine||{},null,2))+'</pre>',"full")+card("GO Σ∞ Constitution",'<div class="metric">'+esc(S.go_sigma?.mission_id||"—")+'</div><p>'+(S.go_sigma?.modes||[]).map(x=>pill(x)).join("")+'</p><pre>'+esc((S.go_sigma?.invariants||[]).join("\n"))+'</pre>',"full")+'</div>'}
function nodes(){let n=S.fleet_truth?.nodes||[];return '<div class="grid">'+card("Fleet Nodes",'<table><tr><th>Node</th><th>Input</th><th>Result</th></tr>'+n.map(x=>'<tr><td>'+esc(x.nodeID)+'</td><td>'+esc((x.inputHash||"").slice(0,10))+'</td><td>'+esc((x.resultHash||"").slice(0,10))+'</td></tr>').join("")+'</table>',"full")+'</div>'}
function render(){
 $("#role").textContent=(S.role||"TRISTAN")+" · "+(S.node||"");
 $("#node").textContent=S.node||"—";$("#memory").textContent=(S.system?.memory?.load_pct??"—")+"%";
 const g=S.system?.gpu;$("#gpu").textContent=g?(g.util_pct+"% · "+g.temp_c+"°C"):"N/A";
 $("#worker").textContent=S.worker_truth?.verifierResult||"UNKNOWN";
 $("#title").textContent=view[0].toUpperCase()+view.slice(1);
 const map={mission:summary,reality,capabilities:caps,residuals,evidence,git,nodes,evolution};$("#content").innerHTML=(map[view]||summary)();
}
async function refresh(){try{S=await fetch("/api/state",{cache:"no-store"}).then(r=>r.json());render();$("#health").textContent="LIVE"}catch(e){$("#health").textContent="DEGRADED"}}
async function action(a){if(!TOKEN)TOKEN=(await fetch("/api/token").then(r=>r.json())).token;await fetch("/api/action",{method:"POST",headers:{"Content-Type":"application/json","X-Tristan-Token":TOKEN},body:JSON.stringify({action:a})});setTimeout(refresh,900)}
document.querySelectorAll(".nav").forEach(b=>b.onclick=()=>{document.querySelectorAll(".nav").forEach(x=>x.classList.remove("active"));b.classList.add("active");view=b.dataset.view;render()});
document.querySelectorAll("[data-action]").forEach(b=>b.onclick=()=>action(b.dataset.action));
setInterval(()=>$("#clock").textContent=new Date().toLocaleString(),1000);setInterval(refresh,2000);refresh();