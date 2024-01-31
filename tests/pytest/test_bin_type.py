import pytest
import numpy as np
from enum import Enum
from cocotbext.fcov import (
    BinSingle,
    BinUniform,
    BinRange,
    BinDict,
    BinEnum,
    BinBool,
    BinExp,
    BinMinMax,
    BinMinMaxUniform,
    BinMinMaxExp,
    BinWindow,
    BinOneHot,
    BinDefault,
    BinOutOfSpec,
    BinBitwise,
    BinTransition,
)


def test_bin_single():
    bin_single = BinSingle(-100)
    assert bin_single.type == "Single"
    assert bin_single.width == 8
    assert bin_single.num == 1
    assert bin_single.systemverilog() == "bins bin_neg100 = {-100};"
    assert bin_single.markdown() == "-100"

    bin_single = BinSingle(range(-100, 100), name="TEST")
    assert bin_single.type == "Single"
    assert bin_single.width == 8
    assert bin_single.num == 1
    assert bin_single.systemverilog() == "bins TEST = {[-100:99]};"
    assert bin_single.markdown() == "[-100:99]"


def test_bin_uniform():
    bin_uniform = BinUniform(width=6)
    assert bin_uniform.type == "Uniform"
    assert bin_uniform.width == 6
    assert bin_uniform.num == 64
    assert bin_uniform.systemverilog() == "bins bin_0_63[] = {[0:63]};"
    assert bin_uniform.markdown() == "[0:63]/64"

    bin_uniform = BinUniform(100, num=2)
    assert bin_uniform.type == "Uniform"
    assert bin_uniform.width == 7
    assert bin_uniform.num == 2
    assert bin_uniform.systemverilog() == "bins bin_0_99[2] = {[0:99]};"
    assert bin_uniform.markdown() == "[0:99]/2"

    bin_uniform = BinUniform(-100, 100, num=3, name="TEST")
    assert bin_uniform.type == "Uniform"
    assert bin_uniform.width == 8
    assert bin_uniform.num == 3
    assert bin_uniform.systemverilog() == "bins TEST[3] = {[-100:99]};"
    assert bin_uniform.markdown() == "[-100:99]/3"

    bin_uniform = BinUniform(-100, 100, 5, num=4, name="TEST2")
    assert bin_uniform.type == "Uniform"
    assert bin_uniform.width == 8
    assert bin_uniform.num == 4
    assert bin_uniform.systemverilog() == "bins TEST2[4] = {[-100:95]} with (item % 5 == 0);"
    assert bin_uniform.markdown() == "{-100, -95, -90, ..., 90, 95}/4"

    bin_uniform = BinUniform(-321, 98, 4, num=5, name="TEST3")
    assert bin_uniform.type == "Uniform"
    assert bin_uniform.width == 10
    assert bin_uniform.num == 5
    assert bin_uniform.systemverilog() == "bins TEST3[5] = {[-321:95]} with (item % 4 == 3);"
    assert bin_uniform.markdown() == "{-321, -317, -313, ..., 91, 95}/5"


def test_bin_range():
    bin_range = BinRange(100)
    assert bin_range.type == "Range"
    assert bin_range.width == 7
    assert bin_range.num == 100
    assert bin_range.systemverilog() == "bins bin_0_99[] = {[0:99]};"
    assert bin_range.markdown() == "[0:99]/100"

    bin_range = BinRange(-100, 100, name="TEST")
    assert bin_range.type == "Range"
    assert bin_range.width == 8
    assert bin_range.num == 200
    assert bin_range.systemverilog() == "bins TEST[] = {[-100:99]};"
    assert bin_range.markdown() == "[-100:99]/200"

    bin_range = BinRange(-100, 100, 5, name="TEST2")
    assert bin_range.type == "Range"
    assert bin_range.width == 8
    assert bin_range.num == 40
    assert bin_range.systemverilog() == "bins TEST2[] = {[-100:95]} with (item % 5 == 0);"
    assert bin_range.markdown() == "{-100, -95, -90, ..., 90, 95}/40"

    bin_range = BinRange(-321, 98, 4, name="TEST3")
    assert bin_range.type == "Range"
    assert bin_range.width == 10
    assert bin_range.num == 105
    assert bin_range.systemverilog() == "bins TEST3[] = {[-321:95]} with (item % 4 == 3);"
    assert bin_range.markdown() == "{-321, -317, -313, ..., 91, 95}/105"


