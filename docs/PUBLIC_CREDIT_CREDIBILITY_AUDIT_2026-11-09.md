# CF-0 — Harsh public credibility, credit and publication audit

**Audited:** November 9, 2026 (Eastern) · **Evidence:** public repository source on `main`, not a browser-rendered end-to-end website test.  
**Scope:** author and owner credit; contributor and donor recognition; licensing; public technical claims; accessibility for a first-time reviewer; public fundraising presentation.  
**Boundary:** recommendations below are **not** legal determinations, ownership transfers, permission grants, donor confirmations, grant awards, or evidence of physical HP/Chrome operation.

## Verdict

**Public-facing project readiness: 5/10 (subjective editorial assessment).** Source work is real and evidence caveats are unusually explicit, but the website currently prioritizes broad invitations and a sprawling project catalog over one immediately reproducible demonstration. Public trust is limited by ambiguous reuse rights and two overlapping meanings of “Hall of Fame.” No external donor payment, automatic signed-in Chrome sweep, real-HP end-to-end autonomy, or paid product fulfillment was proven by this source audit.

**Evidence snapshot:** `automation_200/registry.json` records **87 of 200 verified work orders** (source/operational units, **not product completion**). There are **20** GitHub Actions workflow files (not 20 running agents). The private archive is described as **62 reconstructed project entries**, with **zero original full conversation exports indexed** in the last examined v7 snapshot; these records must never be portrayed as 62 recovered original projects. These source counts can change and must be refreshed before future publication.

## Critical / high findings

