# CF-200 checkpoint 40/200 — receipt recovery controls

Source: existing CF-0 relay code and previously passing Windows CI run 42074418183. No new physical HP execution or GitHub return receipt is claimed.

- CF-065: after local durable receipt save, a later poll republishes the same stored receipt rather than rerunning the action. Ambiguous network outcomes remain subject to GitHub receipt existence/equality checks; no actual dropped-connection test claimed.
- CF-066: existing remote receipt is decoded and compared for exact JSON equality before accepting it.
- CF-067: conflicting or malformed remote receipts raise an error, preventing overwrite.
- CI evidence: relay/tests/test_public_relay.py::test_idempotence, ::test_http_transport_integration, ::test_remote_existing_receipt_forgery_and_malformed_data_rejected in Windows run 42074418183.
- Current public receipts directory returned 404 (not present). HP-to-GitHub writeback still requires local credential setup and a real HP receipt.
- CF-068 (interrupted worker restart) remains planned; future test should simulate a process crash after local receipt save and before publication.

Registry now 40 verified, 160 planned. Evidence provenance is source/CI, not HP deployment.
