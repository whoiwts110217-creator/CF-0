# Automation — Original HP, Sidecar and Research Components

## Operational chain (separate versions)
| Stage | Capability | Evidence boundary |
|---|---|---|
| Domino Sidecar v0.2 | Queue, manual packets, ledger verification | Owner Windows handoff / 3-event local ledger |
| Tactics v0.2.1 | Scheduled local checks, changed-only packets | Assistant-container tests |
| Automation Controller v0.2 | Priority policy, local worker | Assistant-container tests |
| Continuity v0.3 | Historical exports, dedupe, priority review | Assistant-container tests |
| Guardian v0.4 | Resource-aware local supervision | Assistant-container tests |
| Live Operator v0.5 | Approved feed tasks, quest board, HTTPS option | Container demonstration; not HP transport |
| Gap Foundry v0.6 | Detect and repair starving RSS item window | Synthetic/local integration |

Research prototypes v0.7–v1.2 are **not prerequisites to use the operational Sidecar**.

## Real connection target
```
Actual HP Windows Python worker
       -> approved queue + evidence
       -> authenticated outbound transport
       -> owner-authorized Work or receiving service
       -> validated response / identity / idempotent local import
```

**GitHub commit ≠ ChatGPT conversation message.** CF-0 is publicly visible; use it only for source and nonsensitive demo pings. Private chat exports require private owner-controlled storage/transport.

The machine historically had ~4 GB RAM and low disk headroom; remeasure actual resources. Prioritize standard Python libraries, SQLite, one local supervisor and a clear disable/uninstall command.