| Rank | Issue | Exact public evidence | Required change / acceptance |
|---|---|---|---|
| **P0 — RIGHTS** | **No repository-wide license file**; `llms.txt` incorrectly described the repository as “open source.” A publicly accessible repository does **not** itself grant reuse rights. | Public [repository tree](https://github.com/whoiwts110217-creator/CF-0/tree/main); [`llms.txt`](../llms.txt). | **Fix the “open source” phrase now** (done in accompanying patch). Separately obtain actual authorized rights-holder decision: whether any code gets a license, which files/media are reserved, contributor terms, trademark/brand use, and copyright notices. Do not generate a license or imply ownership transfer without explicit authorization. |
| **P0 — CREDIT** | Project role labels vary in emphasis. [README](../README.md), [Start Here](START_HERE.md) and [owner contract](../automation_200/OWNER_CAPABILITY_CONTRACT.json) name **David Smith as creator/developer**, **Kiara Lynn Rose Smith as designated owner/intended generational beneficiary**; [homepage footer](../index.html) says “Kiara Lynn Rose Smith's Caveman Focus” without explaining the distinction. | Those public sources; [reconciliation](CONTINUITY_RECONCILIATION_2026-11-07_DREAMKILLER.md). | Keep both historical and current wording; owner to approve one standard *public role statement* and placement on the homepage. Do **not** claim legal title, transfer completion, or asset control based solely on documentation. Preserve the brand phrase if deliberately approved, accompanied by clear role descriptions. |
| **P0 — RECOGNITION** | A technical/community contributor [Hall of Fame](HALL_OF_FAME.md) and a [First Drop donor “Founding Hall of Fame”](FIRST_DROP_CAMPAIGN_2026-11-09.md) share “Hall of Fame” wording. | Source pages and [First Drop site](../first-drop/index.html). | Separate **Contributors & Discoveries** (verified test or accepted contribution, with consent) from **Founding Supporters** (verified support + opt-in name). No payment earns authorship, scientific validation, ownership, investment, or technical merit. Provide correction/removal request channel without publishing private donor details. |
| **P1 — PROOF** | 87/200 and many CI links can create a false sense of finished-system completeness. A disabled master controller and code-only AUTO-08 have no demonstrated signed-in end-to-end acceptance. | [Project Status](PROJECT_STATUS.md), [Master Controller audit](MASTER_CONTROLLER_AUDIT_2026-11-09.md), [AUTO-08 source](../automation_200/continuation_chrome/). | A **single first-screen status card**: Source exists / Tests pass / Real local deployment / End-to-end result / Money verified. Link the latest current CI run and state every unverified item. Never equate scheduled GitHub workflow count with agent uptime. |
| **P1 — USABILITY** | New visitors encounter five-level navigation and project sprawl before a reproducible one-minute test. The master operating prompt is extremely long and unsuitable as a landing-page pitch. | [Homepage](../index.html), [Start Here](START_HERE.md), [Project index](PROJECTS.md). | One clear demonstration: goal, 60-second exercise or harmless offline test, expected output, screenshot or text transcript from a **verified** run, link to source, and limits. Keep the full research atlas behind “Explore projects.” |
| **P1 — FUNDING** | The top of the public site emphasizes voluntary donations. The [First Drop campaign](FIRST_DROP_CAMPAIGN_2026-11-09.md) headline says “Give any amount and you're in,” while verification + display-name consent are requirements later. | [Homepage](../index.html), [First Drop campaign](FIRST_DROP_CAMPAIGN_2026-11-09.md), [First Drop source](../first-drop/index.html). | Make the optional recognition condition clear **alongside** every invitation. Show what voluntary support pays for (e.g. measured hosting/testing cost, when documented), and offer a no-payment “try the method” option with comparable visibility. No fabricated backer totals, charity status or investment benefits. |
| **P1 — LIVE VALIDATION** | GitHub source files and Pages deploy CI do not verify what an iPhone user sees, whether third-party support pages remain accessible, or whether a Cash App recipient is correct now. | [Public categorization audit](SITE_AND_PUBLIC_CATEGORIZATION_AUDIT_2026-11-07.md); source-only audit here. | Run owner-visible phone + desktop checks for homepage, Mission Control, First Drop, link/contrast/keyboard semantics. Record actual URL, date, screenshot or reproducible result; do not mark a site live merely because source merged. |
| **P2 — FRESHNESS** | README stage date (Nov 6) and older project/continuity snapshots coexist with Nov 9 code and the newer read-only private crosswalk. Readers may treat old evidence as current. | [README](../README.md), [Projects](PROJECTS.md), [Continuity](CONTINUITY.md), [private crosswalk source](../continuity/conversation_crosswalk.py). | Central “As checked [date/commit]” readout with separate source status and real-device test status. Do not bulk rewrite archived historical reports. Link newer code and its limits from the primary project index. |

## Proposed public credit standard — requires rights-holder/owner approval

**Draft, not a legal conclusion:** “Caveman Focus is developed by David Smith. Kiara Lynn Rose Smith is the designated owner and intended generational beneficiary under the project's recorded plan. Legal title and any transfer terms are not independently established by this public repository.”

- Give individually attributable contributors credit for **evidenced, accepted work**, using their selected public name with permission and a link to the reviewed work. Keep technical and financial recognition **separate**.
- Disclose AI assistance accurately where material; AI tools are not automatically human coauthors or rights holders. Do not erase human creative work, reviewer contributions, or earlier corrections.
- For software reuse, the authorized parties must select a license (or explicitly reserve rights). If only some components are offered for reuse, specify their exact directories/files. Consider a separate media/IP rights notice, with qualified legal review before public terms are finalized.
- Treat a project “designated owner” and a legal owner as different claims. When historical attribution differs from the current record, retain source/date and a correction note rather than rewriting the archive to imply it never happened.

## Publication-order recommendations

1. **Now — factual label fix:** `llms.txt` describes the code as **publicly viewable** instead of “open source.” No grant of reuse rights.
2. **Next — editorial front page:** Add a compact **What works / What is tested / What remains open** summary, with just three calls to action: “Try,” “See evidence,” “Support voluntarily.” Don't lead solely with the donor button.
3. **Next — explicit attribution decision:** Obtain approved creator/developer, designated owner, contributors and supporter naming policy. Then apply consistently to homepage, First Drop, README, source license/copyright notices, and Hall of Fame sections.
4. **Next — responsible rights notice:** Approved repository-wide or file-scoped license and separate original-story/media terms. Do not treat a public URL as consent to commercial reuse.
5. **After real tests — live release claims:** Show an independently reviewed Chrome one-tab test (AUTO-08), an actual owner-local HP verification, and an available public 60-second demonstration. Link exact run IDs and failures.
6. **Later — funding readiness:** Show an honest monthly amount **only if supported by documented costs**, delivery examples, and confirmed donations or sales; preserve unknowns as unknown.

## Recommended publication gates

- **Attribution gate:** human project roles are explicitly approved and internally consistent, with no unsupported transfer/legal claim.
- **Rights gate:** license or rights-reserved explanation accurately matches the actual repository.
- **Evidence gate:** every prominent numerical claim has a current source, observation date, acceptance scope and caveat.
- **Privacy gate:** no personal exports, private chat IDs, payment records, HP paths, secrets, personal donor names without consent, or unpublished creative source in GitHub.
- **Site gate:** tested actual mobile + desktop routes; no broken donation, checkout, or external-site assertions.
- **Rollback:** all editorial changes revertible by Git commit; preserve original prose/history and the public issue/contributor evidence.

## What was changed as part of this audit

- Added this **public-safe, source-linked review**.
- Corrected a false “open source” characterization in `llms.txt` while **not adding/changing a license**, public project ownership, donation campaign wording, external contact, schedules, or finance state.
- Added a navigation link to this audit from `README.md` to make recommendations visible. This source update does **not** establish a deployed website, new sale, new project verification or legal rights.

**Source boundaries:** The public pages could not be fully loaded via the available browser retrieval path in this review; this is **source-audit only**, not an independently reproduced public iPhone rendering. Use [public status](PROJECT_STATUS.md) and [registry](../automation_200/registry.json) for separately dated engineering counts. Do not confuse this editorial score with a measured community survey.
