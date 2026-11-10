/* CF-SPIDER-001: deterministic read-only action graph. No external actions or uploads. */
(function(root,factory){
  "use strict";
  const api=factory();
  if(typeof module==="object"&&module.exports)module.exports=api;
  if(root)root.CFSpiderCore=api;
})(typeof globalThis==="object"?globalThis:this,function(){
  "use strict";
  const SCHEMA="cf0.spider.core.v1";
  const ZONES=["now","soon","ready","conditional","optional","waiting","assistant"];
  const ORDER={now:0,soon:1,ready:2,conditional:3,optional:4,waiting:5,assistant:6};
  const val=(x,n)=>typeof x==="string"?x.trim().slice(0,n):"";
  const unique=a=>[...new Set(a)].sort();
  function safeUrl(x){
    if(typeof x!=="string"||x.length>2048||/[\s\\]/.test(x))return false;
    const m=/^https:\/\/([^/?#]+)(?:[/?#]|$)/i.exec(x);
    return !!m&&!m[1].includes("@")&&/^[a-z0-9][a-z0-9.:-]*$/i.test(m[1])&&!m[1].includes("..");
  }
  function snapshotAge(asOf, today){
    if(!/^\d{4}-\d{2}-\d{2}$/.test(asOf||""))return "unknown";
    const current=today||new Date().toISOString().slice(0,10);
    if(!/^\d{4}-\d{2}-\d{2}$/.test(current))return "unknown";
    const start=Date.parse(asOf+"T00:00:00Z"),end=Date.parse(current+"T00:00:00Z");
    if(!Number.isFinite(start)||!Number.isFinite(end))return "unknown";
    const days=Math.round((end-start)/86400000);
    return days<0?"future_conflict":days>7?"stale":"dated_snapshot";
  }
  function dueState(dueDate,today){
    if(!dueDate)return "not_provided";
    if(!/^\d{4}-\d{2}-\d{2}$/.test(dueDate))return "invalid";
    const current=today||new Date().toISOString().slice(0,10);
    return current>dueDate?"overdue":current===dueDate?"due_today":"upcoming";
  }
  function safePrivateRef(x){
    return typeof x==="string" &&
      /^indexed-chat:sha256:[a-f0-9]{64}:[A-Za-z0-9_.:-]{1,100}:[A-Za-z0-9_.:-]{1,100}$/.test(x);
  }
  function normalizeAction(a,origin){
    const local=origin==="owner_local";
    if(!a||typeof a!=="object"||!(local?/^LOCAL-[A-Za-z0-9_-]{1,40}$/:/^CF-ACT-\d{3}$/).test(a.id))throw Error("Invalid action ID");
    const hasUrl=safeUrl(a.link),hasSource=safeUrl(a.source);
    const source_ref=local&&safePrivateRef(a.source_ref)?a.source_ref:"";
    if((a.link&&!hasUrl)||(a.source&&!hasSource)||
       (!source_ref&&(!hasUrl||!hasSource))||
       (local&&a.source_ref&&!source_ref)||
       !ZONES.includes(a.zone)||!["owner","assistant"].includes(a.owner)||
       !val(a.title,160)||!val(a.action,750))throw Error("Invalid action fields");
    const sources=local&&Array.isArray(a.source_refs)?a.source_refs:[];
    if(sources.length>32||sources.some(ref=>!safePrivateRef(ref))||
       (source_ref&&sources.length&&!sources.includes(source_ref)))throw Error("Invalid private source references");
    const project_id=val(a.project_id,64)||"UNRESOLVED";
    if(!/^[A-Z][A-Z0-9-]{1,60}$/.test(project_id))throw Error("Invalid project ID");
    const task_ids=Array.isArray(a.task_ids)?unique(a.task_ids):[];
    if(task_ids.some(id=>!/^CF-\d{3}$/.test(id)))throw Error("Unverified task ID format");
    const due_date=val(a.due_date,10);
    if(dueState(due_date)==="invalid")throw Error("Invalid due date");
    const equivalence_key=val(a.equivalence_key,120);
    if(equivalence_key&&!/^[A-Za-z0-9_.:-]{1,120}$/.test(equivalence_key))throw Error("Invalid equivalence key");
    return {id:a.id,view_ids:[a.id],origin:local?"owner_local":"public_snapshot",
      zone:a.zone,owner:a.owner,priority:val(a.priority,70),title:val(a.title,160),
      detail:val(a.detail,750),action:val(a.action,750),link:a.link,label:val(a.label,160),
      source:hasSource?a.source:"",source_ref,source_refs:unique(source_ref?[source_ref,...sources]:[]),
      evidence_urls:hasSource?[a.source]:[],proof:val(a.proof,750),caution:val(a.caution,750),
      review_required:local&&a.review_required===true, evidence_role:local?val(a.evidence_role,40):"",
      project_id,task_ids,equivalence_key,due_date,due_state:dueState(due_date),conflict:false,conflict_details:[],
      evidence_level:local?"owner_imported_unverified":"public_source_snapshot"};
  }
  function coalesce(records){
    if(!Array.isArray(records)||records.length>200)throw Error("Action batch too large");
    const groups=new Map(),ids=new Map();
    for(const item of records){
      const a=item&&item.evidence_urls?item:normalizeAction(item,"public_snapshot");
      if(ids.has(a.id)){
        const p=ids.get(a.id);
        if(p.project_id!==a.project_id||p.action!==a.action||p.zone!==a.zone)throw Error("Conflicting action ID: "+a.id);
      }
      ids.set(a.id,a);
      const key=a.project_id+(a.equivalence_key?"|eq:"+a.equivalence_key:"|id:"+a.id);
      if(!groups.has(key)){groups.set(key,{...a,view_ids:[...a.view_ids],evidence_urls:[...a.evidence_urls],source_refs:[...a.source_refs],task_ids:[...a.task_ids],conflict_details:[]});continue;}
      const b=groups.get(key);
      b.view_ids=unique(b.view_ids.concat(a.view_ids));
      b.evidence_urls=unique(b.evidence_urls.concat(a.evidence_urls));
      b.source_refs=unique(b.source_refs.concat(a.source_refs));
      b.task_ids=unique(b.task_ids.concat(a.task_ids));
      if(b.zone!==a.zone||b.owner!==a.owner||b.action!==a.action||b.proof!==a.proof){
        b.conflict=true;b.conflict_details.push("Contradictory action/owner/status/proof at "+a.id);
      }
    }
    return [...groups.values()].sort((a,b)=>ORDER[a.zone]-ORDER[b.zone]||a.id.localeCompare(b.id));
  }
  function connect(records,graph,registry){
    const projects=new Map(graph&&graph.schema==="cf0.public_topic_graph.v1"&&Array.isArray(graph.nodes)?graph.nodes.map(x=>[x.id,x]):[]);
    const tasks=new Map(registry&&registry.schema==="CF200.1"&&Array.isArray(registry.tasks)?registry.tasks.map(x=>[x.id,x]):[]);
    const edges=[],missing=[];
    const actions=coalesce(records).map(a=>{
      const p=projects.get(a.project_id);
      if(!p)missing.push({action:a.id,missing_project:a.project_id});
      else {
        edges.push({from:a.id,to:p.id,kind:"belongs_to",evidence:a.source});
        if(p.parent)edges.push({from:p.id,to:p.parent,kind:"parent",evidence:p.source});
      }
      const work_orders=a.task_ids.map(id=>{
        const t=tasks.get(id);
        if(!t){missing.push({action:a.id,missing_work_order:id});return {id,status:"unverified_reference"};}
        edges.push({from:a.id,to:id,kind:"canonical_work_order",evidence:a.source});
        return {id,title:t.title,status:t.status,evidence:t.evidence||""};
      });
      return {...a,project_title:p?p.title:"Project not resolved",project_source:p?p.source:"",
        project_parent:p?p.parent:null,related_project_ids:p&&Array.isArray(p.related)?p.related:[],
        project_checked:!!p,work_orders};
    });
    return {schema:SCHEMA,actions,edges,missing,provenance:{public_graph:projects.size>0,
      cf200_registry:tasks.size>0,remote_conversation_access:false,completion_mutations:false,private_upload:false}};
  }
  function validateManifest(data){
    if(!data||data.schema!=="cf0.spider.action_manifest.v1"||!Array.isArray(data.actions)||
       data.actions.length<1||data.actions.length>100)throw Error("Requires private action manifest v1, 1–100 items");
    const ids=new Set();return data.actions.map(a=>{
      const row=normalizeAction(a,"owner_local");
      if(ids.has(row.id))throw Error("Duplicate imported ID");
      ids.add(row.id);return row;
    });
  }
  function selectLane(actions,lane,checks,query){
    const zones={mine:["now","soon","ready"],later:["conditional","optional"],waiting:["waiting"],
      assistant:["assistant"],all:ZONES,done:[]}[lane]||[];
    const q=val(query,100).toLowerCase();
    return actions.filter(a=>(lane==="done"?!!checks[a.id]:zones.includes(a.zone)&&(lane!=="mine"||!checks[a.id]))&&
      (!q||[a.id,a.title,a.action,a.project_id,a.project_title].some(s=>String(s||"").toLowerCase().includes(q))));
  }
  return Object.freeze({SCHEMA,normalizeAction,coalesce,connect,validateManifest,selectLane,safeUrl,safePrivateRef,snapshotAge,dueState});
});
