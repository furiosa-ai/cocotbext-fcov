"""cocotb test for the adder pilot.

The adder is combinational; the testbench sweeps a deterministic set of
(A, B) pairs that hit:
  - every value 0..15 on both A and B (BinUniform)
  - both polarities of every bit on A (BinBitwise)
  - the carry-out high case (A=15, B=15) and low cases (BinBool)
  - the diagonal of the A x carry cross (Cross)

A small Timer between samples lets the cocotbext-fcov sample handler
toggle the SV-side cg_adder_sample wire before the next deposit.
"""

from __future__ import annotations

import cocotb
from cocotb.triggers import Timer

from cocotbext.fcov import CoverageCollector

from coverage_spec import AdderCovModel


class AdderCollector(CoverageCollector):
    """Thin collector — `__init__` binds the model to the DUT handle."""


def _carry(a: int, b: int) -> int:
    return 1 if (a + b) >> 4 else 0


@cocotb.test()
async def smoke_emit_and_sample(dut):
    """Sweep both A and B across 0..15 + extra carry-producing combos."""

    cov_model = AdderCovModel(name="cov_model")
    collector = AdderCollector(dut, cov_model=cov_model)
    cg = collector.cov.cg_adder

    # Diagonal sweep -- A == B from 0..15. Covers every BinUniform bin
    # on both A and B at once, also flips every bit of A (BinBitwise) and
    # produces a high carry whenever A == B >= 8.
    await Timer(10, unit="ns")
    for v in range(16):
        dut.A.value = v
        dut.B.value = v
        await Timer(2, unit="ns")
        cg.cp_a     <= int(dut.A.value)
        cg.cp_b     <= int(dut.B.value)
        cg.cp_carry <= _carry(int(dut.A.value), int(dut.B.value))
        cg.sample()
        await Timer(1, unit="ns")

    # Extra anti-diagonal pairs to populate the cross corners (A=15, carry=1).
    for a, b in [(15, 1), (0, 15), (8, 8), (15, 0)]:
        dut.A.value = a
        dut.B.value = b
        await Timer(2, unit="ns")
        cg.cp_a     <= int(dut.A.value)
        cg.cp_b     <= int(dut.B.value)
        cg.cp_carry <= _carry(int(dut.A.value), int(dut.B.value))
        cg.sample()
        await Timer(1, unit="ns")

    dut._log.info("adder: sampled 20 vectors -- expecting full BinUniform on A and B + full BinBitwise on A + both BinBool bins")
