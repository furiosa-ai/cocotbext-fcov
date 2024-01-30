import pytest
from enum import Enum
from cocotbext.fcov import CoverPoint
from cocotbext.fcov import (
    BinSingle,
    BinUniform,
    BinRange,
    BinDict,
    BinEnum,
    BinBool,
    BinExp,
    BinMinMax,
    BinMinMaxExp,
    BinWindow,
    BinOneHot,
    BinDefault,
    BinOutOfSpec,
    BinBitwise,
    BinTransition,
)


def test_cp_empty():
    cp = CoverPoint()
    assert (
        str(cp) == "CoverPoint(bins=(), ignore_bins=(), illegal_bins=(), width=None, name=None, group=None, ref=None)"
    )
    assert cp.num == 0
    assert cp.width == None
    with pytest.raises(AssertionError):
        cp.signal

    cp.set_name("cp_name", "cg_name")
    cp.width = 10
    assert (
        str(cp)
        == "CoverPoint(bins=(), ignore_bins=(), illegal_bins=(), width=10, name=cp_name, group=cg_name, ref=None)"
    )
    assert cp.num == 0
    assert cp.signal == "cg_name_cp_name"
    assert cp.width == 10
    assert cp.sv_wire() == "wire [9:0] cg_name_cp_name;"
    assert cp.sv_declare() == "cp_name: coverpoint cg_name_cp_name;"
    assert cp.markdown() == {
        "Coverpoint": "cp_name",
        "Width": "[9:0]",
        "Bin Type": "Custom",
        "# of Bins": 0,
        "Bins": "",
        "Ignore Bins": "",
        "Illegal Bins": "",
    }


def test_cp_dict_list():
    bin_dict = {
        "test_a": -11,
        "test_b": range(-10, 10),
        "test_c": range(10, 20, 2),
    }
    ignore_list = [
        ("ignore_a", -10),
        range(0, 10, 2),
        ("ignore_b", range(10, 20, 5), 2),
    ]
    cp = CoverPoint(bin_dict, ignore_list, name="cp_dict", group="cg_python")
    assert (
        str(cp)
        == "CoverPoint(bins=(-11, [-10:9], (10, 12, 14, 16, 18)), ignore_bins=(-10, (0, 2, 4, 6, 8), (10, 15)),"
        " illegal_bins=(), width=None, name=cp_dict, group=cg_python, ref=None)"
    )
    assert cp.num == 3
    assert cp.signal == "cg_python_cp_dict"
    assert cp.width == 5
    assert cp.sv_wire() == "wire [4:0] cg_python_cp_dict;"
    assert (
        cp.sv_declare()
        == "cp_dict: coverpoint cg_python_cp_dict {\n"
        "bins test_a = {-11};\n"
        "bins test_b = {[-10:9]};\n"
        "bins test_c = {[10:18]} with (item % 2 == 0);\n"
        "ignore_bins ignore_a = {-10};\n"
        "ignore_bins bin_0_8 = {[0:8]} with (item % 2 == 0);\n"
        "ignore_bins ignore_b[2] = {[10:15]} with (item % 5 == 0);}"
    )
    assert cp.markdown() == {
        "Coverpoint": "cp_dict",
        "Width": "[4:0]",
        "Bin Type": "Custom",
        "# of Bins": 3,
        "Bins": "-11, [-10:9], {10, 12, 14, 16, 18}",
        "Ignore Bins": "-10, {0, 2, 4, 6, 8}, {10, 15}/2",
        "Illegal Bins": "",
    }


def test_eq():
    bin_dict = {
        "test_a": -11,
        "test_b": range(-10, 10),
        "test_c": range(10, 20, 2),
    }
    bin_list = [
        ("test", -11),
        range(-10, 10),
        (None, range(10, 20, 2)),
    ]

    assert CoverPoint(bin_dict) == CoverPoint(bin_list)
    assert CoverPoint(bin_dict, width=100) == CoverPoint(bin_list, width=100)
    with pytest.raises(AssertionError):
        assert CoverPoint(bin_dict, width=100) == CoverPoint(bin_list)


