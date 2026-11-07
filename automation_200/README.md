# CF-200 — Owner-Supervised Task Ledger

**Target:** 200 specific Caveman Focus work orders, organized into 10 workstreams × 20 tasks. **Checkpoint cadence:** 4 verified items. Public-by-default, source-linked progress; avoid claiming incomplete work is finished.

**Priority #1** is real AI operation of the owner's HP: command from the same ChatGPT account → CF-0 GitHub job → local HP poller → approved action → recorded receipt. Other tracks remain secondary.

`registry.json` tracks 200 work items, dependencies, observed status and evidence. `checkpoints.py` refuses a `verified` status without a specific nonempty evidence reference. Each four-task checkpoint includes a registry SHA-256 and completed IDs. A checkpoint is **not** proof that all listed activities ran on the real HP.

Run:

```powershell
py -3 automation_200\checkpoints.py status
py -3 automation_200\checkpoints.py validate
```

For developer maintenance only, after actually verifying a task, record the task ID and specific evidence:

```powershell
py -3 automation_200\checkpoints.py complete CF-001 --evidence "link-to-committed-source-and-passing-test"
py -3 automation_200\checkpoints.py checkpoint
```

Commit after every four **verified** tasks, not after generating four speculative ideas. This registry can outlive any one chat. Public source and CI can verify local claims, but user-HP tasks require independent HP evidence.

At a four-item milestone, `py -3 automation_200\checkpoints.py git-checkpoint`
creates a local commit containing the registry, event log, and numbered
checkpoint. Unrelated staged files stay staged for their own commit.
