"""Coverage spec for the opcode_cross pilot.

Demonstrates the Cross + ignore_bins + illegal_bins flow:

  cp_op            BinEnum         ADD / SUB / AND / OR
  cp_a             BinExp(16)      exponential buckets on operand A (0..15)
  cp_a_onehot      BinOneHot(4)    ref=cp_a -- the four one-hot patterns
                                   (1, 2, 4, 8) on the same input wire
  cp_b             BinExp(16)      operand B
  cp_result_zero   BinBool         "result == 0" flag

  cx_op_zero       Cross(op, result_zero) with:
                     ignore_bins  ig_and_zero  (AND op producing zero is
                                                trivially uninteresting --
                                                exclude from closure goal)
                     illegal_bins il_or_zero   (OR producing zero implies
                                                both operands zero; the
                                                guide explains why we flag
                                                it as illegal in this DUT's
                                                test scenario)
"""

from enum import IntEnum

from cocotbext.fcov import (
    CoverageModel,
    CoverGroup,
    CoverPoint,
    Cross,
    BinEnum,
    BinExp,
    BinBool,
    BinOneHot,
)


class Op(IntEnum):
    ADD = 0
    SUB = 1
    AND = 2
    OR  = 3


class AluCoverGroup(CoverGroup):
    cp_op          = CoverPoint(BinEnum(Op))
    cp_a           = CoverPoint(BinExp(16, base=2))
    cp_a_onehot    = CoverPoint(BinOneHot(4), ref=cp_a)
    cp_b           = CoverPoint(BinExp(16, base=2))
    cp_result_zero = CoverPoint(BinBool())

    # SV LRM: `binsof(cp) intersect {<value>}` -- the set takes integer
    # values, not bin names. Pass the integer encoding (Op.AND=2, OR=3;
    # cp_result_zero TRUE=1).
    cx_op_zero = Cross(
        [cp_op, cp_result_zero],
        name="cx_op_zero",
        ignore_bins=[
            {"name":  "ig_and_zero",
             "terms": [(cp_op, int(Op.AND)), (cp_result_zero, 1)]},
        ],
        illegal_bins=[
            {"name":  "il_or_zero",
             "terms": [(cp_op, int(Op.OR)), (cp_result_zero, 1)]},
        ],
    )


class AluCovModel(CoverageModel):
    cg_alu = AluCoverGroup()


# Module-level instance discovered by ``make_coverage``.
cov_model = AluCovModel(name="cov_model")
