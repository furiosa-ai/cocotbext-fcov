"""cocotb test for the opcode_cross pilot.

Hits every Bin* axis + walks the cross matrix on (op, result_zero):
  - All four ops (ADD/SUB/AND/OR)               -> BinEnum 4/4
  - Operand magnitudes 0..15                    -> BinExp 5/5 buckets
  - One-hot operand patterns 1, 2, 4, 8         -> BinOneHot 4/4
  - Result zero / non-zero                      -> BinBool 2/2
  - Cross (op, result_zero) with one ignore + one illegal clause
    documented in coverage_spec.py.
"""

from __future__ import annotations

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from cocotbext.fcov import CoverageCollector

from coverage_spec import AluCovModel, Op


class AluCollector(CoverageCollector):
    """Thin collector — `__init__` binds the model to the DUT handle."""


# (op, a, b) tuples. Sampling happens after every posedge.
STIMULUS: list[tuple[int, int, int]] = [
    # ADD: hit BinExp buckets + carry corners
    (Op.ADD, 0, 0),     # zero result
    (Op.ADD, 1, 1),     # bucket bin_1
    (Op.ADD, 2, 1),     # bucket bin_2_3
    (Op.ADD, 5, 3),     # bucket bin_4_7
    (Op.ADD, 8, 8),     # bucket bin_8_15 (wraps to 0 -- result_zero TRUE)
    # SUB: produce zero by equality
    (Op.SUB, 7, 7),     # 0
    (Op.SUB, 4, 1),     # 3
    # AND: ig_and_zero clause exercises here (AND -> zero)
    (Op.AND, 0xF, 0x0), # 0
    (Op.AND, 0xA, 0x5), # 0
    (Op.AND, 0xF, 0xF), # 15
    # OR: never produce zero -> covers il_or_zero "shouldn't happen" intent
    (Op.OR,  0x1, 0x2), # 3
    (Op.OR,  0x4, 0x8), # 12
    (Op.OR,  0xF, 0xF), # 15
    # One-hot patterns on operand A (1, 2, 4, 8) for BinOneHot.
    (Op.ADD, 0x1, 0),
    (Op.ADD, 0x2, 0),
    (Op.ADD, 0x4, 0),
    (Op.ADD, 0x8, 0),
]


@cocotb.test()
async def smoke_emit_and_sample(dut):
    cov_model = AluCovModel(name="cov_model")
    collector = AluCollector(dut, cov_model=cov_model)
    cg = collector.cov.cg_alu

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Reset pulse.
    dut.rst.value = 1
    await Timer(15, unit="ns")
    dut.rst.value = 0

    await Timer(5, unit="ns")

    for op, a, b in STIMULUS:
        dut.op.value = int(op)
        dut.a.value  = a
        dut.b.value  = b
        await RisingEdge(dut.clk)
        # result + result_zero update one cycle after inputs (registered output).
        await RisingEdge(dut.clk)
        cg.cp_op          <= int(op)
        cg.cp_a           <= a
        cg.cp_b           <= b
        cg.cp_result_zero <= int(dut.result_zero.value)
        cg.sample()
        await Timer(1, unit="ns")

    dut._log.info("opcode_cross: %d ALU ops sampled", len(STIMULUS))
