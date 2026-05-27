"""cocotb test for the matrix_multiplier pilot.

Drives a small set of 2x2 matrix multiplications that hit:
  - hybrid bins on cp_a0 / cp_b0 (BinUniform low 0..3 + BinMinMaxExp 4/[5:7]/[8:14]/15)
  - BinMinMax boundary + uniform interior on cp_c0
  - BinMinMaxExp interior on cp_c0_mmexp (same wire via ref=)
  - both valid_o polarities
  - cross corners on (cp_a0, cp_b0)
"""

from __future__ import annotations

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from cocotbext.fcov import CoverageCollector

from coverage_spec import MatmulCovModel


class MatmulCollector(CoverageCollector):
    """Thin collector — `__init__` binds the model to the DUT handle."""


# (a_flat, b_flat) pairs. Each is a 4-element 4-bit vector for a 2x2 matrix.
# c_o[0] computed as a[0]*b[0] + a[1]*b[2]   (row 0 * col 0).
STIMULUS: list[tuple[list[int], list[int]]] = [
    # All-zero -> C[0] = 0 (BinMinMax boundary low)
    ([0, 0, 0, 0], [0, 0, 0, 0]),
    # Diagonal small -> exp bucket bin_1 on A[0]/B[0]
    ([1, 0, 0, 1], [1, 0, 0, 1]),
    # Mid-range -> exp bucket bin_2_3 / bin_4_7
    ([3, 2, 5, 4], [2, 3, 4, 5]),
    # High range with non-zero result -> bucket bin_8_15
    ([15, 0, 0, 15], [15, 0, 0, 15]),  # C[0] = 15*15 + 0 = 225
    # Maximum result -> C[0] = 2*15*15 = 450 (boundary high)
    ([15, 15, 0, 0], [15, 15, 0, 0]),  # C[0] = 15*15 + 15*15 = 450
    # Variety to fill cross corners
    ([1, 2, 3, 4],  [4, 3, 2, 1]),
    ([8, 4, 2, 1],  [1, 2, 4, 8]),
    ([10, 5, 5, 10], [5, 10, 10, 5]),
]


@cocotb.test()
async def smoke_emit_and_sample(dut):
    cov_model = MatmulCovModel(name="cov_model")
    collector = MatmulCollector(dut, cov_model=cov_model)
    cg = collector.cov.cg_matmul

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Reset pulse.
    dut.reset.value = 1
    dut.valid_i.value = 0
    await Timer(15, unit="ns")
    dut.reset.value = 0

    await Timer(5, unit="ns")

    for a_flat, b_flat in STIMULUS:
        for i, v in enumerate(a_flat):
            dut.a_i[i].value = v
        for i, v in enumerate(b_flat):
            dut.b_i[i].value = v
        dut.valid_i.value = 1
        await RisingEdge(dut.clk)
        # Result is registered, one cycle after valid_i.
        await RisingEdge(dut.clk)
        cg.cp_a0       <= int(dut.a_i[0].value)
        cg.cp_b0       <= int(dut.b_i[0].value)
        cg.cp_c0       <= int(dut.c_o[0].value)
        cg.cp_c0_mmexp <= int(dut.c_o[0].value)
        cg.cp_valid_o  <= int(dut.valid_o.value)
        cg.sample()
        dut.valid_i.value = 0
        await Timer(1, unit="ns")

    dut._log.info("matrix_multiplier: %d 2x2 multiplications sampled", len(STIMULUS))
