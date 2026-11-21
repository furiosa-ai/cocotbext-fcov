import copy

from cocotbext.fcov import CoverPoint, Cross, CoverGroup
from cocotbext.fcov import (
    BinSingle,
    BinUniform,
    BinOneHot,
    BinBitwise,
    BinBool,
    BinRange,
)


def assertion_check(inst: CoverGroup):
    name = inst.name
    wire = (
        f"wire {name}_cp_single_list_0;\n"
        f"wire [3:0] {name}_cp_single_list_1;\n"
        f"wire [4:0] {name}_cp_single_list_2;\n"
        f"wire [4:0] {name}_cp_single_list_3;\n"
        f"wire [5:0] {name}_cp_single_list_4;\n"
        f"wire signed [7:0] {name}_cp_uniform;\n"
        f"wire [3:0] {name}_cp_uniform_list_0;\n"
        f"wire [3:0] {name}_cp_uniform_list_1;\n"
        f"wire [3:0] {name}_cp_uniform_list_2;\n"
        f"wire [3:0] {name}_cp_width;\n"
        f"wire {name}_sample;"
    )
    declare = (
        f"covergroup {name};\n"
        f"cp_bitwise_0: coverpoint {name}_cp_width[0];\n"
        f"cp_bitwise_1: coverpoint {name}_cp_width[1];\n"
        f"cp_bitwise_2: coverpoint {name}_cp_width[2];\n"
        f"cp_bitwise_3: coverpoint {name}_cp_width[3];\n"
        f"cp_onehot: coverpoint {name}_cp_width {{\n"
        "bins bin_0x1 = {'h1};\n"
        "bins bin_0x2 = {'h2};\n"
        "bins bin_0x4 = {'h4};\n"
        "bins bin_0x8 = {'h8};}\n"
        f"cp_single_list_0: coverpoint {name}_cp_single_list_0 {{\n"
        "bins bin_0 = {0};}\n"
        f"cp_single_list_1: coverpoint {name}_cp_single_list_1 {{\n"
        "bins bin_10 = {10};}\n"
        f"cp_single_list_2: coverpoint {name}_cp_single_list_2 {{\n"
        "bins bin_20 = {20};}\n"
        f"cp_single_list_3: coverpoint {name}_cp_single_list_3 {{\n"
        "bins bin_30 = {30};}\n"
        f"cp_single_list_4: coverpoint {name}_cp_single_list_4 {{\n"
        "bins bin_40 = {40};}\n"
        f"cp_uniform: coverpoint {name}_cp_uniform {{\n"
        "bins bin_neg100_99[4] = {[-100:99]} with (item % 5 == 0);}\n"
        f"cp_uniform_list_0: coverpoint {name}_cp_uniform_list_0 {{\n"
        "bins bin_0_9[] = {[0:9]};}\n"
        f"cp_uniform_list_1: coverpoint {name}_cp_uniform_list_1 {{\n"
        "bins bin_0_9[] = {[0:9]};}\n"
        f"cp_uniform_list_2: coverpoint {name}_cp_uniform_list_2 {{\n"
        "bins bin_0_9[] = {[0:9]};}\n"
        f"cp_width: coverpoint {name}_cp_width {{\n"
        "bins bin_0_15[] = {[0:15]};}\n"
        "cx_onehot_bitwise_0: cross cp_onehot, cp_bitwise_0;\n"
        "cx_onehot_bitwise_1: cross cp_onehot, cp_bitwise_1;\n"
        "cx_onehot_bitwise_2: cross cp_onehot, cp_bitwise_2;\n"
        "cx_onehot_bitwise_3: cross cp_onehot, cp_bitwise_3;\n"
        f"endgroup : {name}"
    )
    instance = f"{name} {name}_inst = new;"
    sample_event = f"always@ ({name}_sample) begin {name}_inst.sample(); end"
    assert (
        str(inst)
        == f"CoverGroup(name={name}, "
        # fmt: off
        f"cp_bitwise=CoverPoint(bins=(), ignore_bins=(), illegal_bins=(), width=None, name=cp_bitwise, group={name}, ref=cp_width), "
        f"cp_onehot=CoverPoint(bins=(0x1, 0x2, 0x4, 0x8), ignore_bins=(), illegal_bins=(), width=None, name=cp_onehot, group={name}, ref=cp_width), "
        f"cp_single_list_0=CoverPoint(bins=(0), ignore_bins=(), illegal_bins=(), width=None, name=cp_single_list_0, group={name}, ref=None), "
        f"cp_single_list_1=CoverPoint(bins=(10), ignore_bins=(), illegal_bins=(), width=None, name=cp_single_list_1, group={name}, ref=None), "
        f"cp_single_list_2=CoverPoint(bins=(20), ignore_bins=(), illegal_bins=(), width=None, name=cp_single_list_2, group={name}, ref=None), "
        f"cp_single_list_3=CoverPoint(bins=(30), ignore_bins=(), illegal_bins=(), width=None, name=cp_single_list_3, group={name}, ref=None), "
        f"cp_single_list_4=CoverPoint(bins=(40), ignore_bins=(), illegal_bins=(), width=None, name=cp_single_list_4, group={name}, ref=None), "
        f"cp_uniform=CoverPoint(bins=((-100, -95, -90, ..., 90, 95)), ignore_bins=(), illegal_bins=(), width=None, name=cp_uniform, group={name}, ref=None), "
        f"cp_uniform_list_0=CoverPoint(bins=([0:9]), ignore_bins=(), illegal_bins=(), width=None, name=cp_uniform_list_0, group={name}, ref=None), "
        f"cp_uniform_list_1=CoverPoint(bins=([0:9]), ignore_bins=(), illegal_bins=(), width=None, name=cp_uniform_list_1, group={name}, ref=None), "
        f"cp_uniform_list_2=CoverPoint(bins=([0:9]), ignore_bins=(), illegal_bins=(), width=None, name=cp_uniform_list_2, group={name}, ref=None), "
        f"cp_width=CoverPoint(bins=([0:15]), ignore_bins=(), illegal_bins=(), width=None, name=cp_width, group={name}, ref=None), "
        f"cx_onehot_bitwise=Cross(coverpoints=(cp_onehot, cp_bitwise), name=cx_onehot_bitwise, group={name}))"
        # fmt: on
    )
    assert inst.sv_wire() == wire
    assert inst.sv_declare() == declare
    assert inst.sv_instance() == instance
    assert inst.sv_sample_event() == sample_event
    assert inst.systemverilog() == "\n\n".join([wire, declare, instance, sample_event]) + "\n"
    assert (
        inst.markdown()
        == f"### Covergroup {name}\n\n"
        # fmt: off
        "| Coverpoint            | Width   | Bin Type   |   # of Bins | Bins                            | Ignore Bins   | Illegal Bins   |\n"
        "|-----------------------|---------|------------|-------------|---------------------------------|---------------|----------------|\n"
        "| cp_bitwise            | [3:0]   | Bitwise    |           8 | 0, 1 for each bit               |               |                |\n"
        "| cp_onehot             | [3:0]   | OneHot     |           4 | 0x1, 0x2, 0x4, 0x8              |               |                |\n"
        "| cp_single_list_0      | [0:0]   | Single     |           1 | 0                               |               |                |\n"
        "| cp_single_list_1      | [3:0]   | Single     |           1 | 10                              |               |                |\n"
        "| cp_single_list_2      | [4:0]   | Single     |           1 | 20                              |               |                |\n"
        "| cp_single_list_3      | [4:0]   | Single     |           1 | 30                              |               |                |\n"
        "| cp_single_list_4      | [5:0]   | Single     |           1 | 40                              |               |                |\n"
        "| cp_uniform            | [7:0]   | Uniform    |           4 | {-100, -95, -90, ..., 90, 95}/4 |               |                |\n"
        "| cp_uniform_list_{0-2} | [3:0]   | Uniform    |          10 | [0:9]/10                        |               |                |\n"
        "| cp_width              | [3:0]   | Uniform    |          16 | [0:15]/16                       |               |                |\n\n"
        "| Cross             | Coverpoints           |   # of Bins |\n"
        "|-------------------|-----------------------|-------------|\n"
        "| cx_onehot_bitwise | cp_onehot, cp_bitwise |          32 |\n\n"
        # fmt: on
    )


