# Parallel coordination: isolated source experiment

This directory implements **advisory, side-effect-free preflight checks** for competing CF-0 operators. It does **not** create an atomic GitHub lock, claim a CF-200 work order, contact an HP, alter a scheduler, or write to the mission board.

Run from this directory with Python 3.10+:

```sh
python -m unittest -v test_parallel_guard
```

The test module contains 12 synthetic cases. Their presence does **not** mean they passed in GitHub Actions or on the owner's HP.

**Important limitation:** Two workers may pass local preflight concurrently. The actual remote update must still enforce the current blob SHA or an equivalent server-side compare-and-swap. Expired claims are not proof that a peer has stopped; avoid duplicate irreversible actions. Durable cross-worker claims and CI integration remain future work.

**Branch:** `experiment/parallel-coordination-v1` (not merged to `main`).  
**Related policy:** [Parallel Operator Coordination](../../docs/PARALLEL_OPERATOR_COORDINATION.md).  
**Preflight source blobs:** operator `f3d4d0d443323528a64c6aa9e9d4c9a3b30e8098`; continuity `cac63dead1e00592c1d12ea6562639b02893d81f`; Work `5da1a390f31ee8f57e5829ef368062f9215c28ac`.  
**Initial registry observation:** 69/200, blob `8114ecc161c4ffd8773913625b5b48b52f6ef5a7`. Check current main before any promotion.
