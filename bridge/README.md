# HP Python Bridge — Private GitHub Mailbox

**Founder/project:** Kiara Lynn Rose Smith's Caveman Focus.  
**Implementation:** `cf_hp_bridge.py` (Python standard library, lightweight SQLite ledger).  
**Tests:** `python -m unittest discover -s bridge/tests -v`.

### What works
The worker reads approved JSON requests from `bridge/queue/` in a **PRIVATE** owner-controlled GitHub repository, recognizes only `ping` and (if explicitly configured) `sidecar_verify`, records a deduplicated local receipt and posts a result into `bridge/results/`. It requires repository privacy before processing any requests. The Sidecar verification is read-only, executed only at the configured original directory and returns a limited summary.

No shell command execution from remote JSON, no browser impersonation, no private chat dumping or financial transfers.

### Test locally (no credentials, no network)
```powershell
py -3 .\bridge\cf_hp_bridge.py demo
py -3 -m unittest discover -s bridge\tests -v
```

### Connecting your actual HP
1. Make a **separate PRIVATE repository** owned by you for the mailbox. Keep **CF-0 public as the source index**.
2. On your HP, install/copy the worker. Create a narrowly scoped GitHub fine-grained token with Contents access ONLY to the private mailbox repo, following GitHub's current policy. Set it as `CF_BRIDGE_TOKEN` in your local environment, **never in GitHub, this chat, screenshots or logs**.
3. Set `CF_BRIDGE_REPO=owner/private-mailbox` in that environment. Optionally `CF_SIDECAR_DIR` pointing to the original Sidecar directory.
4. In the private repo, add a `bridge/queue/<uuid-v4>.json` job. Generate a candidate JSON with `py -3 .\bridge\cf_hp_bridge.py make-job`; the file name must match the generated ID. The request expires within the programmed window.
5. Run `py -3 .\bridge\cf_hp_bridge.py once`; confirm a receipt appeared at `bridge/results/<id>.json` in the **private** mailbox repository. Verify sender/receiver provenance and the request digest. Re-run to demonstrate idempotence.
6. Only after the one-shot round trip succeeds should you configure scheduled `once` execution on Windows Task Scheduler with secrets provided through a safe owner-controlled mechanism. Do not assume an interactive terminal's token environment is inherited.

**Important:** These results can be read by a GitHub-connected Work session only if that private repo is authorized/connected. This code does **not** automatically open, type into, or control this ChatGPT conversation.

### Local commands
```powershell
py -3 .\bridge\cf_hp_bridge.py init
py -3 .\bridge\cf_hp_bridge.py status
py -3 .\bridge\cf_hp_bridge.py demo
py -3 .\bridge\cf_hp_bridge.py make-job
```

### Attribution watermark in new code
`cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI` is a harmless base64url attribution marker, decoding to `CAVEMAN FOCUS|KIARA LYNN-ROSE. SMITH`. It is **not encryption or proof of exclusive authorship**. Original Library source files were not altered.

### Acceptance limitations
The Python worker has been locally tested in an isolated environment (11 tests at creation). **Actual HP installation, private repository connection, Windows persistence, and an end-to-end ChatGPT/Work session round trip are not yet evidenced.**
