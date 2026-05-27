"""Coverage spec for the matrix_multiplier pilot.

Compact "magnitude / range" coverage via combined Bin* patterns:

  cp_a0          one CoverPoint, one wire, hybrid bin set:
                   BinUniform(4, num=4)      0..3 split into 4 single-value
                                             sub-bins (fine-grained low)
                 + BinMinMaxExp(4, 15)       4 / [5:7] / [8:14] / 15
                                             (boundary + exp high)
                 -> bins: 0,1,2,3, 4, [5:7], [8:14], 15
  cp_b0          same shape on operand B
  cp_c0          BinMinMax(0, 450, num=5)    coarse boundary + uniform interior
                 + BinMinMaxExp(0, 450)      (ref=cp_c0) boundary + exp interior
  cp_valid_o     BinBool                     valid_o flag
  cx_a0_b0       Cross(cp_a0, cp_b0)         cross-product on the hybrid spec

The cp_a0/cp_b0 emit demonstrates BinGroup.__add__ combining a
BinUniform-with-num low region with a BinMinMaxExp high region in
ONE coverpoint -- no ref= needed for that pair. The cp_c0 pair
retains ref= because both halves want to sample the same result
wire with two different range shapes (BinMinMax + BinMinMaxExp).
"""

from cocotbext.fcov import (
    CoverageModel,
    CoverGroup,
    CoverPoint,
    Cross,
    BinUniform,
    BinMinMax,
    BinMinMaxExp,
    BinBool,
)


# Hybrid factory: fine-grained low region (0..3 split into 4) +
# boundary/exp high region (4, [5:7], [8:14], 15).
def _hybrid_4bit():
    return BinUniform(4, num=4) + BinMinMaxExp(min=4, max=15, base=2)


class MatmulCoverGroup(CoverGroup):
    cp_a0        = CoverPoint(_hybrid_4bit(), name="cp_a0")
    cp_b0        = CoverPoint(_hybrid_4bit(), name="cp_b0")
    cp_c0        = CoverPoint(BinMinMax(min=0, max=450, num=5))
    cp_c0_mmexp  = CoverPoint(BinMinMaxExp(min=0, max=450, base=2), ref=cp_c0)
    cp_valid_o   = CoverPoint(BinBool())

    cx_a0_b0 = Cross([cp_a0, cp_b0], name="cx_a0_b0")


class MatmulCovModel(CoverageModel):
    cg_matmul = MatmulCoverGroup()


# Module-level instance discovered by ``make_coverage``.
cov_model = MatmulCovModel(name="cov_model")
