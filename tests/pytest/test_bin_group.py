import pytest
from cocotbext.fcov import BinGroup, BinCustom


def test_bin_empty():
    bin_group = BinGroup()
    assert bin_group.type == "Custom"
    assert bin_group.width == None
    assert bin_group.num == 0
    assert repr(bin_group) == "BinGroup(bins=(), width=None, prefix=bin, format=d)"
    assert str(bin_group) == ""
    assert bin_group.systemverilog() == ""
    assert bin_group.markdown() == ""

    width = 10
    bin_group.width = width
    assert bin_group.type == "Custom"
    assert bin_group.width == width
    assert bin_group.num == 0
    assert str(bin_group) == ""
    assert repr(bin_group) == "BinGroup(bins=(), width=10, prefix=bin, format=d)"
    assert bin_group.systemverilog() == ""
    assert bin_group.markdown() == ""


def test_bin_single():
    value = range(-10, 10)
    value_str = "[-10:9]"
    bin_group = BinGroup([value])
    assert bin_group.type == "Custom"
    assert bin_group.width == 5
    assert bin_group.num == 1
    assert str(bin_group) == value_str
    assert repr(bin_group) == f"BinGroup(bins=({value_str}), width=None, prefix=bin, format=d)"
    assert bin_group.systemverilog() == f"bins bin_neg10_9 = {{{value_str}}};"
    assert bin_group.markdown() == value_str

    bin_group = BinCustom([("TEST", value)])
    assert bin_group.type == "Custom"
    assert bin_group.width == 5
    assert bin_group.num == 1
    assert bin_group.systemverilog() == f"bins TEST = {{{value_str}}};"
    assert bin_group.markdown() == value_str

    num_bin = 5
    bin_group = BinGroup([("TEST", value, num_bin)])
    assert bin_group.type == "Custom"
    assert bin_group.width == 5
    assert bin_group.num == num_bin
    assert bin_group.systemverilog() == f"bins TEST[{num_bin}] = {{{value_str}}};"
    assert bin_group.markdown() == value_str + f"/{num_bin}"


def test_bin_dict():
    bin_dict = {
        "test_a": -11,
        "test_b": range(-10, 10),
        "test_c": range(10, 20, 2),
    }
    bin_group = BinGroup(bin_dict)
    assert bin_group.type == "Custom"
    assert bin_group.width == 5
    assert bin_group.num == 3
    assert str(bin_group) == "-11, [-10:9], (10, 12, 14, 16, 18)"
    assert repr(bin_group) == "BinGroup(bins=(-11, [-10:9], (10, 12, 14, 16, 18)), width=None, prefix=bin, format=d)"
    assert (
        bin_group.systemverilog()
        == "bins test_a = {-11};\nbins test_b = {[-10:9]};\nbins test_c = {[10:18]} with (item % 2 == 0);"
    )
    assert bin_group.markdown() == "-11, [-10:9], {10, 12, 14, 16, 18}"


def test_bin_list():
    bin_list = [
        ("test", -11),
        range(-10, 10),
        (None, range(10, 20, 2), 5),
    ]
    bin_group = BinGroup(bin_list)
    assert bin_group.type == "Custom"
    assert bin_group.width == 5
    assert bin_group.num == 7
    assert str(bin_group) == "-11, [-10:9], (10, 12, 14, 16, 18)"
    assert repr(bin_group) == "BinGroup(bins=(-11, [-10:9], (10, 12, 14, 16, 18)), width=None, prefix=bin, format=d)"
    assert (
        bin_group.systemverilog()
        == "bins test = {-11};\nbins bin_neg10_9 = {[-10:9]};\nbins bin_10_18[5] = {[10:18]} with (item % 2 == 0);"
    )
    assert bin_group.markdown() == "-11, [-10:9], {10, 12, 14, 16, 18}/5"


def test_prefix():
    bin_list = [
        -11,
        5,
        -21,
        10,
        1,
    ]
    bin_group = BinGroup(bin_list, prefix="test")
    assert bin_group.type == "Custom"
    assert bin_group.width == 6
    assert bin_group.num == 5
    assert str(bin_group) == "-11, 5, -21, 10, 1"
    assert repr(bin_group) == f"BinGroup(bins=(-11, 5, -21, 10, 1), width=None, prefix=test, format=d)"
    assert (
        bin_group.systemverilog()
        == "bins test_neg11 = {-11};\n"
        "bins test_5 = {5};\n"
        "bins test_neg21 = {-21};\n"
        "bins test_10 = {10};\n"
        "bins test_1 = {1};"
    )
    assert bin_group.markdown() == "-11, 5, -21, 10, 1"


def test_eq():
    bin_dict = {
        "test_a": -11,
        "test_b": range(-10, 10),
        "test_c": range(10, 20, 2),
    }
    assert bin_dict == BinGroup(bin_dict)
    with pytest.raises(AssertionError):
        assert bin_dict == BinGroup(bin_dict, width=100)

    bin_list = [
        (None, range(10, 20, 2)),
        range(-10, 10),
        ("test", -11),
    ]
    assert bin_list == BinGroup(bin_list)
    with pytest.raises(AssertionError):
        assert bin_list == BinGroup(bin_list, width=100)

    assert bin_list == BinGroup(bin_dict)
    assert bin_dict == BinGroup(bin_list)
    assert BinGroup(bin_dict, width=100) == BinGroup(bin_list, width=100)


def test_add():
    bin_dict = {
        "test_a": -11,
        "test_b": range(-10, 10),
        "test_c": range(10, 20, 2),
    }
    bin_list = [
        ("test_a", bin_dict["test_a"]),
        bin_dict["test_b"],
        ("test_c", bin_dict["test_c"], 5),
    ]
    bin_group = BinGroup([bin_list[0]]) + BinGroup([bin_list[1]])
    bin_group += BinGroup([bin_list[2]])
    assert bin_group.type == "Custom"
    assert bin_group.width == 5
    assert bin_group.num == 7
    assert str(bin_group) == "-11, [-10:9], (10, 12, 14, 16, 18)"
    assert repr(bin_group) == "BinGroup(bins=(-11, [-10:9], (10, 12, 14, 16, 18)), width=None, prefix=bin, format=d)"
    assert (
        bin_group.systemverilog()
        == "bins test_a = {-11};\nbins bin_neg10_9 = {[-10:9]};\nbins test_c[5] = {[10:18]} with (item % 2 == 0);"
    )
    assert bin_group.markdown() == "-11, [-10:9], {10, 12, 14, 16, 18}/5"
