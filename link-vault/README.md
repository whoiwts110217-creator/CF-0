# CF-LINK-VAULT-001 — Caveman Focus iPhone Link Vault

**Parent:** CF-CORE / UCC-001 · **Related:** CF-FRESH-001, CF-MESH-001, Mission Control, CF-200, FIN-09, owner Jungle Map, Skill Foundry. 
**Owner update:** November 10, 2026 — Links are operational navigation, not decoration. The launcher must help the owner find the right workstream, update routes without replacing the whole app, and recover after a stale bookmark.

## Open and install

**Launch URL:** https://whoiwts110217-creator.github.io/CF-0/link-vault/

On iPhone **Safari**: open the URL → tap **Share** → **Add to Home Screen** → **Add**. It becomes a home-screen web app, not a native App Store app. The public page does not control ChatGPT, GitHub, your HP, payment accounts or external sessions.

## How public links update

1. Public source of truth is [`link-vault/links.json`](links.json), **not another contacts list or task registry**. Keep each link's **stable `id`** when correcting a URL; do not recycle retired IDs. Add new IDs for new public entries. Increment the `revision` field after editing. Do not add credentials, personal contacts, conversation URLs, private manuscripts or account-specific details.
2. GitHub Pages deploys this file with the site through the existing [website publishing workflow](../.github/workflows/publish-website.yml). A successful source commit is not itself proof the Pages deployment or external destination has updated.
3. On iPhone tap **↻ Refresh public links**. The app requests `./links.json` with a cache-busting query and `cache: no-store`, validates the schema, reports the revision and last successful check, and preserves local favorites/corrections. It also checks on normal app launch while connected.
4. If offline or GitHub Pages is unavailable, it displays the last saved catalog or embedded fallback, visibly labeled **not checked now**. A cached link is not a confirmed working external page.
5. Its v2 service worker uses **network-first** for the launcher, enhancement script and public JSON. Cached fallback remains available offline. One older v1 cache-first installation may require opening the link in Safari with a fresh URL once or refreshing the Home Screen app after the new worker activates.

## When a link needs a correction

- Tap **Fix link** on a public card, enter the corrected HTTPS URL, and save. **Local override only**; it is never written to public GitHub, and survives future public catalog updates until reset. Tap **Use public version** to remove the override.
- Tap **＋ Add my link** to keep a private shortcut on the device. The custom entry supports **Edit** and **Remove**. Local storage is browser/origin-specific and can be cleared by iOS or browser settings.
- Use **Export my backup** to save favorites, personal links, local public-link corrections, and the last visited doorway to Files as JSON. **Import backup** restores them. Old v1 JSON backups containing only favorites/custom links are accepted. Keep exports containing private conversations private.
- To request a public correction, use the [GitHub issue tracker](https://github.com/whoiwts110217-creator/CF-0/issues/new) **for public-safe links only**. Do not post private conversations there. Owner/maintainer changes belong in the canonical `links.json` on `main`, not in a second parallel link directory.

## Jungle Compass / get unlost

The top panel answers practical tasks, instead of demanding the user remember project titles:

| Task | Route |
| --- | --- |
| Where am I? | [Owner Jungle Map](../docs/OWNER_JUNGLE_MAP.md) (dated map; follow newest routes) |
| Run the operation | [Mission Control](https://whoiwts110217-creator.github.io/CF-0/mission-control/) (source-level dashboard) |
| Continue my work | [ChatGPT Memory Bootstrap](../docs/CHATGPT_MEMORY_BOOTSTRAP.md) (mandatory three-prompt boot) |
| What's current? | [Current Source Gateway](../docs/CURRENT_SOURCE_GATEWAY.md) + [CF-FRESH-001](../docs/UNIVERSAL_FRESHNESS_CONTRACT.md) |
| Make money | [Clarity Check offer](https://whoiwts110217-creator.github.io/CF-0/clarity-check/) and [funding evidence](../docs/BUSINESS.md) |
| Build something | [iPhone Skill Foundry](https://whoiwts110217-creator.github.io/CF-0/skill-foundry/) and [project index](../docs/PROJECTS.md) |

The **last doorway** shortcut is local history, not a record that a destination completed any task.

## Privacy, freshness and evidence

- **Only public-safe shortcuts** belong in this repository and website. No private contact workbook, personal chat URL, private source exports, keys, or payment details. Browser-local links may themselves be private; they are never sent to CF-0 by this app.
- **Refresh means catalog fetched**, not that 82 external destinations were live-checked. GitHub source pages are moving `main` URLs, but embedded historical facts can still be stale. Real payment/HP/account statuses require provider evidence.
- The latest [CF-FRESH-001 policy](../docs/UNIVERSAL_FRESHNESS_CONTRACT.md) and [gateway](../docs/CURRENT_SOURCE_GATEWAY.md) apply to these links. The original [Start Here index](../docs/START_HERE.md) remains the canonical written guide. This app is a **navigation surface** for that work, not a replacement source of truth.

## Tests, acceptance and rollback

The [website publishing workflow](../.github/workflows/publish-website.yml) runs Python source tests in [`link-vault/tests/`](tests/) and JavaScript syntax checks; staging asserts the catalog and update script are present. Passing source tests do not prove actual iOS Safari behavior. **Acceptance:** on iPhone Safari, install the launcher, open a route, check Last Doorway, fix a public link locally, refresh the public catalog, and confirm the correction/favorites survive; export to Files and reimport if desired.

**Rollback:** revert the isolated PWA commit; restore its previous `index.html` and service worker via the public commit history. A rollback does not erase browser-local saved personal URLs; export them first if migrating devices. No change was made to Mission Control's controls, AUTO-08, the HP allowlist, funding, schedules, CF-200 task statuses or private originals.

**Continuity ID:** CF-LINK-VAULT-001. Current source route: https://github.com/whoiwts110217-creator/CF-0/tree/main/link-vault ; **read current `main` each time**. Source changes are not live/deployed claims until separately checked.
