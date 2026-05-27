"""Coverage spec for the adder pilot.

Four coverage axes on the 4-bit unsigned adder + carry:
  cp_a         BinUniform(16)  -- every value 0..15 on input A
  cp_b         BinUniform(16)  -- every value 0..15 on input B
  cp_a_bitwise BinBitwise(4)   -- per-bit 0/1 toggle on A
  cp_carry     BinBool         -- carry-out (X[4]) seen / not seen
  cx_a_carry   Cross           -- (A, carry) pair

The cp_a_bitwise coverage demonstrates a structural Bin* (BinBitwise)
alongside the value Bin* (BinUniform) on the same source signal.
"""

from cocotbext.fcov import (
    CoverageModel,
    CoverGroup,
    CoverPoint,
    Cross,
    BinUniform,
    BinBitwise,
    BinBool,
)


class AdderCoverGroup(CoverGroup):
    cp_a         = CoverPoint(BinUniform(16))
    cp_b         = CoverPoint(BinUniform(16))
    cp_a_bitwise = CoverPoint(BinBitwise(4), ref=cp_a)
    cp_carry     = CoverPoint(BinBool())
    cx_a_carry   = Cross([cp_a, cp_carry])


class AdderCovModel(CoverageModel):
    cg_adder = AdderCoverGroup()


# Module-level instance discovered by ``make_coverage``.
cov_model = AdderCovModel(name="cov_model")
