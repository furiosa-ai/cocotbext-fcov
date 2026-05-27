# matrix_multiplier pilot — cocotb upstream port (CC0).
#
# DUT: vendored cocotb examples/matrix_multiplier/hdl/matrix_multiplier.sv,
# parameter-overridden to a 2x2 × 2x2 case (4-bit elements) for tractable
# coverage closure.
#
# Paired guide: docs/how-to/bin-type-recipes.md

PILOT_DIR := $(dir $(realpath $(firstword $(MAKEFILE_LIST))))

COCOTB_TOPLEVEL     = tb_top
COCOTB_TEST_MODULES = tb_mm

PILOT_DUT_SOURCES = $(PILOT_DIR)/matrix_multiplier.sv

include $(PILOT_DIR)/../_lib/Makefile.common
