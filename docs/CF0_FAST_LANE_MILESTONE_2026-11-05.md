# CF-0 Public Automation Milestone — 2026-11-05

## What changed
The owner's HP Windows computer now has a tested ChatGPT → public GitHub queue → local Windows relay → public-safe receipt pathway. Owner confirmed Notepad windows appeared without manually triggering PowerShell after installing a separate Fast Lane.

### Evidence and implementation
- Existing original scheduled task: `CavemanFocusCF0Relay` (preserved).
- New separate sign-in task: `CavemanFocusCF0FastLane`, approximately 30-second polling, installed and started by owner.
- Installers: [Notepad opt-in](../relay/INSTALL_NOTEPAD_CONTROL.ps1) and [Fast Lane](../relay/INSTALL_CF0_FAST_LANE.ps1).
- Worker: [allowlisted relay](../relay/cf_public_relay.py); wrapper: [read/write](../relay/cf_public_relay_rw.ps1).
- Owner-confirmed execution and public receipts for Notepad test IDs `cf200003-0000-4000-8000-00006aed47d5` and `cf200004-0000-4000-8000-00006aed47ff`.
- Four additional commands were submitted in a batch; ten more commands were submitted in a later batch. **Submitting requests does not by itself verify execution of every request.**
- Public receipts are not proof of visible GUI by themselves; owner observation plus receipts supports the Notepad demonstration.

### Limitations
- No direct push, general remote shell or arbitrary software installation. The HP must be awake and signed in for visible desktop interaction.
- Windows restart/sign-in persistence has not yet been independently demonstrated.
- Autonomous multi-step project execution, machine-enforced STOP, capability installation and seven-day unattended operation are **not yet verified**.
- This public repo must not contain secrets, personal records, private creative source or private device information.

## Governance
Read the [Autonomous Operations Rulebook v0.1](../CAVEMAN_FOCUS_RULEBOOK_v0.1.md). Standing priority order: automation → priority intelligence → financial sustainability → other projects concurrently. Intervention is preferred over repeated routine approval **within established authority boundaries**.

## Next engineering deliverable
Build a separate, bounded file-work executor and intervention controller without changing the verified Fast Lane and fallback relay. Require receipts, tests and a recovery procedure.
