/* CF-LINK-VAULT-001: intentional owner-only privacy/data reset; no network or third-party APIs. */
(function(root, factory) {
  "use strict";
  const api=factory();
  if(typeof module==="object" && module.exports) module.exports=api;
  if(root && root.document) api.attach(root.document,root);
})(typeof globalThis==="object"?globalThis:this,function(){
  "use strict";
  const OWNED_KEYS=Object.freeze([
    "cf_link_vault_v1",
    "cf_link_vault_owner_action_checks_v1"
  ]);
  function purgeLocalData(storage){
    if(!storage || typeof storage.removeItem!=="function")throw Error("Browser storage unavailable");
    const cleared=[];
    for(const key of OWNED_KEYS){
      storage.removeItem(key);
      cleared.push(key);
    }
    return cleared;
  }
  function attach(doc,win){
    const trigger=doc.getElementById("privacy");
    const dialog=doc.getElementById("privacy-dialog");
    const close=doc.getElementById("privacy-close");
    const clear=doc.getElementById("privacy-clear");
    const input=doc.getElementById("privacy-confirmation");
    const feedback=doc.getElementById("privacy-status");
    if(!trigger||!dialog||!close||!clear||!input||!feedback)return;
    trigger.addEventListener("click",()=>{
      input.value="";
      feedback.textContent="This site stores some personal links and checkmarks as readable browser data.";
      clear.disabled=true;
      if(typeof dialog.showModal==="function") dialog.showModal();
    });
    input.addEventListener("input",()=>{clear.disabled=input.value!=="CLEAR"});
    close.addEventListener("click",()=>dialog.close());
    clear.addEventListener("click",()=>{
      if(input.value!=="CLEAR")return;
      try{
        purgeLocalData(win.localStorage);
      }catch(_){
        feedback.textContent="Could not clear local storage. Use Safari site data settings.";
        return;
      }
      feedback.textContent="Saved personal links, favorites, fixes, visited shortcut and action checkmarks cleared. Reloading…";
      // Imported Spider actions are held in memory only; reload releases them.
      win.location.reload();
    });
  }
  return {OWNED_KEYS,purgeLocalData,attach};
});
