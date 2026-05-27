# simple_counter pilot — self-authored 4-bit up-counter.
# Paired guide: docs/how-to/build-coverage-hierarchy.md

PILOT_DIR := $(dir $(realpath $(firstword $(MAKEFILE_LIST))))

COCOTB_TOPLEVEL     = tb_top
COCOTB_TEST_MODULES = tb_counter

PILOT_DUT_SOURCES = $(PILOT_DIR)/counter.sv

include $(PILOT_DIR)/../_lib/Makefile.common
