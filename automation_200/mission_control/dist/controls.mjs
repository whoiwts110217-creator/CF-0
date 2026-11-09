// Public-safe source inventory for CF-0 Mission Control.
// These are CONTROLS TO DISPLAY, not enabled remote commands or proof of live execution.
export const SOURCE_DATE = "2026-11-09";
const gh = "https://github.com/whoiwts110217-creator/CF-0";
export const SOURCES = Object.freeze({
  github: Object.freeze([
    {id:"ai-tracker-monitor",title:"AI Tracker public response monitor",detail:"Scheduled every six hours (source cron: 17 */6 * * *)",research:true},
    {id:"cf0-abund-daily",title:"Abund.ai daily discussions",detail:"Five scheduled daily slots in workflow source",research:true},
    {id:"cf0-abund-discovery",title:"Abund.ai task discovery",detail:"Scheduled every six hours (source cron: 41 */6 * * *)",research:true},
    {id:"cf0-channel-watchdog",title:"CF-0 channel evidence watchdog",detail:"Scheduled every five minutes; operational health, not a research brief",research:false},
    {id:"cf0-release-gate",title:"CF-0 release gate",detail:"Daily scheduled release/readiness test",research:false}
  ]),
  windows: Object.freeze([
    {id:"CavemanFocusCF0FastLane",title:"CF-0 Fast Lane",detail:"Owner-local 30-second poller; actual Windows status not connected",research:false},
    {id:"CavemanFocusCF0Relay",title:"CF-0 Relay",detail:"Owner-local 5-minute scheduled relay; actual Windows status not connected",research:false},
    {id:"CavemanFocusHPBridge",title:"CF-0 HP Bridge",detail:"Separate optional owner-local worker; current installation/status not verified",research:false}
  ]),
  continuation: Object.freeze([
    {id:"auto08",title:"AUTO-08 conversation continuation",detail:"Keyboard-only, single-tab runner in source; no signed-in executor connected to this dashboard",research:false}
  ])
});
export const GITHUB_BASE = gh;
export const CHATGPT_PLACEHOLDER_COUNT = 10; // Only count is public; titles remain private until local import.
export const inventoryStatus = item => item.source === "chatgpt"
  ? (item.reportedEnabled === true ? "Last reported enabled" : item.reportedEnabled === false ? "Last reported paused" : "State unknown")
  : item.source === "github" ? "Schedule in source; runtime unknown" : "Local state unverified";

export function records(privateAutomations = null) {
  const slots = privateAutomations === null
    ? Array.from({length:CHATGPT_PLACEHOLDER_COUNT},(_,index)=>({
       id:"slot-"+(index+1), title:"Private automation "+String(index+1).padStart(2,"0"),
       detail:"Import private task inventory locally to identify this slot.", source:"chatgpt", research:false
      }))
    : privateAutomations.map((entry,index)=>({
       ...entry, id:"task-"+index, source:"chatgpt",
       detail:"Last reported state from user-selected private file; not a live connection."
      }));
  return [
    ...slots,
    ...SOURCES.github.map(x=>({...x,source:"github",url:gh+"/actions/workflows/"+x.id+".yml"})),
    ...SOURCES.windows.map(x=>({...x,source:"windows",url:gh+"/blob/main/relay/URGENT_STOP_AND_RESUME.md"})),
    ...SOURCES.continuation.map(x=>({...x,source:"continuation",url:gh+"/tree/main/automation_200/continuation_keyboard"}))
  ];
}

export function parsePrivateInventory(input) {
  if (!input || input.schema !== "cf0.private_automation_inventory.v1"
      || !Array.isArray(input.automations) || input.automations.length > 50) {
    throw new Error("Expected cf0.private_automation_inventory.v1 with up to 50 automations.");
  }
  const seen=new Set();
  return input.automations.map((a,i)=>{
    if (!a || typeof a.title!=="string" || !a.title.trim() || a.title.length > 140
        || typeof a.is_enabled!=="boolean" || typeof a.id!=="string" || a.id.length>140
        || seen.has(a.id)) throw new Error("Invalid or duplicate private automation row "+(i+1));
    seen.add(a.id);
    return {title:a.title.trim(), reportedEnabled:a.is_enabled,
      // Do not expose task ids, prompts, environments, or URLs in rendered HTML.
      research:typeof a.research==="boolean" ? a.research : false};
  });
}

export function shutdownPlan(rows, selected) {
  if (!Array.isArray(rows) || !(selected instanceof Set)) throw new Error("Invalid stage selection.");
  const valid=rows.filter(x=>selected.has(x.source+":"+x.id));
  const lines=[
    "CF-0 AUTO RESEARCH SHUTDOWN — DRAFT ONLY",
    "No automations were paused, cancelled, or disabled by Mission Control.",
    "Operator must verify live task identities and status before any real action.",
    ""
  ];
  if (!valid.length) lines.push("No tasks staged.");
  for (const row of valid) {
    lines.push("STAGE FOR REVIEW ["+row.source.toUpperCase()+"] "+row.title+
      " — "+inventoryStatus(row));
  }
  lines.push("PRESERVE: private archives, ledger, code, GitHub history, receipts and grant monitoring unless explicitly selected.");
  return lines.join("\n");
}
