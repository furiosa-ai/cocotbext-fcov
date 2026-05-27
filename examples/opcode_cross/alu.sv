// 4-bit ALU with four ops (ADD / SUB / AND / OR) + zero-result flag.
// Self-authored for cocotbext-fcov pilots.
//
// op encoding:
//   2'd0  ADD
//   2'd1  SUB
//   2'd2  AND
//   2'd3  OR

`timescale 1ns/1ps

module alu (
  input  logic        clk,
  input  logic        rst,
  input  logic [1:0]  op,
  input  logic [3:0]  a,
  input  logic [3:0]  b,
  output logic [3:0]  result,
  output logic        result_zero
);

  always_ff @(posedge clk) begin
    if (rst) begin
      result      <= 4'h0;
      result_zero <= 1'b1;
    end else begin
      case (op)
        2'd0: result <= a + b;       // ADD (low 4 bits)
        2'd1: result <= a - b;       // SUB (mod 16)
        2'd2: result <= a & b;       // AND
        2'd3: result <= a | b;       // OR
        default: result <= 4'h0;
      endcase
      result_zero <= (result == 4'h0);
    end
  end

endmodule
