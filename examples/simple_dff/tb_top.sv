// Toplevel wrapper: instantiates the vendored dff DUT alongside the
// cocotbext-fcov-emitted cov_model. cocotb drives clk + d from Python.

`timescale 1ns/1ps

module tb_top();
  logic clk;
  logic d;
  logic q;

  initial begin
    clk = 1'b0;
    d   = 1'b0;
  end

  dff dut (
    .clk(clk),
    .d  (d),
    .q  (q)
  );

  // Instance name matches model name (cocotbext-fcov dut.<model_name> lookup).
  cov_model cov_model();
endmodule
