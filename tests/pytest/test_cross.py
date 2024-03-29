import pytest
from itertools import combinations_with_replacement
from cocotbext.fcov import CoverPoint, Cross
from cocotbext.fcov import (
    BinUniform,
    BinOneHot,
    BinBitwise,
)


def test_cross():
    bin_list = [
        BinUniform(-100, 100, 5, num=4, name="UNIFORM"),
        BinOneHot(4, prefix="ONEHOT", format="b"),
        BinBitwise(4),
    ]

    for bin in combinations_with_replacement(bin_list, 3):
        cp = [CoverPoint(b, name=b.type.lower(), group="cg_predefined") for b in bin]
        cx_name = "_x_".join(i.name for i in cp)
        cx = Cross(cp, name=cx_name, group="cg_cross")
        assert cx.name == cx_name
        assert (
            str(cx)
            == f"Cross(coverpoints=({', '.join(cp.name for cp in cx.coverpoints)}), name={cx_name}, group=cg_cross)"
        )

        if any(i.is_bitwise_bin for i in cp):
            bitwise_cx = []
            for i in range(4):
                bitwise_cp = ", ".join(f"{c.name}_{i}" if c.is_bitwise_bin else c.name for c in cp)
                bitwise_sv = f"{cx_name}_{i}: cross {bitwise_cp};"
                bitwise_cx.append(bitwise_sv)
            cx_sv = "\n".join(bitwise_cx)
        else:
            cx_cp = ", ".join(i.name for i in cp)
            cx_sv = f"{cx_name}: cross {cx_cp};"
        assert cx.sv_declare() == cx_sv


def test_cross_list():
    bin_uniforms = [CoverPoint(BinUniform(20, num=4), name=f"cp_uniform_{i}", group="cg_cross") for i in range(2)]
    bin_onehots = [CoverPoint(BinOneHot(4), name=f"cp_onehot_{i}", group="cg_cross") for i in range(2)]
    for cp in [bin_uniforms + bin_onehots, [bin_uniforms[0], bin_uniforms[1], *bin_onehots]]:
        cx = Cross(cp, name="cx_uniform_onehot", group="cg_cross")
        assert (
            str(cx)
            == "Cross(coverpoints=(cp_uniform_0, cp_uniform_1, cp_onehot_0, cp_onehot_1), name=cx_uniform_onehot,"
            " group=cg_cross)"
        )
        assert cx.sv_declare() == "cx_uniform_onehot: cross cp_uniform_0, cp_uniform_1, cp_onehot_0, cp_onehot_1;"


def test_eq():
    cp_uniform = CoverPoint(BinUniform(-100, 100, 5, num=4, name="UNIFORM"))
    cp_onehot = CoverPoint(BinOneHot(4, prefix="ONEHOT", format="b"))
    cp_bitwise = CoverPoint(BinBitwise(4))
    assert Cross([cp_uniform, cp_onehot, cp_bitwise]) == Cross([cp_onehot, cp_bitwise, cp_uniform])
    with pytest.raises(AssertionError):
        assert Cross([cp_uniform, cp_onehot]) == Cross([cp_onehot, cp_bitwise])
