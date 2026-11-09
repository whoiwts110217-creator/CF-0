import {records,parsePrivateInventory,inventoryStatus,shutdownPlan,CHATGPT_PLACEHOLDER_COUNT,SOURCE_DATE} from "./controls.mjs";

const byId=id=>document.getElementById(id);
const groups=[
  ["chatgpt","control-chatgpt"],
  ["github","control-github"],
  ["windows","control-windows"],
  ["continuation","control-continuation"]
];
const staged=new Set();
let privateAutomations=null;
let rows=[];

function element(tag,className,text) {
  const node=document.createElement(tag);
  if(className) node.className=className;
  if(text!==undefined) node.textContent=text;
  return node;
}

function disabledAction(text,label) {
  const button=element("button","control-action",text);
  button.type="button";
  button.disabled=true;
  button.title=label+" — no authenticated executor connected; display only.";
  button.setAttribute("aria-label",text+" "+label+": unavailable until connected");
  return button;
}

function draw() {
  rows=records(privateAutomations);
  const valid=new Set(rows.map(x=>x.source+":"+x.id));
  for(const key of staged) if(!valid.has(key)) staged.delete(key);
  for(const [name,id] of groups) {
    const container=byId(id);
    const result=rows.filter(x=>x.source===name).map(x=>{
      const row=element("div","control-row");
      const description=element("div","control-description");
      const title=element("strong","control-title",x.title);
      const note=element("small","control-detail",x.detail);
      const status=element("span","badge",inventoryStatus(x));
      status.dataset.tone="muted";
      description.append(title,note,status);
      const actions=element("div","control-row-actions");
      if(x.url) {
        const link=element("a","tiny-link","View source");
        link.href=x.url;
        link.target="_blank";
        link.rel="noopener noreferrer";
        actions.append(link);
      }
      const label=element("label","control-stage");
      const checkbox=document.createElement("input");
      checkbox.type="checkbox";
      checkbox.checked=staged.has(x.source+":"+x.id);
      checkbox.addEventListener("change",()=>{
        const key=x.source+":"+x.id;
        if(checkbox.checked) staged.add(key); else staged.delete(key);
        updatePlan();
      });
      label.append(checkbox,element("span",null,"Stage shutdown"));
      actions.append(label,disabledAction(x.source==="continuation"?"Start":"Pause",x.title),
        disabledAction("Resume",x.title));
      row.append(description,actions);
      return row;
    });
    if (name === "github") {
      const matching=rows.filter(x=>x.source==="github");
      const scheduled=matching.flatMap((x,i)=>x.trigger==="schedule"?[result[i]]:[]);
      const other=matching.flatMap((x,i)=>x.trigger!=="schedule"?[result[i]]:[]);
      const scheduleHead=element("h4","control-subheading","Scheduled ("+scheduled.length+")");
      const scheduleList=element("div","control-rows");
      scheduleList.append(...scheduled);
      const details=element("details","control-optional-group");
      const summary=element("summary",null,"Event-triggered and manual workflows ("+other.length+")");
      const eventList=element("div","control-rows");
      eventList.append(...other);
      details.append(summary,eventList);
      container.replaceChildren(scheduleHead,scheduleList,details);
    } else container.replaceChildren(...result);
  }
  updatePlan();
  byId("control-chatgpt-count").textContent=privateAutomations===null
    ? CHATGPT_PLACEHOLDER_COUNT+" private slots — last count, not a live read"
    : privateAutomations.length+" private tasks in user-selected file";
  byId("control-source-date").textContent="Public source inventory reviewed "+SOURCE_DATE+
    ". No connector is attached to these switches.";
}

function updatePlan(){
  byId("control-stage-status").textContent=staged.size+
    " task(s) staged for a proposed shutdown. Nothing has been disabled.";
  byId("control-plan-preview").textContent=shutdownPlan(rows,staged);
}

async function importPrivate(){
  const file=byId("control-private-file").files?.[0];
  if(!file)return;
  try {
    if(file.size > 65536)throw new Error("Private inventory exceeds 64 KiB.");
    const privateRows=parsePrivateInventory(JSON.parse(await file.text()));
    privateAutomations=privateRows;
    staged.clear();
    draw();
    byId("control-import-status").textContent=
      "Local-only inventory loaded for this page session. No upload, account action or saved browser storage.";
  } catch {
    privateAutomations=null;
    staged.clear();
    draw();
    byId("control-import-status").textContent=
      "Private file rejected. Expected cf0.private_automation_inventory.v1 (id, title, is_enabled, optional research).";
  }
}

byId("control-private-file").addEventListener("change",importPrivate);
byId("control-clear-private").addEventListener("click",()=>{
  privateAutomations=null;staged.clear();byId("control-private-file").value="";
  draw();byId("control-import-status").textContent="Private inventory cleared from memory; no account state changed.";
});
byId("control-stage-research").addEventListener("click",()=>{
  for(const x of rows)if(x.research)staged.add(x.source+":"+x.id);
  draw();
});
byId("control-clear-stage").addEventListener("click",()=>{staged.clear();draw();});
byId("control-copy-stage").addEventListener("click",async()=>{
  const plan=shutdownPlan(rows,staged);
  try{
    if(!navigator.clipboard?.writeText)throw new Error("Clipboard unavailable");
    await navigator.clipboard.writeText(plan);
    byId("control-copy-status").textContent="Draft plan copied. NO schedules or tasks were changed.";
  }catch{
    byId("control-copy-status").textContent="Clipboard unavailable. Select and copy the preview text below.";
  }
});
draw();
