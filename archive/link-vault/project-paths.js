/* CF0 One Compass: purpose filters for the existing Link Vault, not a second dashboard. */
(() => {
"use strict";
const ROUTES=Object.freeze([
{"id":"now","title":"What needs me?","hint":"One action sphere: now, soon, ready, waiting and AI work.","mode":"actions"},
{"id":"spider","title":"Spider & Windows","hint":"Spider source, Windows handoffs and recovery history.","mode":"search","query":"spider"},
{"id":"operations","title":"Automation & control","hint":"Mission Control, CF-200, HP relay and routines.","mode":"category","category":"Automation"},
{"id":"funding","title":"Income & grants","hint":"Clarity offers, support pages, business and grants.","mode":"category","category":"Funding"},
{"id":"history","title":"History & continuity","hint":"Source history, topic graph, backups and recovery gaps.","mode":"category","category":"Continuity"},
{"id":"stories","title":"Stories, games & worlds","hint":"Book Machine, Mushroomhead, SYNAPSE and Dreamkiller.","mode":"category","category":"Creative"},
{"id":"research","title":"Research & invention","hint":"Experiments, concepts and evidence still being tested.","mode":"category","category":"Research"},
{"id":"skills","title":"Apps, tools & skills","hint":"Skill Foundry, EYE/SEE and Skill Screen Learn.","mode":"search","query":"skill"}
]);
const CSS=`
#cf-project-paths{margin:18px 0 26px;padding:17px;border:1px solid #31576c;border-radius:20px;background:linear-gradient(145deg,#0f2333,#081825)}
#cf-project-paths h2{font-size:21px;margin:0 0 4px}
#cf-project-paths .cf-paths-note{font-size:13px;color:#b6ccd9;margin:0 0 14px;max-width:790px}
#cf-project-paths .cf-paths-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
#cf-project-paths .cf-path-button{display:block;width:100%;text-align:left;border:1px solid #335c70;border-radius:12px;padding:13px 12px;background:#102a3b;color:#e9f8fe;min-height:94px}
#cf-project-paths .cf-path-button:hover{border-color:#79e9fa;background:#164058}
#cf-project-paths .cf-path-button:focus-visible{outline:3px solid #ffcd81;outline-offset:3px}
#cf-project-paths .cf-path-button strong{display:block;font-size:14px;line-height:1.3;margin-bottom:5px}
#cf-project-paths .cf-path-button small{display:block;color:#b6d1dd;font-size:12px;line-height:1.35}
#cf-project-paths .cf-paths-status{color:#b3deee;font-size:12px;min-height:16px;margin:12px 0 0}
#cf-project-paths .cf-paths-index{font-size:13px;color:#8fe8ff;font-weight:700}
@media(min-width:740px){#cf-project-paths .cf-paths-grid{grid-template-columns:repeat(4,minmax(0,1fr))}}
@media(max-width:370px){#cf-project-paths .cf-paths-grid{grid-template-columns:1fr}#cf-project-paths .cf-path-button{min-height:68px}}
@media(prefers-reduced-motion:reduce){#cf-project-paths *{scroll-behavior:auto}}
`;
const root=document.getElementById("cf-project-paths");
if(!root)return;
const style=document.createElement("style");style.textContent=CSS;document.head.append(style);
const el=(tag,className,textValue)=>{
 const e=document.createElement(tag);if(className)e.className=className;
 if(textValue!==undefined)e.textContent=textValue;
 return e;
};
function choose(route){
 const search=document.getElementById("q"),chips=document.getElementById("chips");
 const status=document.getElementById("cf-paths-status");
 if(!route||!status)return false;
 if(route.mode==="actions"){
  const sphere=document.getElementById("owner-actions");
  if(!sphere){status.textContent="Action sphere unavailable. See public project index below.";return false;}
  sphere.scrollIntoView({block:"start",behavior:"auto"});
  const first=sphere.querySelector('[data-view="mine"]');
  if(first&&typeof first.focus==="function")first.focus({preventScroll:true});
  status.textContent="Action sphere · owner statuses are dated source snapshots, not live account reports.";
  return true;
 }
 if(!search||!chips){status.textContent="Directory unavailable. Use the public project index.";return false;}
 const category=route.mode==="category"?route.category:"All";
 const selected=[...chips.querySelectorAll("button")].find(x=>x.textContent.trim()===category);
 if(!selected){status.textContent="Category unavailable. Use the public project index.";return false;}
 selected.click();
 search.value=route.mode==="search"?route.query:"";
 search.dispatchEvent(new Event("input",{bubbles:true}));
 search.focus();
 status.textContent=route.title+" → existing public directory below. Private archives stay private.";
 return true;
}
root.replaceChildren();
const header=el("h2",null,"Find your work by purpose");
header.id="cf-paths-title";root.setAttribute("aria-labelledby",header.id);
root.append(header,el("p","cf-paths-note","One CF-0 system, not another task list. Choose a goal to filter the existing directory below."));
const grid=el("div","cf-paths-grid");
for(const route of ROUTES){
 const button=el("button","cf-path-button");button.type="button";button.dataset.path=route.id;
 button.append(el("strong",null,route.title),el("small",null,route.hint));
 button.addEventListener("click",()=>choose(route));
 grid.append(button);
}
root.append(grid);
const status=el("p","cf-paths-status","Select a purpose to browse public routes.");
status.id="cf-paths-status";status.setAttribute("role","status");root.append(status);
const index=el("a","cf-paths-index","All indexed public projects and source caveats ↗");
index.href="https://github.com/whoiwts110217-creator/CF-0/blob/main/docs/PROJECTS.md";
index.rel="noopener noreferrer";index.target="_blank";root.append(index);
document.addEventListener("keydown",event=>{
 if(event.key!=="/"||event.ctrlKey||event.metaKey||event.altKey)return;
 const t=event.target;if(t&&(/INPUT|TEXTAREA|SELECT/.test(t.tagName)||t.isContentEditable))return;
 const q=document.getElementById("q");if(!q)return;
 event.preventDefault();q.focus();
});
window.CFProjectPathways={routeIds:ROUTES.map(r=>r.id),chooseRoute:(id)=>choose(ROUTES.find(r=>r.id===id))};
})();