def test_bin_dict():
    item_dict = {f"TEST{i}": range(i * 10, (i + 1) * 10) for i in range(5)}
    bin_dict = BinDict(item_dict)
    assert bin_dict.width == 6
    assert bin_dict.num == 5
    assert bin_dict.systemverilog() == "\n".join(f"bins TEST{i} = {{[{i*10}:{i*10+9}]}};" for i in range(5))
    assert bin_dict.markdown() == ", ".join(f"TEST{i}([{i*10}:{i*10+9}])" for i in range(5))


def test_bin_enum():
    class TestItem(Enum):
        TEST0 = range(10)
        TEST1 = range(10, 20)
        TEST2 = range(20, 30)
        TEST3 = range(30, 40)
        TEST4 = range(40, 50)

    bin_enum = BinEnum(TestItem)
    assert bin_enum.width == 6
    assert bin_enum.num == 5
    assert bin_enum.systemverilog() == "\n".join(f"bins TEST{i} = {{[{i*10}:{i*10+9}]}};" for i in range(5))
    assert bin_enum.markdown() == ", ".join(f"TEST{i}([{i*10}:{i*10+9}])" for i in range(5))

    bin_enum = BinEnum([TestItem.TEST1, TestItem.TEST3, TestItem.TEST4], prefix="PRE")
    assert bin_enum.width == 6
    assert bin_enum.num == 3
    assert bin_enum.systemverilog() == "\n".join(f"bins PRE_TEST{i} = {{[{i*10}:{i*10+9}]}};" for i in [1, 3, 4])
    assert bin_enum.markdown() == ", ".join(f"PRE_TEST{i}([{i*10}:{i*10+9}])" for i in [1, 3, 4])

    class TestDuplicate(Enum):
        DUPLICATE0 = 10
        DUPLICATE1 = 10
        DUPLICATE2 = 20
        DUPLICATE3 = 30
        DUPLICATE4 = 30

    bin_enum = BinEnum(TestDuplicate)
    assert bin_enum.width == 5
    assert bin_enum.num == 5
    assert bin_enum.systemverilog() == "\n".join(f"bins DUPLICATE{i} = {{{np.clip(i*10, 10, 30)}}};" for i in range(5))
    assert bin_enum.markdown() == ", ".join(f"DUPLICATE{i}({np.clip(i*10, 10, 30)})" for i in range(5))


def test_bin_bool():
    bin_bool = BinBool()
    assert bin_bool.width == 1
    assert bin_bool.num == 2
    assert bin_bool.systemverilog() == "bins FALSE = {0};\nbins TRUE = {1};"
    assert bin_bool.markdown() == "FALSE(0), TRUE(1)"

    bin_bool = BinBool(prefix="TEST", format="b")
    assert bin_bool.width == 1
    assert bin_bool.num == 2
    assert bin_bool.systemverilog() == "bins TEST_FALSE = {'b0};\nbins TEST_TRUE = {'b1};"
    assert bin_bool.markdown() == "TEST_FALSE(0b0), TEST_TRUE(0b1)"


