"""cocotb test for the simple_dff pilot.

Drives clk + d into the vendored dff DUT, samples cp_q after each posedge.
After enough toggles, cg_dff should reach 100% functional coverage on VCS or
Questa (FALSE + TRUE bins, plus 0->1 / 1->0 transitions).

Verilator 5.038 records compile + sample-call-reach only; functional bin hits
are no-op there (verilator/#7099).
"""

from __future__ import annotations

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from cocotbext.fcov import CoverageCollector

from coverage_spec import DffCovModel


class DffCollector(CoverageCollector):
    """Thin collector — `__init__` binds the model to the DUT handle."""


@cocotb.test()
async def smoke_emit_and_sample(dut):
    """Exercise both Q values + both transitions, then exit cleanly."""

    cov_model = DffCovModel(name="cov_model")
    collector = DffCollector(dut, cov_model=cov_model)
    cg = collector.cov.cg_dff

    # Free-running clock.
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Let the cocotbext-fcov sample-handler thread initialise.
    await Timer(20, unit="ns")

    # Pattern: 0, 1, 1, 0, 0, 1, 0, 1 — exercises both values + both
    # transitions (0->1 at step 1, 1->0 at step 3, 0->1 at step 5, etc.).
    pattern = [0, 1, 1, 0, 0, 1, 0, 1]
    for d_val in pattern:
        dut.d.value = d_val
        await RisingEdge(dut.clk)
        cg.cp_q <= int(dut.q.value)
        cg.sample()
        # Let _drive + sample handler complete before the next edge.
        await Timer(1, unit="ns")

    dut._log.info("simple_dff: sampled %d values, expecting both BinBool bins + both BinTransition bins", len(pattern))