def test_cp_uniform_range_single():
    bin_uniform = BinUniform(-100, 100, 5, num=4, name="UNIFORM")
    bin_range = BinRange(-121, 98, 10, name="RANGE")
    bin_single = BinSingle(range(-10, 10), name="SINGLE")
    cp = CoverPoint(bin_uniform, bin_range, bin_single, name="cp_uniform", group="cg_predefined")
    assert (
        str(cp)
        == "CoverPoint(bins=((-100, -95, -90, ..., 90, 95)), ignore_bins=((-121, -111, -101, ..., 79, 89)),"
        " illegal_bins=([-10:9]), width=None, name=cp_uniform, group=cg_predefined, ref=None)"
    )
    assert cp.num == 4
    assert cp.signal == "cg_predefined_cp_uniform"
    assert cp.width == 8
    assert cp.sv_wire() == "wire [7:0] cg_predefined_cp_uniform;"
    assert (
        cp.sv_declare()
        == "cp_uniform: coverpoint cg_predefined_cp_uniform {\n"
        "bins UNIFORM[4] = {[-100:95]} with (item % 5 == 0);\n"
        "ignore_bins RANGE[] = {[-121:89]} with (item % 10 == 9);\n"
        "illegal_bins SINGLE = {[-10:9]};}"
    )
    assert cp.markdown() == {
        "Coverpoint": "cp_uniform",
        "Width": "[7:0]",
        "Bin Type": "Uniform",
        "# of Bins": 4,
        "Bins": "{-100, -95, -90, ..., 90, 95}/4",
        "Ignore Bins": "{-121, -111, -101, ..., 79, 89}/22",
        "Illegal Bins": "[-10:9]",
    }


def test_cp_enum_dict():
    class TestItem(Enum):
        TEST0 = range(10)
        TEST1 = range(10, 20)
        TEST2 = range(20, 30)
        TEST3 = range(30, 40)
        TEST4 = range(40, 50)

    bin_enum = BinEnum(TestItem)
    bin_enum_ignore = BinEnum([TestItem.TEST1, TestItem.TEST3, TestItem.TEST4], prefix="IGNORE")

    item_dict = {f"ILLEGAL{i}": range(i * 10, i * 10 + 5) for i in range(5)}
    bin_dict = BinDict(item_dict)

    cp = CoverPoint(bin_enum, bin_enum_ignore, bin_dict, name="cp_enum", group="cg_predefined")
    assert (
        str(cp)
        == "CoverPoint(bins=([0:9], [10:19], [20:29], [30:39], [40:49]), ignore_bins=([10:19], [30:39], [40:49]),"
        " illegal_bins=([0:4], [10:14], [20:24], [30:34], [40:44]), width=None, name=cp_enum, group=cg_predefined,"
        " ref=None)"
    )
    assert cp.num == 5
    assert cp.signal == "cg_predefined_cp_enum"
    assert cp.width == 6
    assert cp.sv_wire() == "wire [5:0] cg_predefined_cp_enum;"
    assert (
        cp.sv_declare()
        == "cp_enum: coverpoint cg_predefined_cp_enum {\n"
        "bins TEST0 = {[0:9]};\n"
        "bins TEST1 = {[10:19]};\n"
        "bins TEST2 = {[20:29]};\n"
        "bins TEST3 = {[30:39]};\n"
        "bins TEST4 = {[40:49]};\n"
        "ignore_bins IGNORE_TEST1 = {[10:19]};\n"
        "ignore_bins IGNORE_TEST3 = {[30:39]};\n"
        "ignore_bins IGNORE_TEST4 = {[40:49]};\n"
        "illegal_bins ILLEGAL0 = {[0:4]};\n"
        "illegal_bins ILLEGAL1 = {[10:14]};\n"
        "illegal_bins ILLEGAL2 = {[20:24]};\n"
        "illegal_bins ILLEGAL3 = {[30:34]};\n"
        "illegal_bins ILLEGAL4 = {[40:44]};}"
    )
    assert cp.markdown() == {
        "Coverpoint": "cp_enum",
        "Width": "[5:0]",
        "Bin Type": "Enum",
        "# of Bins": 5,
        "Bins": "TEST0([0:9]), TEST1([10:19]), TEST2([20:29]), TEST3([30:39]), TEST4([40:49])",
        "Ignore Bins": "IGNORE_TEST1([10:19]), IGNORE_TEST3([30:39]), IGNORE_TEST4([40:49])",
        "Illegal Bins": "ILLEGAL0([0:4]), ILLEGAL1([10:14]), ILLEGAL2([20:24]), ILLEGAL3([30:34]), ILLEGAL4([40:44])",
    }


