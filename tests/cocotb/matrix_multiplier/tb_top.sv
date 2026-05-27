// Toplevel: parameter-overridden 2x2 x 2x2 matrix_multiplier + cov_model.
//
// Pilot parameters: A is 2x2, B is 2x2, elements 4-bit. Result C is
// 2x2 with C_DATA_WIDTH = 2*4 + clog2(2) = 9 bits, max value 2*15*15 = 450.

`timescale 1ns/1ps

module tb_top();
  localparam int DATA_W   = 4;
  localparam int A_ROWS   = 2;
  localparam int B_COLS   = 2;
  localparam int A_COLS_B_ROWS = 2;
  localparam int C_DATA_W = (2 * DATA_W) + 1;  // = 9 for 2x2

  logic clk;
  logic reset;
  logic valid_i;
  logic valid_o;
  logic [DATA_W-1:0]   a_i [0:A_ROWS*A_COLS_B_ROWS-1];   // 4 elements
  logic [DATA_W-1:0]   b_i [0:A_COLS_B_ROWS*B_COLS-1];   // 4 elements
  logic [C_DATA_W-1:0] c_o [0:A_ROWS*B_COLS-1];          // 4 elements

  initial begin
    clk     = 1'b0;
    reset   = 1'b0;
    valid_i = 1'b0;
    for (int i = 0; i < A_ROWS*A_COLS_B_ROWS; i++) a_i[i] = '0;
    for (int i = 0; i < A_COLS_B_ROWS*B_COLS; i++) b_i[i] = '0;
  end

  matrix_multiplier #(
    .DATA_WIDTH       (DATA_W),
    .A_ROWS           (A_ROWS),
    .B_COLUMNS        (B_COLS),
    .A_COLUMNS_B_ROWS (A_COLS_B_ROWS)
  ) dut (
    .clk_i   (clk),
    .reset_i (reset),
    .valid_i (valid_i),
    .valid_o (valid_o),
    .a_i     (a_i),
    .b_i     (b_i),
    .c_o     (c_o)
  );

  cov_model cov_model();
endmodule