def test_class_new(width=4):
    class CoverGroupTest(CoverGroup):
        cp_uniform = CoverPoint(BinUniform(-100, 100, 5, num=4))
        cp_width = CoverPoint(BinUniform(width=width))
        cp_onehot = CoverPoint(BinOneHot(width), ref=cp_width)
        cp_bitwise = CoverPoint(BinBitwise(width), ref=cp_width)
        cp_single_list = [CoverPoint(BinSingle(i)) for i in range(0, 50, 10)]
        cp_uniform_list = [CoverPoint(BinUniform(10)) for _ in range(3)]

        cx_onehot_bitwise = Cross([cp_onehot, cp_bitwise])

    cg_test1 = CoverGroupTest(name="cg_test1")
    cg_test2 = CoverGroupTest()
    cg_test2.set_name("cg_test2")
    assertion_check(cg_test1)
    assertion_check(cg_test2)
    assert cg_test1.cp_onehot.signal == "cg_test1_cp_width"
    assert cg_test2.cp_onehot.signal == "cg_test2_cp_width"


def test_class_init(width=4):
    class CoverGroupTest(CoverGroup):
        def __init__(self, width, name=None):
            self.cp_uniform = CoverPoint(BinUniform(-100, 100, 5, num=4))
            self.cp_width = CoverPoint(BinUniform(width=width))
            self.cp_onehot = CoverPoint(BinOneHot(width), ref=self.cp_width)
            self.cp_bitwise = CoverPoint(BinBitwise(width), ref=self.cp_width)
            self.cp_single_list = [CoverPoint(BinSingle(i)) for i in range(0, 50, 10)]
            self.cp_uniform_list = [CoverPoint(BinUniform(10)) for _ in range(3)]

            self.cx_onehot_bitwise = Cross([self.cp_onehot, self.cp_bitwise])

            super().__init__(name=name)

    cg_test1 = CoverGroupTest(width=width, name="cg_test1")
    cg_test2 = CoverGroupTest(width=width)
    cg_test2.set_name("cg_test2")
    assertion_check(cg_test1)
    assertion_check(cg_test2)
    assert cg_test1.cp_onehot.signal == "cg_test1_cp_width"
    assert cg_test2.cp_onehot.signal == "cg_test2_cp_width"


