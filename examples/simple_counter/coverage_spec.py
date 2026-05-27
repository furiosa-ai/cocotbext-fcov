"""Coverage spec for the simple_counter pilot.

Three coverage axes on a 4-bit counter:
  cp_value     BinRange(16)    -- every count value 0..15
  cp_overflow  BinBool         -- overflow pulse seen / not seen
  cx_val_ovf   Cross           -- (value, overflow) pair coverage
"""

from cocotbext.fcov import (
    CoverageModel,
    CoverGroup,
    CoverPoint,
    Cross,
    BinRange,
    BinBool,
)


class CounterCoverGroup(CoverGroup):
    cp_value    = CoverPoint(BinRange(16))
    cp_overflow = CoverPoint(BinBool())
    cx_val_ovf  = Cross([cp_value, cp_overflow])


class CounterCovModel(CoverageModel):
    cg_counter = CounterCoverGroup()


# Module-level instance discovered by ``make_coverage``.
cov_model = CounterCovModel(name="cov_model")
