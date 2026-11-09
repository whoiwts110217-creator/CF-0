# Habit Automator v0.1 — iPhone companion to CF-0 Mission Control

**Public route after Pages deployment:** https://whoiwts110217-creator.github.io/CF-0/mission-control/habit-automator/

**Continuity ID:** CF-HA-001  
**Parent:** CF-0 Mission Control / P0 automation. **Related:** P1 owner-priority policy, AUTO-08 continuity control, UCC-001; none are replaced.  
**Owner direction:** November 9, 2026: develop “Habit Automator” and continue to an iPhone-compatible real interface.
**Creator/developer:** David Smith. **Designated owner/intended beneficiary:** Kiara Lynn Rose Smith (not legal proof of transfer).

## What actually works in source

- Create, edit, copy, pause, resume, delete and run multiple-step local routines.
- Schedule **due-date calculations** for daily and chosen weekdays while viewing the app; manual routines remain manual.
- Confirm each step explicitly and record an **owner-marked**, non-provider-verified completion receipt.
- Launch configured HTTPS websites and **existing owner-created Apple Shortcuts** by name **on tap**.
- Keep routine and history state in device-local browser storage; export/import a private, schema-validated JSON backup.
- Install through Safari **Add to Home Screen**; a service worker caches this app's own assets for offline access after an initial successful load.
- Free static assets; no account API keys, user logins, third-party libraries, financial commands, or HP command-surface changes.

**What is NOT connected:** This static iPhone site cannot itself execute when closed, set iOS background automations, message ChatGPT conversations, scan Gmail, operate a Windows PC, pull private account data or confirm external outcomes. Apple's Shortcuts Automation must be configured by the owner independently. Clicking a launch button does not count as completion until the owner confirms. Local browser history is **not** a CF-200 receipt or source verification.

## Install on iPhone

1. Open the public route above in **Safari**.
2. Tap **Share → Add to Home Screen → Add**.
3. Add a template or create a routine with actions and a local due-time display.
4. To connect a Shortcuts step, create a named Shortcut in Apple's Shortcuts app; use the exact name as the step target. Tap **Run** then **Launch Shortcut** on a compatible iPhone.
5. Use **Export private backup** to preserve continuity before clearing Safari data or changing devices.

## Verification and provenance

- **Source:** automation_200/mission_control/dist/habit-automator/.
- **Tests:** node --test automation_200/mission_control/tests/habit-automator.test.mjs (also included in the website workflow's Mission Control suite).
- **Evidence:** source and CI attest only logic and static UI packaging; actual iPhone installed launch, offline recovery, shortcuts integration and App Store signing need separate device evidence.
- **Source version:** pin the merged commit SHA when reporting deployment; branch SHA alone does not prove Pages deployment.
- **Privacy:** only sanitized public code and sample templates in GitHub. Routines, history and backups are private on the owner's device; export is manual.
- **Permissions:** no new account or relay privileges, background scheduling, external outreach, payment or financial authority; capability contract and existing Mission Control controls stay unchanged.
- **Rollback:** revert the feature commit(s) or remove the added navigation link and habit-automator/ static directory, without touching CF-200 registry/history or AUTO-08.
- **Next action:** verify actual GitHub Pages route and iPhone install; consider an owner-reviewed authenticated adapter later, one narrow scope at a time.

**Mandatory continuation:** re-fetch automation_200/MASTER_OPERATOR_PROMPT.md, MASTER_CONTINUITY_PROMPT.md, WORK_COPY_PASTE_AUTOMATION_PROMPT.md in that order from current public main; then UCC-001 and current Mission Control/capability sources before modifications.
