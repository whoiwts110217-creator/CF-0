// Public-safe source inventory for CF-0 Mission Control.
// These are CONTROLS TO DISPLAY, not enabled remote commands or proof of live execution.
export const SOURCE_DATE = "2026-11-09";
const gh = "https://github.com/whoiwts110217-creator/CF-0";
export const SOURCES = Object.freeze({
  github: Object.freeze([
    {"id":"auto08-chrome-source","title":"AUTO-08 Chrome extension source tests","trigger":"event","detail":"On extension source push or pull request; tests do not prove live Chrome operation","research":false},
    {"id":"ai-tracker-monitor","title":"AI Tracker response monitor","trigger":"schedule","detail":"Every six hours (17 */6 * * *)","research":true},
    {"id":"cf0-abund-daily","title":"Abund.ai daily discussions","trigger":"schedule","detail":"Five daily cron slots","research":true},
    {"id":"cf0-abund-discovery","title":"Abund.ai task discovery","trigger":"schedule","detail":"Every six hours (41 */6 * * *)","research":true},
    {"id":"cf0-channel-watchdog","title":"CF-0 channel evidence watchdog","trigger":"schedule","detail":"Every five minutes (*/5 * * * *), health only","research":false},
    {"id":"cf0-release-gate","title":"CF-0 release/readiness gate","trigger":"schedule","detail":"Daily (17 9 * * *), validation only","research":false},
    {"id":"agent-native-outreach-round-2","title":"Agent outreach round 2","trigger":"event","detail":"On matching source push or manual dispatch","research":true},
    {"id":"bridge-tests","title":"Bridge regression tests","trigger":"event","detail":"On matching source push or manual dispatch","research":false},
    {"id":"cf0-hp-control-windows-probe","title":"HP control Windows source probe","trigger":"event","detail":"Source-only Windows probe workflow; does not establish owner HP deployment or control","research":false},
    {"id":"cf0-relay-tests","title":"Public relay Windows tests","trigger":"event","detail":"On source push, pull request or manual dispatch","research":false},
    {"id":"clarity-check-guards","title":"$5 Clarity Check offer safeguards","trigger":"event","detail":"Source-only tests for public buyer intake, no-prepayment warnings and preservation of the free Clarity Card; not live orders or revenue","research":false},
    {"id":"dashboard-guard","title":"Dashboard regression guard","trigger":"event","detail":"On matching source push, pull request or manual dispatch","research":false},
    {"id":"dreamkiller-browser-smoke","title":"Dreamkiller browser smoke test","trigger":"event","detail":"On source push, pull request or manual dispatch","research":false},
    {"id":"dreamkiller-chapter01","title":"Dreamkiller chapter 01","trigger":"event","detail":"On matching source push or manual dispatch","research":false},
    {"id":"dreamkiller-v02-browser","title":"Dreamkiller v0.2 browser tests","trigger":"event","detail":"On matching source push or manual dispatch","research":false},
    {"id":"dreamkiller-v02","title":"Dreamkiller v0.2 build tests","trigger":"event","detail":"On matching source push or manual dispatch","research":false},
    {"id":"cf0-skill-evolution-ci","title":"CF0 Skill Evolution Offline Tests","trigger":"event","detail":"On matching pull requests or manual dispatch; offline evidence-gate tests, not an autonomous agent","research":false},
    {"id":"iphone-skill-foundry-browser-smoke","title":"Skill Foundry Browser Smoke Tests","trigger":"event","detail":"On matching pull requests or manual dispatch; synthetic Chromium/WebKit tests, not a deployed iPhone app","research":false},
    {"id":"iphone-skill-foundry-ci","title":"Skill Foundry iPhone checks","trigger":"event","detail":"On matching pull requests or manual dispatch; local-only package tests, not an installed iPhone app","research":false},
    {"id":"mission-control-access-tests","title":"Mission Control access visibility tests","trigger":"event","detail":"On source push or pull request","research":false},
    {"id":"one-time-agent-invitations","title":"One-time agent invitations","trigger":"event","detail":"On matching source push or manual dispatch","research":true},
    {"id":"prompt-efficiency-guard","title":"Prompt efficiency guard","trigger":"event","detail":"On source push or manual dispatch","research":false},
    {"id":"publish-website","title":"Publish Caveman Focus website","trigger":"event","detail":"On source push or manual dispatch","research":false},
    {"id":"retry-agent-message-directory","title":"Retry agent message directory","trigger":"event","detail":"On matching source push or manual dispatch","research":true},
    {"id":"verify-public-agent-invites","title":"Verify public agent invitations","trigger":"event","detail":"On matching source push or manual dispatch","research":true}
  ]),
  windows: Object.freeze([
    {id:"CavemanFocusCF0FastLane",title:"CF-0 Fast Lane",detail:"Owner-local 30-second poller; actual Windows status not connected",research:false},
    {id:"CavemanFocusCF0Relay",title:"CF-0 Relay",detail:"Owner-local 5-minute scheduled relay; actual Windows status not connected",research:false},
    {id:"CavemanFocusHPBridge",title:"CF-0 HP Bridge",detail:"Separate optional owner-local worker; current installation/status not verified",research:false}
  ]),
  continuation: Object.freeze([
    {id:"auto08",title:"AUTO-08 conversation continuation",detail:"Owner-local Chrome extension can check and attach to exactly one existing ChatGPT tab without new tabs or mouse controls. Requires installation and a live smoke test.",research:false}
  ])
});
export const GITHUB_BASE = gh;
export const CHATGPT_PLACEHOLDER_COUNT = 11; // Only count is public; titles remain private until local import.
export const inventoryStatus = item => item.source === "chatgpt"
  ? (item.reportedEnabled === true ? "Last reported enabled" : item.reportedEnabled === false ? "Last reported not enabled (pause/completion not distinguished)" : "State unknown")
  : item.source === "github" ? (item.trigger === "schedule" ? "Scheduled in source; live state unknown" : "Event/manual trigger in source; live state unknown") : "Local state unverified";

