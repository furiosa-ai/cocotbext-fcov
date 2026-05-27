// 4-bit up-counter with overflow flag.
// Self-authored for cocotbext-fcov pilots.

`timescale 1ns/1ps

module counter (
  input  logic       clk,
  input  logic       rst,
  input  logic       enable,
  output logic [3:0] value,
  output logic       overflow
);

  always_ff @(posedge clk or posedge rst) begin
    if (rst) begin
      value    <= 4'h0;
      overflow <= 1'b0;
    end else if (enable) begin
      if (value == 4'hF) begin
        value    <= 4'h0;
        overflow <= 1'b1;
      end else begin
        value    <= value + 4'h1;
        overflow <= 1'b0;
      end
    end else begin
      overflow <= 1'b0;
    end
  end

endmodule
