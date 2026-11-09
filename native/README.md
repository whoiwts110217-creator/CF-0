# CF-0 native C / C++ migration

This is an **additive first component**, not a completed translation. Existing Python, JavaScript and PowerShell implementations remain in place.

## C++17 read-only JSONL structure diagnostic

GCC/Clang build: c++ -std=c++17 -O2 -Wall -Wextra -pedantic native/ledger_check.cpp -o cf-ledger-shape

Windows MSVC build: cl /std:c++17 /EHsc native\\ledger_check.cpp /Fe:cf-ledger-shape.exe

Run: cf-ledger-shape automation_200/events.jsonl

It checks basic line-level quote/object/array balance, **not** full JSON grammar, hash chains, task acceptance or HP health. It does not write files and uses no external libraries. Initial local C++ compilation and one valid/one invalid fixture passed; Windows build and full parity remain untested.

Next: add a proper parser and tests, independently port the hash-chain verifier with exact canonicalization, and then benchmark mathematical computation kernels against the Python reference. Do not remove working languages or alter the HP relay until replacements meet the existing acceptance gates.
