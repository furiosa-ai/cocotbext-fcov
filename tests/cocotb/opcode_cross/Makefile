# opcode_cross pilot — self-authored 4-bit ALU.
# Paired guide: docs/how-to/cross-with-ignore-illegal.md

PILOT_DIR := $(dir $(realpath $(firstword $(MAKEFILE_LIST))))

COCOTB_TOPLEVEL     = tb_top
COCOTB_TEST_MODULES = tb_alu

PILOT_DUT_SOURCES = $(PILOT_DIR)/alu.sv

include $(PILOT_DIR)/../_lib/Makefile.common
