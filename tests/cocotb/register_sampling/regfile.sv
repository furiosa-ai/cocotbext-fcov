// 4-entry register file with read / write / no-op interface.
// Self-authored for cocotbext-fcov pilots.
//
// Encoding:
//   op       : 0 = NONE, 1 = READ, 2 = WRITE
//   addr     : 2-bit register select (R0..R3)
//   size     : 1 / 2 / 4 byte transfer width (informational; full word
//              transfer happens regardless to keep the DUT minimal)
//
// Reads return the previously-stored word on the next posedge.

`timescale 1ns/1ps

module regfile #(
  parameter integer ADDR_W = 2,
  parameter integer DATA_W = 32
)(
  input  logic                  clk,
  input  logic                  rst,
  input  logic [1:0]            op,
  input  logic [ADDR_W-1:0]     addr,
  input  logic [2:0]            size,
  input  logic [DATA_W-1:0]     wdata,
  output logic [DATA_W-1:0]     rdata
);

  logic [DATA_W-1:0] mem [(1 << ADDR_W)];

  always_ff @(posedge clk) begin
    if (rst) begin
      rdata <= '0;
      for (int i = 0; i < (1 << ADDR_W); i++) begin
        mem[i] <= '0;
      end
    end else begin
      if (op == 2'd2) begin       // WRITE
        mem[addr] <= wdata;
      end
      rdata <= mem[addr];          // read every cycle (NONE / READ / WRITE)
    end
  end

  // Suppress unused-net warnings on size (informational only in this DUT).
  wire _unused_size = &{1'b0, size};

endmodule
