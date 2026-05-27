// Toplevel: regfile DUT + cocotbext-fcov-emitted cov_model.

`timescale 1ns/1ps

module tb_top();
  logic        clk;
  logic        rst;
  logic [1:0]  op;
  logic [1:0]  addr;
  logic [2:0]  size;
  logic [31:0] wdata;
  logic [31:0] rdata;

  initial begin
    clk   = 1'b0;
    rst   = 1'b0;
    op    = 2'd0;
    addr  = 2'd0;
    size  = 3'd1;
    wdata = 32'h0;
  end

  regfile #(.ADDR_W(2), .DATA_W(32)) dut (
    .clk   (clk),
    .rst   (rst),
    .op    (op),
    .addr  (addr),
    .size  (size),
    .wdata (wdata),
    .rdata (rdata)
  );

  cov_model cov_model();
endmodule
