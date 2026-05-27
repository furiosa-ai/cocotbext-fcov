`ifdef FUNC_COV
`endif
`ifdef COCOTBEXT_FCOV
module cov_model ();
  wire [3:0] cg_matmul_cp_a0;
  wire [3:0] cg_matmul_cp_b0;
  wire [8:0] cg_matmul_cp_c0;
  wire cg_matmul_cp_valid_o;
  wire cg_matmul_sample;

  covergroup cg_matmul;
    cp_a0: coverpoint cg_matmul_cp_a0 {
      bins bin_0_3[4] = {[0 : 3]};
      bins bin_4 = {4};
      bins bin_5_7 = {[5 : 7]};
      bins bin_8_14 = {[8 : 14]};
      bins bin_15 = {15};
    }
    cp_b0: coverpoint cg_matmul_cp_b0 {
      bins bin_0_3[4] = {[0 : 3]};
      bins bin_4 = {4};
      bins bin_5_7 = {[5 : 7]};
      bins bin_8_14 = {[8 : 14]};
      bins bin_15 = {15};
    }
    cp_c0: coverpoint cg_matmul_cp_c0 {
      bins bin_0 = {0}; bins bin_1_449[3] = {[1 : 449]}; bins bin_450 = {450};
    }
    cp_c0_mmexp: coverpoint cg_matmul_cp_c0 {
      bins bin_0 = {0};
      bins bin_1 = {1};
      bins bin_2_3 = {[2 : 3]};
      bins bin_4_7 = {[4 : 7]};
      bins bin_8_15 = {[8 : 15]};
      bins bin_16_31 = {[16 : 31]};
      bins bin_32_63 = {[32 : 63]};
      bins bin_64_127 = {[64 : 127]};
      bins bin_128_255 = {[128 : 255]};
      bins bin_256_449 = {[256 : 449]};
      bins bin_450 = {450};
    }
    cp_valid_o: coverpoint cg_matmul_cp_valid_o {bins FALSE = {0}; bins TRUE = {1};}
    cx_a0_b0: cross cp_a0, cp_b0;
  endgroup : cg_matmul

  cg_matmul cg_matmul_inst = new;

  `ifndef VERILATOR
  always @(cg_matmul_sample) begin
    cg_matmul_inst.sample();
  end
  `endif
endmodule
`endif
