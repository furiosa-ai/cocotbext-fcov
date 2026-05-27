// This file is public domain, it can be freely copied without restrictions.
// SPDX-License-Identifier: CC0-1.0
//
// Vendored verbatim from cocotb upstream:
//   https://github.com/cocotb/cocotb/blob/master/examples/simple_dff/dff.sv
// No modifications. The cocotbext-fcov pilot wraps this in tb_top.sv and uses
// it as the DUT for the first-coverage-model tutorial. See ../../NOTICE.md.

`timescale 1us/1us

module dff (
  input logic clk, d,
  output logic q
);

always @(posedge clk) begin
  q <= d;
end

endmodule
