"""cocotb test for the register_sampling pilot.

Drives a sequence of register accesses that hit each Bin* axis:

  - Walk every address R0..R3 with WRITE+READ pairs -> BinDict 4/4
  - Issue NONE / READ / WRITE -> BinEnum 3/3
  - Cycle through size_1 / size_2 / size_4 -> 3/3
  - Write a mix of low (0..63) and high (>= 64) data values
    -> BinRange(64) interior + BinDefault "others"
  - Generate write_after_read and read_after_write transitions on cp_op
"""

from __future__ import annotations

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from cocotbext.fcov import CoverageCollector

from coverage_spec import Op, RegfileCovModel


class RegfileCollector(CoverageCollector):
    """Thin collector — `__init__` binds the model to the DUT handle."""


# Stimulus tape: (op, addr, size, wdata) tuples, run one per posedge.
STIMULUS: list[tuple[int, int, int, int]] = [
    # Walk writes across all four addresses with low data values.
    (Op.WRITE, 0, 1, 0x05),
    (Op.READ,  0, 1, 0),       # read_after_write
    (Op.WRITE, 1, 2, 0x2A),
    (Op.READ,  1, 2, 0),
    (Op.WRITE, 2, 4, 0x40),
    (Op.READ,  2, 4, 0),
    (Op.WRITE, 3, 1, 0x3F),
    (Op.READ,  3, 1, 0),
    # High-data writes -> BinDefault "others" catch-all bin.
    (Op.WRITE, 0, 4, 0x100),
    (Op.WRITE, 1, 4, 0xFFFFFF00),
    # write_after_read transition (1 -> 2 in cp_op).
    (Op.READ,  2, 2, 0),
    (Op.WRITE, 2, 2, 0xDEADBEEF),
    # NONE pulses (hits cp_op NONE bin).
    (Op.NONE,  0, 1, 0),
    (Op.NONE,  3, 4, 0),
]


@cocotb.test()
async def smoke_emit_and_sample(dut):
    cov_model = RegfileCovModel(name="cov_model")
    collector = RegfileCollector(dut, cov_model=cov_model)
    cg = collector.cov.cg_regfile

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Reset pulse.
    dut.rst.value = 1
    await Timer(15, unit="ns")
    dut.rst.value = 0

    await Timer(5, unit="ns")

    for op, addr, size, wdata in STIMULUS:
        dut.op.value    = int(op)
        dut.addr.value  = addr
        dut.size.value  = size
        dut.wdata.value = wdata
        await RisingEdge(dut.clk)
        cg.cp_addr <= addr
        cg.cp_op   <= int(op)
        cg.cp_size <= size
        # cp_data samples wdata's low 6 bits; high values fall into
        # the BinDefault "others" catch-all.
        cg.cp_data <= (wdata & 0x3F) if wdata < 64 else 0x80
        cg.sample()
        await Timer(1, unit="ns")

    dut._log.info("register_sampling: %d transactions sampled", len(STIMULUS))
