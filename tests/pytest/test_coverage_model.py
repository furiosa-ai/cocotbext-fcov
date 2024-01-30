from cocotbext.fcov import CoverageModel
from cocotbext.fcov import CoverPoint, Cross, CoverGroup
from cocotbext.fcov import (
    BinSingle,
    BinUniform,
    BinOneHot,
    BinBitwise,
)


def test_coverage_model():
    class CoverGroupTest(CoverGroup):
        width = 4
        cp_width = CoverPoint(BinUniform(width=width))
        cp_onehot = CoverPoint(BinOneHot(width), ref=cp_width)
        cp_bitwise = CoverPoint(BinBitwise(width), ref=cp_width)
        cp_single_list = [CoverPoint(BinSingle(i)) for i in range(0, 30, 10)]
        cp_uniform_list = [CoverPoint(BinUniform(10)) for _ in range(3)]

        cx_onehot_bitwise = Cross([cp_onehot, cp_bitwise])

    class CoverGroupTest2(CoverGroup):
        def __init__(self, width):
            self.cp_width = CoverPoint(BinUniform(width=width))
            self.cp_onehot = CoverPoint(BinOneHot(width), ref=self.cp_width)
            self.cp_bitwise = CoverPoint(BinBitwise(width), ref=self.cp_width)
            self.cp_single_list = [CoverPoint(BinSingle(i)) for i in range(0, 30, 10)]
            self.cp_uniform_list = [CoverPoint(BinUniform(10)) for _ in range(3)]

            self.cx_onehot_bitwise = Cross([self.cp_onehot, self.cp_bitwise])

    class TestCoverage(CoverageModel):
        cg_single = CoverGroupTest()
        cg_repeat = [CoverGroupTest() for _ in range(3)]
        cg_list = [CoverGroupTest(), CoverGroupTest2(5), CoverGroupTest2(5), CoverGroupTest2(4), CoverGroupTest2(6)]

    cov_model = TestCoverage("cov_model")
    with open("test_coverage_model.sv", "r") as f:
        assert cov_model.systemverilog() == f.read()
    with open("test_coverage_model.md", "r") as f:
        assert cov_model.markdown() == f.read()

    class TestCoverage2(CoverageModel):
        cg_single = CoverGroupTest2(4)
        cg_repeat = [CoverGroupTest2(4) for _ in range(3)]
        cg_list = [CoverGroupTest2(4), CoverGroupTest2(5), CoverGroupTest2(5), CoverGroupTest2(4), CoverGroupTest2(6)]

    cov_model_2 = TestCoverage2()
    assert cov_model == cov_model_2
