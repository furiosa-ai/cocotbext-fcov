from enum import Enum
from itertools import combinations_with_replacement

import pytest

from cocotbext.fcov import CoverPoint, Cross
from cocotbext.fcov import (
    BinUniform,
    BinOneHot,
    BinBitwise,
    BinEnum,
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


# ---------------------------------------------------------------------------
# Cross-level ignore_bins / illegal_bins (commit 7f5dba0)
# Public-API surface only: assertions go through Cross.sv_declare() output.
# ---------------------------------------------------------------------------


class _Op(Enum):
    READ = 0
    WRITE = 1
    WRAP = 2


def _make_op_size_cps():
    cp_op = CoverPoint(BinEnum(_Op), name="cp_op", group="cg_xx")
    cp_size = CoverPoint(BinUniform(16), name="cp_size", group="cg_xx")
    return cp_op, cp_size


def test_cross_ignore_bins_int_value():
    cp_op, cp_size = _make_op_size_cps()
    cx = Cross(
        [cp_op, cp_size],
        name="cx_op_size",
        group="cg_xx",
        ignore_bins=[{"name": "ig_wrap0", "terms": [(cp_op, 2), (cp_size, 0)]}],
    )
    assert cx.sv_declare() == (
        "cx_op_size: cross cp_op, cp_size {\n"
        "  ignore_bins ig_wrap0 = binsof(cp_op) intersect {2} && binsof(cp_size) intersect {0};\n"
        "}"
    )


def test_cross_illegal_bins_int_value():
    cp_op, cp_size = _make_op_size_cps()
    cx = Cross(
        [cp_op, cp_size],
        name="cx_op_size",
        group="cg_xx",
        illegal_bins=[{"name": "il_read_at_0", "terms": [(cp_op, 0), (cp_size, 0)]}],
    )
    assert cx.sv_declare() == (
        "cx_op_size: cross cp_op, cp_size {\n"
        "  illegal_bins il_read_at_0 = binsof(cp_op) intersect {0} && binsof(cp_size) intersect {0};\n"
        "}"
    )


@pytest.mark.parametrize(
    "value_spec, expected_inside_braces",
    [
        ("WRAP", "WRAP"),
        ("1, 3, 5", "1, 3, 5"),
        ("[17:256]", "[17:256]"),
        (7, "7"),
        (range(10), "[0:9]"),
        (range(0, 8, 2), "0, 2, 4, 6"),
        ([1, 3, 5], "1, 3, 5"),
        ((1, 3, 5), "1, 3, 5"),
        ([1, 3, range(5, 8)], "1, 3, [5:7]"),
    ],
    ids=[
        "str_identifier",
        "str_comma_list",
        "str_range",
        "int",
        "range_step1",
        "range_step2",
        "list_int",
        "tuple_int",
        "list_mixed_int_range",
    ],
)
def test_cross_clause_value_spec_dispatch(value_spec, expected_inside_braces):
    cp_op, _ = _make_op_size_cps()
    cx = Cross(
        [cp_op],
        name="cx_a",
        group="cg_xx",
        ignore_bins=[{"name": "ig", "terms": [(cp_op, value_spec)]}],
    )
    sv = cx.sv_declare()
    assert f"binsof(cp_op) intersect {{{expected_inside_braces}}}" in sv


def test_cross_clause_negate_wraps_bang_paren():
    cp_op, cp_size = _make_op_size_cps()
    cx = Cross(
        [cp_op, cp_size],
        name="cx_neg",
        group="cg_xx",
        illegal_bins=[{"name": "il", "terms": [(cp_op, 1, True), (cp_size, 0)]}],
    )
    sv = cx.sv_declare()
    assert "!(binsof(cp_op) intersect {1})" in sv
    assert " && binsof(cp_size) intersect {0}" in sv


def test_cross_term_bad_arity_raises():
    cp_op, _ = _make_op_size_cps()
    cx_one_tuple = Cross(
        [cp_op],
        name="cx_bad",
        group="cg_xx",
        ignore_bins=[{"name": "ig", "terms": [(cp_op,)]}],
    )
    with pytest.raises(ValueError, match="2- or 3-tuple"):
        cx_one_tuple.sv_declare()

    cx_four_tuple = Cross(
        [cp_op],
        name="cx_bad",
        group="cg_xx",
        ignore_bins=[{"name": "ig", "terms": [(cp_op, 1, True, "extra")]}],
    )
    with pytest.raises(ValueError, match="2- or 3-tuple"):
        cx_four_tuple.sv_declare()


def test_cross_multi_term_and_join():
    cp_op, cp_size = _make_op_size_cps()
    cx = Cross(
        [cp_op, cp_size],
        name="cx_multi",
        group="cg_xx",
        ignore_bins=[
            {
                "name": "ig_multi",
                "terms": [(cp_op, 2), (cp_size, range(8, 16)), (cp_op, 1, True)],
            }
        ],
    )
    sv = cx.sv_declare()
    assert (
        "ignore_bins ig_multi = "
        "binsof(cp_op) intersect {2}"
        " && binsof(cp_size) intersect {[8:15]}"
        " && !(binsof(cp_op) intersect {1});"
    ) in sv


def test_cross_bitwise_with_clauses_broadcasts_body():
    """Pin the design choice at coverage.py:506-514: when a Cross with
    ignore/illegal clauses is bitwise-expanded into N sub-crosses, the same
    clause body is appended to every sub-cross. Locks this semantic so a
    future refactor surfaces the change."""
    cp_op = CoverPoint(BinEnum(_Op), name="cp_op", group="cg_xx")
    cp_bw = CoverPoint(BinBitwise(2), name="cp_bw", group="cg_xx")
    cx = Cross(
        [cp_op, cp_bw],
        name="cx_op_bw",
        group="cg_xx",
        ignore_bins=[{"name": "ig", "terms": [(cp_op, 2)]}],
    )
    sv = cx.sv_declare()
    body = " {\n  ignore_bins ig = binsof(cp_op) intersect {2};\n}"
    assert f"cx_op_bw_0: cross cp_op, cp_bw_0{body}" in sv
    assert f"cx_op_bw_1: cross cp_op, cp_bw_1{body}" in sv