def test_cp_exp_min_max():
    bin_exp = BinExp(-100, 100, base=4, prefix="EXP")
    bin_min_max = BinMinMax(min=-10, width=5, num=5, prefix="MIN_MAX")
    bin_min_max_exp = BinMinMaxExp(-32, 9, width=11, base=6, prefix="MIN_MAX_EXP")
    cp = CoverPoint(bin_exp, bin_min_max, bin_min_max_exp, name="cp_exp", group="cg_predefined")
    assert (
        str(cp)
        == "CoverPoint(bins=([-100:-65], [-64:-17], [-16:-5], [-4:-2], -1, 0, [1:3], [4:15], [16:63],"
        " [64:99]), ignore_bins=(-10, [-9:30], 31), illegal_bins=(-32, [-31:-7], [-6:-2], -1, 0, [1:5],"
        " [6:8], 9), width=None, name=cp_exp, group=cg_predefined, ref=None)"
    )
    assert cp.num == 10
    assert cp.signal == "cg_predefined_cp_exp"
    assert cp.width == 11
    assert cp.sv_wire() == "wire [10:0] cg_predefined_cp_exp;"
    assert (
        cp.sv_declare()
        == "cp_exp: coverpoint cg_predefined_cp_exp {\n"
        "bins EXP_neg100_neg65 = {[-100:-65]};\n"
        "bins EXP_neg64_neg17 = {[-64:-17]};\n"
        "bins EXP_neg16_neg5 = {[-16:-5]};\n"
        "bins EXP_neg4_neg2 = {[-4:-2]};\n"
        "bins EXP_neg1 = {-1};\n"
        "bins EXP_0 = {0};\n"
        "bins EXP_1_3 = {[1:3]};\n"
        "bins EXP_4_15 = {[4:15]};\n"
        "bins EXP_16_63 = {[16:63]};\n"
        "bins EXP_64_99 = {[64:99]};\n"
        "ignore_bins MIN_MAX_neg10 = {-10};\n"
        "ignore_bins MIN_MAX_neg9_30[3] = {[-9:30]};\n"
        "ignore_bins MIN_MAX_31 = {31};\n"
        "illegal_bins MIN_MAX_EXP_neg32 = {-32};\n"
        "illegal_bins MIN_MAX_EXP_neg31_neg7 = {[-31:-7]};\n"
        "illegal_bins MIN_MAX_EXP_neg6_neg2 = {[-6:-2]};\n"
        "illegal_bins MIN_MAX_EXP_neg1 = {-1};\n"
        "illegal_bins MIN_MAX_EXP_0 = {0};\n"
        "illegal_bins MIN_MAX_EXP_1_5 = {[1:5]};\n"
        "illegal_bins MIN_MAX_EXP_6_8 = {[6:8]};\n"
        "illegal_bins MIN_MAX_EXP_9 = {9};}"
    )
    assert cp.markdown() == {
        "Coverpoint": "cp_exp",
        "Width": "[10:0]",
        "Bin Type": "Exp",
        "# of Bins": 10,
        "Bins": "[-100:-65], [-64:-17], [-16:-5], ..., [16:63], [64:99]",
        "Ignore Bins": "-10, [-9:30]/3, 31",
        "Illegal Bins": "-32, [-31:-7], [-6:-2], ..., [6:8], 9",
    }


def test_cp_window_onehot_bool():
    bin_window = (
        BinWindow(window=0b1, width=6, prefix="WINDOW_1")
        + BinWindow(window=0b11, width=6, prefix="WINDOW_11")
        + BinDefault()
    )
    bin_onehot = BinOneHot(4, prefix="ONEHOT", format="b")
    bin_bool = BinBool()

    cp = CoverPoint(bin_window, bin_onehot, bin_bool, name="cp_window", group="cg_predefined")
    assert (
        str(cp)
        == "CoverPoint(bins=(0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x3, 0xc, 0x30, default), ignore_bins=(0b1, 0b10, 0b100,"
        " 0b1000), illegal_bins=(0, 1), width=None, name=cp_window, group=cg_predefined, ref=None)"
    )
    assert cp.num == 10
    assert cp.signal == "cg_predefined_cp_window"
    assert cp.width == 6
    assert cp.sv_wire() == "wire [5:0] cg_predefined_cp_window;"
    assert (
        cp.sv_declare()
        == "cp_window: coverpoint cg_predefined_cp_window {\n"
        "bins WINDOW_1_0x1 = {'h1};\n"
        "bins WINDOW_1_0x2 = {'h2};\n"
        "bins WINDOW_1_0x4 = {'h4};\n"
        "bins WINDOW_1_0x8 = {'h8};\n"
        "bins WINDOW_1_0x10 = {'h10};\n"
        "bins WINDOW_1_0x20 = {'h20};\n"
        "bins WINDOW_11_0x3 = {'h3};\n"
        "bins WINDOW_11_0xc = {'hc};\n"
        "bins WINDOW_11_0x30 = {'h30};\n"
        "bins others = default;\n"
        "ignore_bins ONEHOT_0b1 = {'b1};\n"
        "ignore_bins ONEHOT_0b10 = {'b10};\n"
        "ignore_bins ONEHOT_0b100 = {'b100};\n"
        "ignore_bins ONEHOT_0b1000 = {'b1000};\n"
        "illegal_bins FALSE = {0};\n"
        "illegal_bins TRUE = {1};}"
    )
    assert cp.markdown() == {
        "Coverpoint": "cp_window",
        "Width": "[5:0]",
        "Bin Type": "Custom",
        "# of Bins": 10,
        "Bins": "0x1, 0x2, 0x4, ..., 0x30, default",
        "Ignore Bins": "0b1, 0b10, 0b100, 0b1000",
        "Illegal Bins": "FALSE(0), TRUE(1)",
    }