def test_bin_exp():
    bin_exp = BinExp(100)
    assert bin_exp.type == "Exp"
    assert bin_exp.width == 7
    assert bin_exp.num == 8
    assert (
        bin_exp.systemverilog()
        == "bins bin_0 = {0};\n"
        "bins bin_1 = {1};\n"
        "bins bin_2_3 = {[2:3]};\n"
        "bins bin_4_7 = {[4:7]};\n"
        "bins bin_8_15 = {[8:15]};\n"
        "bins bin_16_31 = {[16:31]};\n"
        "bins bin_32_63 = {[32:63]};\n"
        "bins bin_64_99 = {[64:99]};"
    )
    assert bin_exp.markdown() == "0, 1, [2:3], ..., [32:63], [64:99]"
    assert bin_exp.markdown(shorten=False) == "0, 1, [2:3], [4:7], [8:15], [16:31], [32:63], [64:99]"

    bin_exp = BinExp(-100, 100, base=3, prefix="TEST")
    assert bin_exp.type == "Exp"
    assert bin_exp.width == 8
    assert bin_exp.num == 12
    assert (
        bin_exp.systemverilog()
        == "bins TEST_neg100_neg82 = {[-100:-82]};\n"
        "bins TEST_neg81_neg28 = {[-81:-28]};\n"
        "bins TEST_neg27_neg10 = {[-27:-10]};\n"
        "bins TEST_neg9_neg4 = {[-9:-4]};\n"
        "bins TEST_neg3_neg2 = {[-3:-2]};\n"
        "bins TEST_neg1 = {-1};\n"
        "bins TEST_0 = {0};\n"
        "bins TEST_1_2 = {[1:2]};\n"
        "bins TEST_3_8 = {[3:8]};\n"
        "bins TEST_9_26 = {[9:26]};\n"
        "bins TEST_27_80 = {[27:80]};\n"
        "bins TEST_81_99 = {[81:99]};"
    )
    assert bin_exp.markdown() == "[-100:-82], [-81:-28], [-27:-10], ..., [27:80], [81:99]"
    assert (
        bin_exp.markdown(shorten=False)
        == "[-100:-82], [-81:-28], [-27:-10], [-9:-4], [-3:-2], -1, 0, [1:2], [3:8], [9:26], [27:80], [81:99]"
    )

    bin_exp = BinExp(-100, 100, 5, base=4, prefix="TEST2")
    assert bin_exp.type == "Exp"
    assert bin_exp.width == 8
    assert bin_exp.num == 10
    assert (
        bin_exp.systemverilog()
        == "bins TEST2_neg100_neg65 = {[-100:-65]} with (item % 5 == 0);\n"
        "bins TEST2_neg64_neg19 = {[-64:-19]} with (item % 5 == 1);\n"
        "bins TEST2_neg16_neg6 = {[-16:-6]} with (item % 5 == 4);\n"
        "bins TEST2_neg4 = {-4};\n"
        "bins TEST2_neg1 = {-1};\n"
        "bins TEST2_0 = {0};\n"
        "bins TEST2_1 = {1};\n"
        "bins TEST2_4_14 = {[4:14]} with (item % 5 == 4);\n"
        "bins TEST2_16_61 = {[16:61]} with (item % 5 == 1);\n"
        "bins TEST2_64_99 = {[64:99]} with (item % 5 == 4);"
    )
    assert (
        bin_exp.markdown()
        == "{-100, -95, -90, ..., -70, -65}, {-64, -59, -54, ..., -24, -19}, {-16, -11, -6}, ..., {16, 21, 26, ..., 56,"
        " 61}, {64, 69, 74, ..., 94, 99}"
    )
    assert (
        bin_exp.markdown(shorten=False)
        == "{-100, -95, -90, -85, -80, -75, -70, -65}, {-64, -59, -54, -49, -44, -39, -34, -29, -24, -19}, {-16, -11,"
        " -6}, -4, -1, 0, 1, {4, 9, 14}, {16, 21, 26, 31, 36, 41, 46, 51, 56, 61}, {64, 69, 74, 79, 84, 89, 94, 99}"
    )

    bin_exp = BinExp(-321, 98, 4, base=5, prefix="TEST3")
    assert bin_exp.type == "Exp"
    assert bin_exp.width == 10
    assert bin_exp.num == 9
    assert (
        bin_exp.systemverilog()
        == "bins TEST3_neg321_neg129 = {[-321:-129]} with (item % 4 == 3);\n"
        "bins TEST3_neg125_neg29 = {[-125:-29]} with (item % 4 == 3);\n"
        "bins TEST3_neg25_neg9 = {[-25:-9]} with (item % 4 == 3);\n"
        "bins TEST3_neg5 = {-5};\n"
        "bins TEST3_neg1 = {-1};\n"
        "bins TEST3_0 = {0};\n"
        "bins TEST3_1 = {1};\n"
        "bins TEST3_5_21 = {[5:21]} with (item % 4 == 1);\n"
        "bins TEST3_25_97 = {[25:97]} with (item % 4 == 1);"
    )
    assert (
        bin_exp.markdown()
        == "{-321, -317, -313, ..., -133, -129}, {-125, -121, -117, ..., -33, -29}, {-25, -21, -17, -13, -9}, ..., {5,"
        " 9, 13, 17, 21}, {25, 29, 33, ..., 93, 97}"
    )
    assert (
        bin_exp.markdown(shorten=False)
        == "{-321, -317, -313, -309, -305, -301, -297, -293, -289, -285, -281, -277, -273, -269, -265, -261, -257,"
        " -253, -249, -245, -241, -237, -233, -229, -225, -221, -217, -213, -209, -205, -201, -197, -193, -189,"
        " -185, -181, -177, -173, -169, -165, -161, -157, -153, -149, -145, -141, -137, -133, -129}, {-125, -121,"
        " -117, -113, -109, -105, -101, -97, -93, -89, -85, -81, -77, -73, -69, -65, -61, -57, -53, -49, -45, -41,"
        " -37, -33, -29}, {-25, -21, -17, -13, -9}, -5, -1, 0, 1, {5, 9, 13, 17, 21}, {25, 29, 33, 37, 41, 45, 49,"
        " 53, 57, 61, 65, 69, 73, 77, 81, 85, 89, 93, 97}"
    )

    bin_exp = BinExp(width=7, base=6, prefix="TEST4")
    assert bin_exp.type == "Exp"
    assert bin_exp.width == 7
    assert bin_exp.num == 4
    assert (
        bin_exp.systemverilog()
        == "bins TEST4_0 = {0};\n"
        "bins TEST4_1_5 = {[1:5]};\n"
        "bins TEST4_6_35 = {[6:35]};\n"
        "bins TEST4_36_127 = {[36:127]};"
    )
    assert bin_exp.markdown() == "0, [1:5], [6:35], [36:127]"


