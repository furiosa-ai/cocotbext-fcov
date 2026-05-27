# register_sampling pilot — self-authored 4-entry register file.
# Paired guide: docs/how-to/wire-into-testbench.md

PILOT_DIR := $(dir $(realpath $(firstword $(MAKEFILE_LIST))))

COCOTB_TOPLEVEL     = tb_top
COCOTB_TEST_MODULES = tb_regfile

PILOT_DUT_SOURCES = $(PILOT_DIR)/regfile.sv

include $(PILOT_DIR)/../_lib/Makefile.common
