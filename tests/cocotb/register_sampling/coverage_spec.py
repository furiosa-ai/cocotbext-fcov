"""Coverage spec for the register_sampling pilot.

Shows the widest variety of Bin* patterns on a single pilot:

  cp_addr      BinDict          addr 0..3 -> register names (R0..R3)
  cp_op        BinEnum          op 0/1/2 -> NONE / READ / WRITE
  cp_size      [(name, value)]  three discrete sizes 1 / 2 / 4 byte
  cp_data      BinRange + BinDefault   covers 0..63 explicitly, "others" catch-all
  cp_op_trans  inline transitions      WRITE->READ and READ->WRITE on the
                                       cp_op source signal (via ref=)
  cx_op_addr   Cross            (op, addr) pair coverage
"""

from enum import IntEnum

from cocotbext.fcov import (
    CoverageModel,
    CoverGroup,
    CoverPoint,
    Cross,
    BinDict,
    BinEnum,
    BinRange,
    BinDefault,
)


class Op(IntEnum):
    NONE  = 0
    READ  = 1
    WRITE = 2


class RegfileCoverGroup(CoverGroup):
    cp_addr  = CoverPoint(BinDict({"R0": 0, "R1": 1, "R2": 2, "R3": 3}))
    cp_op    = CoverPoint(BinEnum(Op))
    # NOTE: "byte" / "word" are SV reserved keywords -- avoid as bin names.
    cp_size  = CoverPoint(
        [("size_1", 1), ("size_2", 2), ("size_4", 4)],
        name="cp_size",
    )
    cp_data  = CoverPoint(BinRange(64) + BinDefault(), name="cp_data")
    cp_op_trans = CoverPoint(
        [
            ("write_after_read", [1, "=>", 2]),
            ("read_after_write", [2, "=>", 1]),
        ],
        ref=cp_op,
        name="cp_op_trans",
    )
    cx_op_addr = Cross([cp_op, cp_addr])


class RegfileCovModel(CoverageModel):
    cg_regfile = RegfileCoverGroup()


# Module-level instance discovered by ``make_coverage``.
cov_model = RegfileCovModel(name="cov_model")
