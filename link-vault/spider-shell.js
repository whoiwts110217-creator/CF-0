/* CF-SPIDER-001: original lightweight mechanical spider for the EXISTING action Sphere. */
(() => {
  "use strict";
  const sphere=document.querySelector(".oa-sphere");
  const rail=document.getElementById("oa-items");
  if(!sphere||!rail)return;
  const bot=document.createElement("button");
  bot.type="button";bot.className="spider-bot";bot.id="spider-bot";
  bot.setAttribute("aria-label","Robot spider: focus your next evidenced action");
  bot.title="Spider: find my next action";
  bot.innerHTML=[
    '<svg viewBox="0 0 124 108" role="img" aria-label="Eight-legged mechanical spider">',
    '<g class="spider-limbs" fill="none" stroke="#69e0ef" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">',
    '<path class="spider-leg left l1" d="M51 42 32 23 9 20"/>',
    '<path class="spider-leg left l2" d="M47 50 24 43 4 48"/>',
    '<path class="spider-leg left l3" d="M46 61 23 72 5 80"/>',
    '<path class="spider-leg left l4" d="M53 68 38 91 17 99"/>',
    '<path class="spider-leg right r1" d="M73 42 92 23 115 20"/>',
    '<path class="spider-leg right r2" d="M77 50 100 43 120 48"/>',
    '<path class="spider-leg right r3" d="M78 61 101 72 119 80"/>',
    '<path class="spider-leg right r4" d="M71 68 86 91 107 99"/>',
    '</g>',
    '<path d="M62 18 62 9 M56 9 68 9" stroke="#c8f4ff" stroke-width="3" fill="none"/>',
    '<ellipse cx="62" cy="57" rx="21" ry="29" fill="#0c293d" stroke="#8ddfff" stroke-width="3"/>',
    '<path d="M48 38 62 32 76 38 81 60 62 75 43 60Z" fill="#133f55" stroke="#9deefd" stroke-width="2"/>',
    '<path d="M49 44 62 38 75 44M49 65 62 70 75 65" fill="none" stroke="#2b8fa3" stroke-width="2"/>',
    '<circle cx="54" cy="51" r="5" fill="#8cfbff" class="spider-eye"/>',
    '<circle cx="70" cy="51" r="5" fill="#8cfbff" class="spider-eye"/>',
    '<path d="M57 60 62 63 67 60" stroke="#e1faff" stroke-width="2" fill="none"/>',
    '<circle cx="62" cy="17" r="3" fill="#ffd58a" class="spider-signal"/>',
    '</svg>'
  ].join("");
  sphere.append(bot);
  const status=document.createElement("p");
  status.className="spider-status";status.id="spider-status";status.setAttribute("role","status");
  status.textContent="Spider online · public source view, not an account scanner";
  document.querySelector(".oa-system").append(status);
  const xy={mine:[61,54],later:[80,28],waiting:[67,77],assistant:[24,76],all:[34,28],done:[50,50]};
  let active="mine",selected=null;
  function move(lane,id){
    active=xy[lane]?lane:"all";
    const loc=xy[active];bot.style.setProperty("--spider-x",loc[0]+"%");bot.style.setProperty("--spider-y",loc[1]+"%");
    bot.dataset.lane=active;
    if(id)selected=id;
    status.textContent=selected ? "Spider thread → "+selected+" · "+active+" · source-linked view" :
      "Spider perched at "+active+" · select an action to trace its source";
  }
  function select(card){
    if(!card)return;
    for(const c of rail.querySelectorAll(".oa-item"))c.classList.toggle("spider-selected",c===card);
    const id=card.dataset.actionId,zone=card.dataset.zone;
    const lane=zone==="now"||zone==="soon"||zone==="ready"?"mine":
      zone==="conditional"||zone==="optional"?"later":zone==="waiting"?"waiting":"assistant";
    move(lane,id);
    card.scrollIntoView({block:"nearest",behavior:"auto"});
    const summary=card.querySelector("details");
    if(summary)summary.open=true;
  }
  bot.addEventListener("click",()=>{
    const card=rail.querySelector(".oa-item:not([data-done=true])")||rail.querySelector(".oa-item");
    if(card){select(card);const b=card.querySelector(".oa-inspect")||card.querySelector("a");if(b)b.focus()}
    else{status.textContent="No available action in this lane; select All paths";const all=sphere.querySelector('[data-view="all"]');if(all)all.focus()}
  });
  rail.addEventListener("click",event=>{
    const button=event.target.closest(".oa-inspect");
    if(button)select(button.closest(".oa-item"));
  });
  sphere.addEventListener("click",event=>{
    const node=event.target.closest(".oa-node");
    if(node){selected=null;move(node.dataset.view)}
  });
  window.addEventListener("cf-spider-view",event=>{
    const detail=event.detail||{};selected=null;move(detail.view||"mine");
  });
  window.addEventListener("cf-spider-select",event=>{
    const id=event.detail&&event.detail.id;
    if(!id)return;const card=[...rail.querySelectorAll(".oa-item")].find(x=>x.dataset.actionId===id);if(card)select(card);
  });
  move("mine");
})();
