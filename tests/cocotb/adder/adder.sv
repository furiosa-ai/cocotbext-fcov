// This file is public domain, it can be freely copied without restrictions.
// SPDX-License-Identifier: CC0-1.0
//
// Vendored verbatim from cocotb upstream:
//   https://github.com/cocotb/cocotb/blob/master/examples/adder/hdl/adder.sv
// No modifications. The cocotbext-fcov pilot wraps this in tb_top.sv and
// drives coverage for the sampling-in-cocotb how-to. See ../../NOTICE.md.

// Adder DUT
`timescale 1ns/1ps

module adder #(
  parameter integer DATA_WIDTH = 4
) (
  input  logic unsigned [DATA_WIDTH-1:0] A,
  input  logic unsigned [DATA_WIDTH-1:0] B,
  output logic unsigned [DATA_WIDTH:0]   X
);

  assign X = A + B;

endmodule
