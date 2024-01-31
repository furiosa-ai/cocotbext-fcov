import pytest
from functools import reduce
from itertools import combinations

from cocotbext.fcov import BinItem


def test_single_int():
    value = [17, -10]
    for i in value:
        bin_item = i
        for _ in range(2):
            bin_item = BinItem(bin_item)
            assert bin_item.items == [i]
            assert bin_item.max == i
            assert bin_item.min == i
            assert bin_item.width == 5
            assert bin_item.num == 1
            assert str(bin_item) == f"{i}"
            assert bin_item.systemverilog() == f"bins bin_{i} = ".replace("-", "neg") + f"{{{i}}}"
            assert bin_item.markdown() == f"{i}"

            bin_item.width = 4
            assert bin_item.width == 4


def test_single_range():
    value = [range(10, 20), range(-10, 5)]
    for i in value:
        bin_item = i
        for _ in range(2):
            bin_item = BinItem(bin_item)
            assert bin_item.items == [i]
            assert bin_item.max == max(i)
            assert bin_item.min == min(i)
            assert bin_item.width == 5
            assert bin_item.num == 1
            assert str(bin_item) == f"[{min(i)}:{max(i)}]"
            assert (
                bin_item.systemverilog()
                == f"bins bin_{min(i)}_{max(i)} = ".replace("-", "neg") + f"{{[{min(i)}:{max(i)}]}}"
            )
            assert bin_item.markdown() == f"[{min(i)}:{max(i)}]"


def test_single_transition():
    a = range(-10, 20)
    b = range(-30, 40)
    c = range(-50, 60)
    bin_items = [
        [[a, "=>", b, ">>", c]],
        BinItem(a) >> BinItem(b) >> BinItem(c),
        BinItem(c) << BinItem(b) << BinItem(a),
    ]
    for i in bin_items:
        for _ in range(2):
            i = BinItem(i)
            assert i.max == max(max(a), max(b), max(c))
            assert i.min == min(min(a), min(b), min(c))
            assert i.width == 7
            assert i.num == 1
            assert str(i) == "([-10:19] => [-30:39] => [-50:59])"
            assert i.systemverilog() == "bins bin_neg50_59 = ([-10:19] => [-30:39] => [-50:59])"
            assert i.markdown() == "([-10:19] => [-30:39] => [-50:59])"


def test_array():
    value = range(-10, 20)
    for n in [0, 3, 10, 30]:
        bin_item = BinItem(value, num=n)
        assert bin_item.items == [value]
        assert bin_item.max == max(value)
        assert bin_item.min == min(value)
        assert bin_item.width == 5
        if n == 0:
            assert bin_item.num == len(value)
            assert str(bin_item) == f"[{min(value)}:{max(value)}]"
            assert (
                bin_item.systemverilog()
                == f"bins bin_{min(value)}_{max(value)}[] = ".replace("-", "neg") + f"{{[{min(value)}:{max(value)}]}}"
            )
            assert bin_item.markdown() == f"[{min(value)}:{max(value)}]/{len(bin_item)}"
        else:
            assert bin_item.num == n
            assert str(bin_item) == f"[{min(value)}:{max(value)}]"
            assert (
                bin_item.systemverilog()
                == f"bins bin_{min(value)}_{max(value)}[{n}] = ".replace("-", "neg")
                + f"{{[{min(value)}:{max(value)}]}}"
            )
            assert bin_item.markdown() == f"[{min(value)}:{max(value)}]/{n}"


def test_array_complex():
    value = [-11, 17, 16, 18, -16, range(-10, 15)]
    value_str = ", ".join(map(str, value[:5])) + f", [{min(value[5])}:{max(value[5])}]"
    value_max = max(*value[:5], *value[5])
    value_min = min(*value[:5], *value[5])
    for n in [0, 3, 10, 30]:
        bin_item = BinItem(value, num=n)
        assert bin_item.items == value
        assert bin_item.max == value_max
        assert bin_item.min == value_min
        assert bin_item.width == 5
        if n == 0:
            assert bin_item.num == len(value[:5]) + len(value[5])
            assert str(bin_item) == value_str
            assert (
                bin_item.systemverilog()
                == f"bins bin_{value_min}_{value_max}[] = ".replace("-", "neg") + f"{{{value_str}}}"
            )
            assert bin_item.markdown() == f"{{{value_str}}}/{len(bin_item)}"
        else:
            assert bin_item.num == n
            assert str(bin_item) == value_str
            assert (
                bin_item.systemverilog()
                == f"bins bin_{value_min}_{value_max}[{n}] = ".replace("-", "neg") + f"{{{value_str}}}"
            )
            assert bin_item.markdown() == f"{{{value_str}}}/{n}"


def test_eq():
    bin_items = [
        [-11, 17, 16, 18, -16],
        range(-10, 15),
    ]
    for i in bin_items:
        assert BinItem(i) == i
        assert BinItem(i, num=2) == i
        assert i == BinItem(i, num=3)
        assert BinItem(i, width=4) == i
        assert i == BinItem(i, width=5)
        with pytest.raises(AssertionError):
            assert BinItem(i, num=2) == BinItem(i, num=3)
            assert BinItem(i, width=4) == BinItem(i, width=5)
            assert BinItem(i, width=4) == BinItem(i, num=3)

    a = range(-10, 20)
    b = range(-30, 40)
    c = range(-50, 60)
    bin_transitions = [
        [[a, "=>", b, ">>", c]],
        BinItem(a) >> BinItem(b) >> BinItem(c),
        BinItem(c) << BinItem(b) << BinItem(a),
    ]
    for i, j in combinations(bin_transitions, 2):
        assert i == j
        assert j == i