export function records(privateAutomations = null) {
  const slots = privateAutomations === null
    ? Array.from({length:CHATGPT_PLACEHOLDER_COUNT},(_,index)=>({
       id:"slot-"+(index+1), title:"Private automation "+String(index+1).padStart(2,"0"),
       detail:"Import private task inventory locally to identify this slot.", source:"chatgpt", research:false
      }))
    : privateAutomations.map((entry,index)=>({
       ...entry, id:"task-"+index, source:"chatgpt",
       detail:"Owner-supplied snapshot"+(entry.observedAt ? " observed "+entry.observedAt : " (date unknown)")+"; not an authenticated live connection."
      }));
  return [
    ...slots,
    ...SOURCES.github.map(x=>({...x,source:"github",url:gh+"/actions/workflows/"+x.id+".yml"})),
    ...SOURCES.windows.map(x=>({...x,source:"windows",url:gh+"/blob/main/relay/URGENT_STOP_AND_RESUME.md"})),
    ...SOURCES.continuation.map(x=>({...x,source:"continuation",url:gh+"/tree/main/automation_200/continuation_chrome"}))
  ];
}

export function parsePrivateInventory(input) {
  if (!input || input.schema !== "cf0.private_automation_inventory.v1"
      || !Array.isArray(input.automations) || input.automations.length > 50) {
    throw new Error("Expected cf0.private_automation_inventory.v1 with up to 50 automations.");
  }
  // A timestamp makes an owner-selected snapshot auditable, but cannot authenticate its origin.
  const observedAt=input.observed_at;
  if (observedAt !== undefined && (typeof observedAt!=="string"
      || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(observedAt)
      || !Number.isFinite(Date.parse(observedAt)))) throw new Error("Invalid snapshot observed_at.");
  const seen=new Set();
  return input.automations.map((a,i)=>{
    if (!a || typeof a.title!=="string" || !a.title.trim() || a.title.length > 140
        || typeof a.is_enabled!=="boolean" || typeof a.id!=="string" || a.id.length>140
        || seen.has(a.id)) throw new Error("Invalid or duplicate private automation row "+(i+1));
    seen.add(a.id);
    return {title:a.title.trim(), reportedEnabled:a.is_enabled,
      // Do not expose task ids, prompts, environments, or URLs in rendered HTML.
      research:typeof a.research==="boolean" ? a.research : false, observedAt:observedAt||null};
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
