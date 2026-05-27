// Toplevel: vendored adder DUT + cocotbext-fcov-emitted cov_model.

`timescale 1ns/1ps

module tb_top();
  logic [3:0] A;
  logic [3:0] B;
  logic [4:0] X;

  initial begin
    A = 4'h0;
    B = 4'h0;
  end

  adder #(.DATA_WIDTH(4)) dut (
    .A(A),
    .B(B),
    .X(X)
  );

  // Instance name matches model name (dut.<model_name> lookup).
  cov_model cov_model();
endmodule