def test_bin_min_max():
    min_max_class = {
        "MinMax": BinMinMax,
        "MinMaxUniform": BinMinMaxUniform,
    }
    for bin_type, bin_class in min_max_class.items():
        bin_min_max = bin_class(max=100, num=1)
        assert bin_min_max.type == bin_type
        assert bin_min_max.width == 7
        assert bin_min_max.num == 1
        assert bin_min_max.systemverilog() == "bins bin_100 = {100};"
        assert bin_min_max.markdown() == "100"

        bin_min_max = bin_class(width=7, num=2)
        assert bin_min_max.type == bin_type
        assert bin_min_max.width == 7
        assert bin_min_max.num == 2
        assert bin_min_max.systemverilog() == "bins bin_0 = {0};\nbins bin_127 = {127};"
        assert bin_min_max.markdown() == "0, 127"

        bin_min_max = bin_class(-100, 100, num=3, name="TEST")
        assert bin_min_max.type == bin_type
        assert bin_min_max.width == 8
        assert bin_min_max.num == 3
        assert bin_min_max.systemverilog() == "bins TEST_min = {-100};\nbins TEST = {[-99:99]};\nbins TEST_max = {100};"
        assert bin_min_max.markdown() == "-100, [-99:99], 100"

        bin_min_max = bin_class(min=-100, width=8, num=5, prefix="TEST2")
        assert bin_min_max.type == bin_type
        assert bin_min_max.width == 8
        assert bin_min_max.num == 5
        assert (
            bin_min_max.systemverilog()
            == "bins TEST2_neg100 = {-100};\nbins TEST2_neg99_254[3] = {[-99:254]};\nbins TEST2_255 = {255};"
        )
        assert bin_min_max.markdown() == "-100, [-99:254]/3, 255"

        bin_min_max = bin_class(-321, 98, width=11, num=7, name="TEST3", prefix="TEST4")
        assert bin_min_max.type == bin_type
        assert bin_min_max.width == 11
        assert bin_min_max.num == 7
        assert (
            bin_min_max.systemverilog()
            == "bins TEST3_min = {-321};\nbins TEST3[5] = {[-320:97]};\nbins TEST3_max = {98};"
        )
        assert bin_min_max.markdown() == "-321, [-320:97]/5, 98"


