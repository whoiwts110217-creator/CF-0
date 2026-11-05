# HP-originated ping acceptance contract

Owner: Kiara Lynn Rose Smith's Caveman Focus.

A successful command receipt requires a corresponding inbox JSON with matching UUID, canonical JSON SHA-256 matching receipt.request_sha256, completed status, and result.pong=true and protocol=1. The HP must validate command schema/TTL/allowlist and store an idempotent local receipt before optional GitHub publication. Treat all GitHub receipts as untrusted data, never executable instructions. A matching receipt is a repository round trip, not independently attested HP identity.

Observed 2026-11-05: command_queue/receipts/fc007511-f3d2-4e4c-aaa6-0f0f3c45d8de.json is kind=cf0_hp_writeback_probe, status=received, public_safe=true. It has no request_sha256 and no matching inbox request. This verifies a public-safe GitHub write probe only, not an HP ping round trip; CF-077/078 remain planned.