def test_cp_out_of_spec():
    bin_out_of_spec = BinOutOfSpec()
    cp = CoverPoint(bin_out_of_spec, name="cp_out_of_spec", group="cg_predefined")
    assert (
        str(cp)
        == "CoverPoint(bins=(), ignore_bins=(), illegal_bins=(), width=None, name=cp_out_of_spec, group=cg_predefined,"
        " ref=None)"
    )
    assert cp.num == 0
    assert cp.signal == "cg_predefined_cp_out_of_spec"
    assert cp.width == None
    assert cp.sv_wire() == "wire cg_predefined_cp_out_of_spec;"
    assert cp.sv_declare() == None
    assert cp.markdown() == {
        "Coverpoint": "cp_out_of_spec",
        "Width": "",
        "Bin Type": "OutOfSpec",
        "# of Bins": 0,
        "Bins": "Out of spec",
        "Ignore Bins": "",
        "Illegal Bins": "",
    }


def test_cp_bitwise():
    bin_bitwise = BinBitwise(4)
    cp = CoverPoint(bin_bitwise, name="cp_bitwise", group="cg_predefined")
    assert (
        str(cp)
        == "CoverPoint(bins=(), ignore_bins=(), illegal_bins=(), width=None, name=cp_bitwise, group=cg_predefined,"
        " ref=None)"
    )
    assert cp.num == 8
    assert cp.signal == "cg_predefined_cp_bitwise"
    assert cp.width == 4
    assert cp.sv_wire() == "wire [3:0] cg_predefined_cp_bitwise;"
    assert (
        cp.sv_declare()
        == "cp_bitwise_0: coverpoint cg_predefined_cp_bitwise[0];\n"
        "cp_bitwise_1: coverpoint cg_predefined_cp_bitwise[1];\n"
        "cp_bitwise_2: coverpoint cg_predefined_cp_bitwise[2];\n"
        "cp_bitwise_3: coverpoint cg_predefined_cp_bitwise[3];"
    )
    assert cp.markdown() == {
        "Coverpoint": "cp_bitwise",
        "Width": "[3:0]",
        "Bin Type": "Bitwise",
        "# of Bins": 8,
        "Bins": "0, 1 for each bit",
        "Ignore Bins": "",
        "Illegal Bins": "",
    }


def test_cp_transition():
    bin_transition = BinTransition(
        [[1, 2, 3], [4, 5, 6]], [[7, 8, 9, range(10, 20)], range(20, 40)], prefix="TRANSITION"
    )
    cp = CoverPoint(bin_transition, name="cp_transition", group="cg_predefined")
    assert (
        str(cp)
        == "CoverPoint(bins=(((1, 2, 3 => 4, 5, 6)), ((7, 8, 9, [10:19] => [20:39]))), ignore_bins=(), illegal_bins=(),"
        " width=None, name=cp_transition, group=cg_predefined, ref=None)"
    )
    assert cp.num == 2
    assert cp.signal == "cg_predefined_cp_transition"
    assert cp.width == 6
    assert cp.sv_wire() == "wire [5:0] cg_predefined_cp_transition;"
    assert (
        cp.sv_declare()
        == "cp_transition: coverpoint cg_predefined_cp_transition {\n"
        "bins TRANSITION_1_6 = (1, 2, 3 => 4, 5, 6);\n"
        "bins TRANSITION_7_39 = (7, 8, 9, [10:19] => [20:39]);}"
    )
    assert cp.markdown() == {
        "Coverpoint": "cp_transition",
        "Width": "[5:0]",
        "Bin Type": "Transition",
        "# of Bins": 2,
        "Bins": "(1, 2, 3 => 4, 5, 6), (7, 8, 9, [10:19] => [20:39])",
        "Ignore Bins": "",
        "Illegal Bins": "",
    }
