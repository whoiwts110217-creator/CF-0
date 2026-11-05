# HP Bridge — Private Mailbox Pilot v0.2

**Kiara Lynn Rose Smith's Caveman Focus.**

Start with **[v0.2 Setup and Protocol](README_V02.md)**.

The public CF-0 repository contains source code, tests and launchers, **not private conversations or secrets**. The worker reads an owner-controlled separate **PRIVATE** GitHub mailbox, accepts only `ping` or an explicitly configured read-only `sidecar_verify`, and returns a receipt. The private mailbox must exist before a live test.

On the HP, use `RUN_HP_BRIDGE_DEMO.bat` for the offline test, then `SETUP_HP_BRIDGE_WINDOWS.bat` for interactive setup, private-repo verification and opt-in scheduling. `HP_BRIDGE_STATUS.bat` checks the local schedule; `STOP_HP_BRIDGE_WINDOWS.bat` removes it.

**v0.2 fixes:** a starvation bug where only ten oldest jobs were ever visible, and a multi-line Sidecar verification parsing defect. Tests here use a fake mailbox; independently, the read-only `sidecar_verify` result was exercised against the authentic Sidecar v0.2 source in a disposable folder. The PowerShell scheduler must be tested on a real Windows machine before claiming installation.

**Attribution note:** new code contains `cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI`, a reversible nonfunctional attribution marker for `CAVEMAN FOCUS|KIARA LYNN-ROSE. SMITH`, not a cryptographic originality proof.

No remote shell execution, arbitrary scripts, financial transactions, public posting or automatic ChatGPT chat messages are authorized by a queue file.
