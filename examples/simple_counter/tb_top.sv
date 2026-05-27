// Toplevel: vendored counter DUT + cocotbext-fcov-emitted cov_model.

`timescale 1ns/1ps

module tb_top();
  logic       clk;
  logic       rst;
  logic       enable;
  logic [3:0] value;
  logic       overflow;

  initial begin
    clk    = 1'b0;
    rst    = 1'b0;
    enable = 1'b0;
  end

  counter dut (
    .clk     (clk),
    .rst     (rst),
    .enable  (enable),
    .value   (value),
    .overflow(overflow)
  );

  // Instance name matches model name (dut.<model_name> lookup).
  cov_model cov_model();
endmodule
