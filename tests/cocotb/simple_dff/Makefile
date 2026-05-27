# simple_dff pilot — cocotb upstream port (CC0).
#
# DUT: vendored cocotb examples/simple_dff/dff.sv (1-bit D-FF).
# Paired guide: docs/tutorials/first-coverage-model.md
#
# See ../README.md for run instructions (SIM=verilator|vcs|questa).

PILOT_DIR := $(dir $(realpath $(firstword $(MAKEFILE_LIST))))

COCOTB_TOPLEVEL     = tb_top
COCOTB_TEST_MODULES = tb_dff

PILOT_DUT_SOURCES = $(PILOT_DIR)/dff.sv

include $(PILOT_DIR)/../_lib/Makefile.common
