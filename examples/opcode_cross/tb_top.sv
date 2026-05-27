// Toplevel: ALU DUT + cocotbext-fcov-emitted cov_model.

`timescale 1ns/1ps

module tb_top();
  logic       clk;
  logic       rst;
  logic [1:0] op;
  logic [3:0] a;
  logic [3:0] b;
  logic [3:0] result;
  logic       result_zero;

  initial begin
    clk = 1'b0;
    rst = 1'b0;
    op  = 2'd0;
    a   = 4'h0;
    b   = 4'h0;
  end

  alu dut (
    .clk         (clk),
    .rst         (rst),
    .op          (op),
    .a           (a),
    .b           (b),
    .result      (result),
    .result_zero (result_zero)
  );

  cov_model cov_model();
endmodule