def test_inheritance(width=4):
    class CoverGroupTestBase1(CoverGroup):
        cp_uniform = CoverPoint(BinUniform(-100, 100, 5, num=4))
        cp_width = CoverPoint(BinUniform(width=width))
        cp_onehot = CoverPoint(BinOneHot(width), ref=cp_width)

    class CoverGroupTestBase2(CoverGroup):
        def __init__(self):
            self.cp_uniform = CoverPoint(BinUniform(-100, 100, 5, num=4))
            self.cp_width = CoverPoint(BinUniform(width=width))
            self.cp_onehot = CoverPoint(BinOneHot(width), ref=self.cp_width)

    class CoverGroupTest1(CoverGroupTestBase1):
        cp_bitwise = CoverPoint(BinBitwise(width), ref=CoverGroupTestBase1.cp_width)
        cp_single_list = [CoverPoint(BinSingle(i)) for i in range(0, 50, 10)]
        cp_uniform_list = [CoverPoint(BinUniform(10)) for _ in range(3)]

        cx_onehot_bitwise = Cross([CoverGroupTestBase1.cp_onehot, cp_bitwise])

    class CoverGroupTest2(CoverGroupTestBase1):
        def __init__(self):
            super().__init__()
            self.cp_bitwise = CoverPoint(BinBitwise(width), ref=self.cp_width)
            self.cp_single_list = [CoverPoint(BinSingle(i)) for i in range(0, 50, 10)]
            self.cp_uniform_list = [CoverPoint(BinUniform(10)) for _ in range(3)]

            self.cx_onehot_bitwise = Cross([self.cp_onehot, self.cp_bitwise])

    class CoverGroupTest3(CoverGroupTestBase2):
        def __init__(self):
            super().__init__()
            self.cp_bitwise = CoverPoint(BinBitwise(width), ref=self.cp_width)
            self.cp_single_list = [CoverPoint(BinSingle(i)) for i in range(0, 50, 10)]
            self.cp_uniform_list = [CoverPoint(BinUniform(10)) for _ in range(3)]

            self.cx_onehot_bitwise = Cross([self.cp_onehot, self.cp_bitwise])

    cg_test1 = CoverGroupTest1()
    cg_test2 = CoverGroupTest2()
    cg_test3 = CoverGroupTest3()
    cg_test1.set_name("cg_test1")
    cg_test2.set_name("cg_test2")
    cg_test3.set_name("cg_test3")
    assertion_check(cg_test1)
    assertion_check(cg_test2)
    assertion_check(cg_test3)
    assert cg_test1.cp_onehot.signal == "cg_test1_cp_width"
    assert cg_test2.cp_onehot.signal == "cg_test2_cp_width"
    assert cg_test3.cp_onehot.signal == "cg_test3_cp_width"

    assert cg_test1 == cg_test2
    assert cg_test1 == cg_test3
    assert cg_test2 == cg_test2


