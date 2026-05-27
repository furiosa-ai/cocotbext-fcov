"""Coverage spec for the simple_dff pilot.

Covers the 1-bit Q output along two orthogonal axes:
  - cp_q       value coverage (BinBool: FALSE / TRUE)
  - cp_q_trans transition coverage (0 -> 1 and 1 -> 0)

Both coverpoints sample the same source signal (cg_dff_cp_q); cp_q_trans uses
``ref=cp_q`` to share the wire without emitting a second one.
"""

from cocotbext.fcov import (
    CoverageModel,
    CoverGroup,
    CoverPoint,
    BinBool,
)


class DffCoverGroup(CoverGroup):
    cp_q = CoverPoint(BinBool())
    # Explicit names — auto-naming of two transitions with same min/max
    # would collide (both 0->1 and 1->0 derive "bin_0_1").
    cp_q_trans = CoverPoint(
        [("up", [0, "=>", 1]), ("down", [1, "=>", 0])],
        ref=cp_q,
        name="cp_q_trans",
    )


class DffCovModel(CoverageModel):
    cg_dff = DffCoverGroup()


# Module-level instance discovered by ``make_coverage``.
cov_model = DffCovModel(name="cov_model")
