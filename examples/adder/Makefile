# adder pilot — cocotb upstream port (CC0).
#
# DUT: vendored cocotb examples/adder/hdl/adder.sv (4-bit unsigned adder).
# Paired guide: docs/how-to/sampling-in-cocotb.md
#
# See ../README.md for run instructions (SIM=verilator|vcs|questa).

PILOT_DIR := $(dir $(realpath $(firstword $(MAKEFILE_LIST))))

COCOTB_TOPLEVEL     = tb_top
COCOTB_TEST_MODULES = tb_adder

PILOT_DUT_SOURCES = $(PILOT_DIR)/adder.sv

include $(PILOT_DIR)/../_lib/Makefile.common