# ---------------------------------------------------------------------------
# Deepcopy regression for Cross.ignore_bins / illegal_bins clause cp refs
# (commit 769533f -- _remap_clauses inside CoverGroup._copy_coverpoints)
# Single-instance test would accidentally pass because the class-level cp
# name eventually gets set by the last instance's set_name. The TWO
# instances + identity checks are what actually pin the per-__new__ remap.
# ---------------------------------------------------------------------------


def test_covergroup_deepcopy_remaps_cross_clause_cp_refs():
    class CrossClauseCG(CoverGroup):
        cp_op = CoverPoint(BinRange(4))
        cp_z = CoverPoint(BinBool())
        cx = Cross(
            [cp_op, cp_z],
            ignore_bins=[{"name": "ig", "terms": [(cp_op, 2), (cp_z, 1)]}],
            illegal_bins=[{"name": "il", "terms": [(cp_op, 3, True)]}],
        )

    cg1 = CrossClauseCG(name="cg_test1")
    cg2 = CrossClauseCG(name="cg_test2")

    # Each instance's clause refs must be the *instance's own* cp copies,
    # not the class-level originals and not the other instance's copies.
    ig1_cp_op = cg1.cx.ignore_bins[0]["terms"][0][0]
    ig1_cp_z = cg1.cx.ignore_bins[0]["terms"][1][0]
    il1_cp_op = cg1.cx.illegal_bins[0]["terms"][0][0]
    assert ig1_cp_op is cg1.cp_op
    assert ig1_cp_z is cg1.cp_z
    assert il1_cp_op is cg1.cp_op
    assert ig1_cp_op is not CrossClauseCG.cp_op
    assert ig1_cp_op is not cg2.cp_op

    ig2_cp_op = cg2.cx.ignore_bins[0]["terms"][0][0]
    assert ig2_cp_op is cg2.cp_op
    assert ig2_cp_op is not cg1.cp_op

    # Clause dicts themselves are per-instance copies -- mutating cg1's
    # clause must not leak into cg2.
    assert cg1.cx.ignore_bins[0] is not cg2.cx.ignore_bins[0]
    cg1.cx.ignore_bins[0]["name"] = "ig_mutated"
    assert cg2.cx.ignore_bins[0]["name"] == "ig"

    # SV emit on each instance carries the instance's group-prefixed cp
    # names and never `binsof(None)` (the failure signature pre-769533f).
    sv1 = cg1.cx.sv_declare()
    sv2 = cg2.cx.sv_declare()
    assert "binsof(None)" not in sv1
    assert "binsof(None)" not in sv2
    assert "ignore_bins ig_mutated = " in sv1
    assert "ignore_bins ig = " in sv2

    # copy.deepcopy(cg) path (used by CoverageModel for repeated instances)
    # also remaps -- distinct CG.__deepcopy__ entry point at coverage.py:602.
    cg3 = copy.deepcopy(cg2)
    cg3.set_name("cg_test3")
    ig3_cp_op = cg3.cx.ignore_bins[0]["terms"][0][0]
    assert ig3_cp_op is cg3.cp_op
    assert ig3_cp_op is not cg2.cp_op
    assert "binsof(None)" not in cg3.cx.sv_declare()