def test_add():
    items = [
        [-11, 17, 16, 18, -16],
        range(-10, 15),
        [30, 52, 43, 38],
        range(-20, -15),
        range(-10, 5),
        [8, 6, 9, 10, 16],
    ]
    bin_items = [BinItem(i) for i in items]

    for i in range(len(bin_items) - 2):
        value = reduce(lambda a, b: a + b, map(lambda x: x.items, bin_items[i : i + 3]))
        value_str = ", ".join(map(str, bin_items[i : i + 3]))
        value_max = max(map(lambda x: x.max, bin_items[i : i + 3]))
        value_min = min(map(lambda x: x.min, bin_items[i : i + 3]))
        value_width = max(map(lambda x: x.width, bin_items[i : i + 3]))

        for bin_add in [reduce(lambda a, b: a + b, bin_items[i : i + 3]), items[i] + bin_items[i + 1] + items[i + 2]]:
            assert bin_add.items == value
            assert bin_add.max == value_max
            assert bin_add.min == value_min
            assert bin_add.width == value_width
            assert bin_add.num == 1
            assert str(bin_add) == value_str
            assert (
                bin_add.systemverilog()
                == f"bins bin_{value_min}_{value_max} = ".replace("-", "neg") + f"{{{value_str}}}"
            )
            assert bin_add.markdown(shorten=False) == f"{{{value_str}}}"


def test_add_transition():
    bin_items = [
        BinItem(range(-10, 20)),
        BinItem(1),
        BinItem(range(-50, 60)),
    ]
    add_items = [
        BinItem([30, 32, 34]),
        BinItem(range(-30, 40)),
        BinItem(-55),
    ]

    bin_item = reduce(lambda a, b: a >> b, bin_items)
    bin_item += add_items[0]
    bin_item.next.add(add_items[1])
    bin_item.next.next += add_items[2]
    bin_item = BinItem(bin_item)

    value_max = max(map(lambda x: x.max, bin_items + add_items))
    value_min = min(map(lambda x: x.min, bin_items + add_items))
    value_width = max(map(lambda x: x.width, bin_items + add_items))
    value_str = (
        "(" + reduce(lambda a, b: a + " => " + b, map(lambda a, b: str(a) + ", " + str(b), bin_items, add_items)) + ")"
    )
    assert bin_item.max == value_max
    assert bin_item.min == value_min
    assert bin_item.width == value_width
    assert bin_item.num == 1
    assert str(bin_item) == value_str
    assert bin_item.systemverilog() == f"bins bin_{value_min}_{value_max} = ".replace("-", "neg") + value_str
    assert bin_item.markdown() == value_str


def test_name():
    bin_item = BinItem(range(10), name="TEST")
    assert bin_item.systemverilog() == f"bins TEST = {{[0:9]}}"


def test_prefix():
    bin_item = BinItem(range(10), prefix="TEST")
    assert bin_item.systemverilog() == f"bins TEST_0_9 = {{[0:9]}}"


def test_format():
    value = list(range(-10, 10))
    for i in ["b", "bin", "o", "oct", "d", "dec", "x", "h", "hex"]:
        bin_item = BinItem(value, format=i)
        if i in ["b", "bin"]:
            value_list = list(map(bin, value))
            value_str_shorten = ", ".join(value_list[:3] + ["..."] + value_list[-2:])
            value_str = ", ".join(value_list)
            value_sv = "{" + value_str.replace("0b", "'b") + "}"
            value_max = bin(max(value))
            value_min = bin(min(value))
        elif i in ["o", "oct"]:
            value_list = list(map(oct, value))
            value_str_shorten = ", ".join(value_list[:3] + ["..."] + value_list[-2:])
            value_str = ", ".join(value_list)
            value_sv = "{" + value_str.replace("0o", "'o") + "}"
            value_max = oct(max(value))
            value_min = oct(min(value))
        elif i in ["x", "h", "hex"]:
            value_list = list(map(hex, value))
            value_str_shorten = ", ".join(value_list[:3] + ["..."] + value_list[-2:])
            value_str = ", ".join(value_list)
            value_sv = "{" + value_str.replace("0x", "'h") + "}"
            value_max = hex(max(value))
            value_min = hex(min(value))
        else:
            value_list = list(map(str, value))
            value_str_shorten = ", ".join(value_list[:3] + ["..."] + value_list[-2:])
            value_str = ", ".join(value_list)
            value_sv = "{" + value_str + "}"
            value_max = max(value)
            value_min = min(value)
        assert str(bin_item) == value_str
        assert bin_item.systemverilog() == f"bins bin_{value_min}_{value_max} = ".replace("-", "neg") + value_sv
        assert bin_item.markdown() == "{" + value_str_shorten + "}"
        assert bin_item.markdown(shorten=False) == "{" + value_str + "}"


def test_keyword():
    bin_item = BinItem(range(10))
    for k in ["bins", "ignore_bins", "illegal_bins"]:
        assert bin_item.systemverilog(keyword=k) == f"{k} bin_0_9 = {{[0:9]}}"
