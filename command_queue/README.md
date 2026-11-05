# Public CF-0 command queue — no secrets

This path carries only allowlisted **public-safe** commands from the same ChatGPT account to the user's own Python relay on the HP. Do not include PII, finance credentials, bank-account numbers, private document contents, IP or usernames.

Create a unique `inbox/<uuid-v4>.json` with:

```json
{"v":1,"id":"<uuid-v4>","action":"ping","issued":<unix-seconds>,"expires":<unix-seconds-plus-up-to-86400>,"args":{}}
```

Supported actions: `ping`, `hp_status`, `sidecar_verify` (optional local config). Owner instructs ChatGPT with `HP: ping` or similar; the assistant commits the structured command via the connected GitHub tool. The actual HP poller reads the queue without a token and records a local receipt. An optional restricted CF-0 token on the HP enables **public-safe** receipt posts under `receipts/`. GitHub Actions testing is not an HP proof.

Queue files are retained for provenance, so archive/rotate under owner-approved policy before reaching GitHub's directory listing limits. Do not send shell commands in JSON.