def test_bin_min_max_exp():
    bin_min_max_exp = BinMinMaxExp(max=100)
    assert bin_min_max_exp.type == "MinMaxExp"
    assert bin_min_max_exp.width == 7
    assert bin_min_max_exp.num == 9
    assert (
        bin_min_max_exp.systemverilog()
        == "bins bin_0 = {0};\n"
        "bins bin_1 = {1};\n"
        "bins bin_2_3 = {[2:3]};\n"
        "bins bin_4_7 = {[4:7]};\n"
        "bins bin_8_15 = {[8:15]};\n"
        "bins bin_16_31 = {[16:31]};\n"
        "bins bin_32_63 = {[32:63]};\n"
        "bins bin_64_99 = {[64:99]};\n"
        "bins bin_100 = {100};"
    )
    assert bin_min_max_exp.markdown() == "0, 1, [2:3], ..., [64:99], 100"
    assert bin_min_max_exp.markdown(shorten=False) == "0, 1, [2:3], [4:7], [8:15], [16:31], [32:63], [64:99], 100"

    bin_min_max_exp = BinMinMaxExp(width=7, base=3)
    assert bin_min_max_exp.type == "MinMaxExp"
    assert bin_min_max_exp.width == 7
    assert bin_min_max_exp.num == 7
    assert (
        bin_min_max_exp.systemverilog()
        == "bins bin_0 = {0};\n"
        "bins bin_1_2 = {[1:2]};\n"
        "bins bin_3_8 = {[3:8]};\n"
        "bins bin_9_26 = {[9:26]};\n"
        "bins bin_27_80 = {[27:80]};\n"
        "bins bin_81_126 = {[81:126]};\n"
        "bins bin_127 = {127};"
    )
    assert bin_min_max_exp.markdown() == "0, [1:2], [3:8], ..., [81:126], 127"
    assert bin_min_max_exp.markdown(shorten=False) == "0, [1:2], [3:8], [9:26], [27:80], [81:126], 127"

    bin_min_max_exp = BinMinMaxExp(-100, 100, base=4, prefix="TEST")
    assert bin_min_max_exp.type == "MinMaxExp"
    assert bin_min_max_exp.width == 8
    assert bin_min_max_exp.num == 12
    assert (
        bin_min_max_exp.systemverilog()
        == "bins TEST_neg100 = {-100};\n"
        "bins TEST_neg99_neg65 = {[-99:-65]};\n"
        "bins TEST_neg64_neg17 = {[-64:-17]};\n"
        "bins TEST_neg16_neg5 = {[-16:-5]};\n"
        "bins TEST_neg4_neg2 = {[-4:-2]};\n"
        "bins TEST_neg1 = {-1};\n"
        "bins TEST_0 = {0};\n"
        "bins TEST_1_3 = {[1:3]};\n"
        "bins TEST_4_15 = {[4:15]};\n"
        "bins TEST_16_63 = {[16:63]};\n"
        "bins TEST_64_99 = {[64:99]};\n"
        "bins TEST_100 = {100};"
    )
    assert bin_min_max_exp.markdown() == "-100, [-99:-65], [-64:-17], ..., [64:99], 100"
    assert (
        bin_min_max_exp.markdown(shorten=False)
        == "-100, [-99:-65], [-64:-17], [-16:-5], [-4:-2], -1, 0, [1:3], [4:15], [16:63], [64:99], 100"
    )

    bin_min_max_exp = BinMinMaxExp(min=-100, width=8, base=5, prefix="TEST2")
    assert bin_min_max_exp.type == "MinMaxExp"
    assert bin_min_max_exp.width == 8
    assert bin_min_max_exp.num == 11
    assert (
        bin_min_max_exp.systemverilog()
        == "bins TEST2_neg100 = {-100};\n"
        "bins TEST2_neg99_neg26 = {[-99:-26]};\n"
        "bins TEST2_neg25_neg6 = {[-25:-6]};\n"
        "bins TEST2_neg5_neg2 = {[-5:-2]};\n"
        "bins TEST2_neg1 = {-1};\n"
        "bins TEST2_0 = {0};\n"
        "bins TEST2_1_4 = {[1:4]};\n"
        "bins TEST2_5_24 = {[5:24]};\n"
        "bins TEST2_25_124 = {[25:124]};\n"
        "bins TEST2_125_254 = {[125:254]};\n"
        "bins TEST2_255 = {255};"
    )
    assert bin_min_max_exp.markdown() == "-100, [-99:-26], [-25:-6], ..., [125:254], 255"
    assert (
        bin_min_max_exp.markdown(shorten=False)
        == "-100, [-99:-26], [-25:-6], [-5:-2], -1, 0, [1:4], [5:24], [25:124], [125:254], 255"
    )

    bin_min_max_exp = BinMinMaxExp(-321, 98, width=11, base=6, prefix="TEST3")
    assert bin_min_max_exp.type == "MinMaxExp"
    assert bin_min_max_exp.width == 11
    assert bin_min_max_exp.num == 11
    assert (
        bin_min_max_exp.systemverilog()
        == "bins TEST3_neg321 = {-321};\n"
        "bins TEST3_neg320_neg217 = {[-320:-217]};\n"
        "bins TEST3_neg216_neg37 = {[-216:-37]};\n"
        "bins TEST3_neg36_neg7 = {[-36:-7]};\n"
        "bins TEST3_neg6_neg2 = {[-6:-2]};\n"
        "bins TEST3_neg1 = {-1};\n"
        "bins TEST3_0 = {0};\n"
        "bins TEST3_1_5 = {[1:5]};\n"
        "bins TEST3_6_35 = {[6:35]};\n"
        "bins TEST3_36_97 = {[36:97]};\n"
        "bins TEST3_98 = {98};"
    )
    assert bin_min_max_exp.markdown() == "-321, [-320:-217], [-216:-37], ..., [36:97], 98"
    assert (
        bin_min_max_exp.markdown(shorten=False)
        == "-321, [-320:-217], [-216:-37], [-36:-7], [-6:-2], -1, 0, [1:5], [6:35], [36:97], 98"
    )


