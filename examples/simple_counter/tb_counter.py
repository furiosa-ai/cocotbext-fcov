"""cocotb test for the simple_counter pilot.

Resets the counter, then runs it for >16 cycles so every value 0..15 is
hit and the overflow pulse fires at least once. After enough cycles the
cross cp_value x cp_overflow also gets at least the value=15, overflow=1
combination.
"""

from __future__ import annotations

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from cocotbext.fcov import CoverageCollector

from coverage_spec import CounterCovModel


class CounterCollector(CoverageCollector):
    """Thin collector — `__init__` binds the model to the DUT handle."""


@cocotb.test()
async def smoke_emit_and_sample(dut):
    """Hit every value 0..15 + the overflow pulse; sample after every clk."""

    cov_model = CounterCovModel(name="cov_model")
    collector = CounterCollector(dut, cov_model=cov_model)
    cg = collector.cov.cg_counter

    # Free-running clock.
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Reset pulse.
    dut.rst.value = 1
    dut.enable.value = 0
    await Timer(15, unit="ns")
    dut.rst.value = 0
    dut.enable.value = 1

    # Let the sample-handler thread initialise.
    await Timer(5, unit="ns")

    # Run ~20 cycles so we cover 0..15 + at least one overflow pulse.
    for _ in range(20):
        await RisingEdge(dut.clk)
        cg.cp_value    <= int(dut.value.value)
        cg.cp_overflow <= int(dut.overflow.value)
        cg.sample()
        await Timer(1, unit="ns")

    dut._log.info("simple_counter: sampled 20 cycles, expecting full BinRange(16) + overflow")
