`ifdef FUNC_COV
`endif
`ifdef COCOTBEXT_FCOV
module cov_model ();
  wire [3:0] cg_alu_cp_a;
  wire [3:0] cg_alu_cp_b;
  wire [1:0] cg_alu_cp_op;
  wire cg_alu_cp_result_zero;
  wire cg_alu_sample;

  covergroup cg_alu;
    cp_a: coverpoint cg_alu_cp_a {
      bins bin_0 = {0};
      bins bin_1 = {1};
      bins bin_2_3 = {[2 : 3]};
      bins bin_4_7 = {[4 : 7]};
      bins bin_8_15 = {[8 : 15]};
    }
    cp_a_onehot: coverpoint cg_alu_cp_a {
      bins bin_0x1 = {'h1}; bins bin_0x2 = {'h2}; bins bin_0x4 = {'h4}; bins bin_0x8 = {'h8};
    }
    cp_b: coverpoint cg_alu_cp_b {
      bins bin_0 = {0};
      bins bin_1 = {1};
      bins bin_2_3 = {[2 : 3]};
      bins bin_4_7 = {[4 : 7]};
      bins bin_8_15 = {[8 : 15]};
    }
    cp_op: coverpoint cg_alu_cp_op {bins ADD = {0}; bins SUB = {1}; bins AND = {2}; bins OR = {3};}
    cp_result_zero: coverpoint cg_alu_cp_result_zero {bins FALSE = {0}; bins TRUE = {1};}
    cx_op_zero: cross cp_op, cp_result_zero{
      ignore_bins ig_and_zero = binsof (cp_op) intersect {2} && binsof (cp_result_zero) intersect {
        1
      };
      illegal_bins il_or_zero = binsof (cp_op) intersect {3} && binsof (cp_result_zero) intersect {
        1
      };
    }
  endgroup : cg_alu

  cg_alu cg_alu_inst = new;

  `ifndef VERILATOR
  always @(cg_alu_sample) begin
    cg_alu_inst.sample();
  end
  `endif
endmodule
`endif
