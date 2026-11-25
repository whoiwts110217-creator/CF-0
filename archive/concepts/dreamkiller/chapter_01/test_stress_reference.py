"""Run the independent stateful Dreamkiller stress suite in the existing CI discovery.

All assertions exercise a Python reference simulation. A passing result is
NOT evidence that a ROM or an iPhone emulator implemented these mechanics.
"""
from stress_reference import StressReferenceTests

__all__ = ["StressReferenceTests"]