def test_bin_window():
    bin_window = BinWindow(window=0b1, width=5, format="b")
    assert bin_window.type == "Window"
    assert bin_window.width == 5
    assert bin_window.num == 5
    assert (
        bin_window.systemverilog()
        == "bins bin_0b1 = {'b1};\n"
        "bins bin_0b10 = {'b10};\n"
        "bins bin_0b100 = {'b100};\n"
        "bins bin_0b1000 = {'b1000};\n"
        "bins bin_0b10000 = {'b10000};"
    )
    assert bin_window.markdown() == "0b1, 0b10, 0b100, 0b1000, 0b10000"

    bin_window = BinWindow(window=0b11, width=9, prefix="TEST")
    assert bin_window.type == "Window"
    assert bin_window.width == 9
    assert bin_window.num == 5
    assert (
        bin_window.systemverilog()
        == "bins TEST_0x3 = {'h3};\n"
        "bins TEST_0xc = {'hc};\n"
        "bins TEST_0x30 = {'h30};\n"
        "bins TEST_0xc0 = {'hc0};\n"
        "bins TEST_0x100 = {'h100};"
    )
    assert bin_window.markdown() == "0x3, 0xc, 0x30, 0xc0, 0x100"

    bin_window = BinWindow(0b101, 10, shift=2, prefix="TEST2")
    assert bin_window.type == "Window"
    assert bin_window.width == 10
    assert bin_window.num == 5
    assert (
        bin_window.systemverilog()
        == "bins TEST2_0x5 = {'h5};\n"
        "bins TEST2_0x14 = {'h14};\n"
        "bins TEST2_0x50 = {'h50};\n"
        "bins TEST2_0x140 = {'h140};\n"
        "bins TEST2_0x100 = {'h100};"
    )
    assert bin_window.markdown() == "0x5, 0x14, 0x50, 0x140, 0x100"


def test_bin_onehot():
    bin_onehot = BinOneHot(4, format="b")
    assert bin_onehot.type == "OneHot"
    assert bin_onehot.width == 4
    assert bin_onehot.num == 4
    assert (
        bin_onehot.systemverilog()
        == "bins bin_0b1 = {'b1};\nbins bin_0b10 = {'b10};\nbins bin_0b100 = {'b100};\nbins bin_0b1000 = {'b1000};"
    )
    assert bin_onehot.markdown() == "0b1, 0b10, 0b100, 0b1000"

    bin_onehot = BinOneHot(5, format="o", prefix="TEST")
    assert bin_onehot.type == "OneHot"
    assert bin_onehot.width == 5
    assert bin_onehot.num == 5
    assert (
        bin_onehot.systemverilog()
        == "bins TEST_0o1 = {'o1};\n"
        "bins TEST_0o2 = {'o2};\n"
        "bins TEST_0o4 = {'o4};\n"
        "bins TEST_0o10 = {'o10};\n"
        "bins TEST_0o20 = {'o20};"
    )
    assert bin_onehot.markdown() == "0o1, 0o2, 0o4, 0o10, 0o20"

    bin_onehot = BinOneHot(6, prefix="TEST2")
    assert bin_onehot.type == "OneHot"
    assert bin_onehot.width == 6
    assert bin_onehot.num == 6
    assert (
        bin_onehot.systemverilog()
        == "bins TEST2_0x1 = {'h1};\n"
        "bins TEST2_0x2 = {'h2};\n"
        "bins TEST2_0x4 = {'h4};\n"
        "bins TEST2_0x8 = {'h8};\n"
        "bins TEST2_0x10 = {'h10};\n"
        "bins TEST2_0x20 = {'h20};"
    )
    assert bin_onehot.markdown() == "0x1, 0x2, 0x4, 0x8, 0x10, 0x20"


