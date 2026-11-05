# CF200 checkpoint 37/200 — public command rejection gates

Date: 2026-11-05. Previous verified count: 33. New verified count: 37.

CF-083–086: the public relay's exact allowlist, empty arguments and exact-key schema already reject dynamic Python evaluation, file writes, browser actions and unknown JSON fields. Existing Windows CI run 42074418183 passed relevant tests. Added explicit regression cases to relay/tests/test_public_relay.py; these new tests are **pending CI** and are not cited as already passing.

This is **source-level** security verification only. No new physical HP deployment or command execution is claimed. The public receipts directory returned GitHub 404 during this run, so bidirectional writeback is still unverified. The user must configure the HP writeback credential locally; do not put it in chat or repository. No remote shell, browser automation, or arbitrary file writes were enabled.
