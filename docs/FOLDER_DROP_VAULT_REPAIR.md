# CF-0 Folder Drop Vault — machine-reader repair contract (November 8, 2026)

**Existing Site:** `folder-drop-vault.whoiwts110217.chatgpt.site`. This is a **repair requirement**, not evidence of deployment. User requires **drop entire folders once; ChatGPT later reads all files without user zipping/uploading again**. The Site previously reported a 109-file upload/extraction test; the test is historical account context, not independently re-run in this source change.

## Grounded blocker

- `web.run` denied external `.chatgpt.site` URL access in the current chat, independently of the existence of any ZIP endpoint. The Python execution container failed DNS on `github.com`, `google.com` and the vault host: **the container is network-isolated, not evidence of bad DNS for this single Site**.
- Sites uses managed HTTP hosting and supports durable file storage through R2; audience-sharing settings separately govern access. A public share page is **not** proof an agent can fetch the ZIP bytes.
- The current assistant can use a connected **GitHub** tool for repository resources, but has **no direct Sites editor / Work Cloud Browser** tool in this session. Sites changes must be made in that site's own Work/@Sites editor; do not claim this repo has deployed them.

## Minimal fix in the EXISTING Site (not a replacement)

1. Preserve the current drag-folder upload, nested and empty paths, byte hashes, downloadable ZIP, ~95 MiB limit, and prior uploads. Save a version before editing.
2. From the existing `/d/{opaque_id}` share page, expose explicit read-only **machine-readable** `GET /api/d/{opaque_id}/manifest.json` with versioned JSON: `share_id`, `created_at`, `file_count`, `total_uncompressed_bytes`, and `files:[{path,size_bytes,sha256}]`. Use no absolute local filesystem paths; preserve empty folders explicitly as directory entries. File data is stored and served only by the existing site's R2 backend.
3. Expose `GET /api/d/{opaque_id}/download.zip` with `Content-Type: application/zip`, an attachment `Content-Disposition`, a known `Content-Length` when possible, and support for streaming/large downloads and `HEAD` or an equivalent lightweight metadata check. These are **proposed paths**; adapt to the actual existing code, do not claim they already exist.
4. An unguessable share ID must gate both endpoints; ensure ownership controls, a revoke mechanism, and link-only downloads if the user has explicitly enabled public sharing. Test Site-level sharing and app-level sign-in **separately**. Never expose GitHub tokens, Cloudflare credentials or files in public client JavaScript.
5. **Cross-origin blocker:** if ordinary ChatGPT web-reading tools still reject `chatgpt.site` by host even when those endpoints work, provide an **optional explicit export to a supported, connected destination**. Reuse the already connected GitHub integration only if suitable binary transfer and access can be verified, using owner-approved scope/server-side credentials. Do not silently publish source archives in public CF-0; use private storage by default for raw archives and public sanitized metadata only. This is not a request to expand HP permissions.
6. Return two links after upload: a human-friendly `/d/{id}` page and a **machine-usable content origin that has been tested by the receiving ChatGPT environment**. Do not label a link 'ChatGPT-readable' on assumptions.

## Required acceptance tests

- Reopen the owner's two already-shared drops in a permitted Sites/Work browser (do not copy their capability URLs into public GitHub). For each: verify 200/206 downloadable ZIP, correct size/hash, manifest path count, all nested and empty folders, and archive zip-slip and ZIP-bomb limits before extraction.
- Test *outside* owner sign-in via a public/anonymous browser for the agreed share scope; private shares must fail closed. Confirm redirects, 401/403, 404 and revoked tokens.
- Test **from a real consuming assistant**: fetch ZIP *bytes*, extract and list 10 representative files, compare manifest, and preserve provenance. A successful upload or 200 HTML response is insufficient.
- Run the read-only **GitHub Actions root-host network probe** in `.github/workflows/vault-access-probe.yml`. The probe reports HTTP status only and **does not fetch share links or validate ZIP delivery**. If Cloudflare blocks external automated readers, a same-host ZIP route alone cannot repair this; use Work Cloud Browser for the site or the approved external connected destination.
- Preserve existing v7 private archive and CF-0 task registry. Do not mark an HP action, full chat export, sale, or CF-200 task complete from these tests.

**Action in Sites editor:** Open **existing** Folder Drop Vault under ChatGPT Sites, ask @Sites to implement this contract in place, save a reviewable version, test both existing drops and deploy only after the end-to-end readback passes. No new schedule, paid dependency or alternative upload workflow is required.

## GitHub-runner proof (November 8)

The first [external probe run](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42512259162/job/128827650453) **passed five offline tests and observed HTTP 200** from the *Site homepage* using `HEAD /` on a GitHub-hosted Ubuntu runner. The reported JSON had `state=root_reachable`, `share_files_fetched=0`, and `end_to_end_archive_access_verified=false`. This establishes **one connected external environment can reach the host**. It does NOT establish that any specific shared drop can be reached, downloaded or extracted. It also does not remove the separate current-chat web-reader block. The existing Site-side workflow can now be tested from a reachable cloud runner or through the owner-authorized Sites/Work editor, with link IDs kept outside public GitHub source.

**Next operator step:** In ChatGPT Work with @Sites, open the *existing* Folder Drop Vault project. Inspect the actual share handler, R2 keys, audience configuration and both owner-provided links in the private Work context. Prove ZIP bytes and manifest, then save and deploy any needed site-side amendment. If a new external download origin is necessary for this chat, obtain explicit approval of the destination and verify that the connected ChatGPT reader can retrieve actual bytes before declaring the vault fixed. Do not embed unlisted share URLs into public pull requests or workflow logs.