def test_bin_default():
    bin_default = BinDefault(4)
    assert bin_default.type == "Default"
    assert bin_default.width == 4
    assert bin_default.num == 1
    assert bin_default.systemverilog() == "bins others = default;"
    assert bin_default.markdown() == "default"

    bin_default = BinMinMax(max=100, num=5) + BinDefault()
    assert bin_default.type == "Custom"
    assert bin_default.width == 7
    assert bin_default.num == 6
    assert bin_default.systemverilog() == (
        "bins bin_0 = {0};\n" + "bins bin_1_99[3] = {[1:99]};\n" + "bins bin_100 = {100};\n" + "bins others = default;"
    )
    assert bin_default.markdown() == "0, [1:99]/3, 100, default"

    bin_default = BinDefault() + BinMinMax(max=100, num=5)
    assert bin_default.type == "Custom"
    assert bin_default.width == 7
    assert bin_default.num == 6
    assert bin_default.systemverilog() == (
        "bins bin_0 = {0};\n" + "bins bin_1_99[3] = {[1:99]};\n" + "bins bin_100 = {100};\n" + "bins others = default;"
    )
    assert bin_default.markdown() == "0, [1:99]/3, 100, default"

    bin_default = BinDefault() + BinMinMax(max=100, num=5) + BinDefault()
    assert bin_default.type == "Custom"
    assert bin_default.width == 7
    assert bin_default.num == 6
    assert bin_default.systemverilog() == (
        "bins bin_0 = {0};\n" + "bins bin_1_99[3] = {[1:99]};\n" + "bins bin_100 = {100};\n" + "bins others = default;"
    )
    assert bin_default.markdown() == "0, [1:99]/3, 100, default"


def test_bin_out_of_spec():
    bin_out_of_spec = BinOutOfSpec()
    assert bin_out_of_spec.type == "OutOfSpec"
    assert bin_out_of_spec.width == None
    assert bin_out_of_spec.num == 0
    assert bin_out_of_spec.systemverilog() == ""
    assert bin_out_of_spec.markdown() == "Out of spec"


def test_bin_bitwise():
    bin_bitwise = BinBitwise(4)
    assert bin_bitwise.type == "Bitwise"
    assert bin_bitwise.width == 4
    assert bin_bitwise.num == 8
    assert bin_bitwise.systemverilog() == ""
    assert bin_bitwise.markdown() == "0, 1 for each bit"


def test_bin_transition():
    bin_transition = BinTransition([1, 2, 3], (4, 5, 6), [[7, 8, 9], range(10, 20)])
    assert bin_transition.type == "Transition"
    assert bin_transition.width == 5
    assert bin_transition.num == 3
    assert (
        bin_transition.systemverilog()
        == "bins bin_1_3 = (1 => 2 => 3);\nbins bin_4_6 = (4 => 5 => 6);\nbins bin_7_19 = (7, 8, 9 => [10:19]);"
    )
    assert bin_transition.markdown() == "(1 => 2 => 3), (4 => 5 => 6), (7, 8, 9 => [10:19])"

    bin_transition = BinTransition(
        ([1, 2, 3], (4, 5, 6)), [[7, 8, 9, range(10, 20)], range(20, 40)], width=10, prefix="TEST", format="x"
    )
    assert bin_transition.type == "Transition"
    assert bin_transition.width == 10
    assert bin_transition.num == 2
    assert (
        bin_transition.systemverilog()
        == "bins TEST_0x1_0x6 = ('h1, 'h2, 'h3 => 'h4, 'h5, 'h6);\n"
        "bins TEST_0x7_0x27 = ('h7, 'h8, 'h9, ['ha:'h13] => ['h14:'h27]);"
    )
    assert bin_transition.markdown() == "(0x1, 0x2, 0x3 => 0x4, 0x5, 0x6), (0x7, 0x8, 0x9, [0xa:0x13] => [0x14:0x27])"

    with pytest.raises(AssertionError):
        bin_transition = BinTransition(1, 2, 3)
