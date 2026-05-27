`ifdef FUNC_COV
`endif
`ifdef COCOTBEXT_FCOV
module cov_model ();
  wire [3:0] cg_adder_cp_a;
  wire [3:0] cg_adder_cp_b;
  wire cg_adder_cp_carry;
  wire cg_adder_sample;

  covergroup cg_adder;
    cp_a: coverpoint cg_adder_cp_a {bins bin_0_15[] = {[0 : 15]};}
    cp_a_bitwise_0: coverpoint cg_adder_cp_a[0];
    cp_a_bitwise_1: coverpoint cg_adder_cp_a[1];
    cp_a_bitwise_2: coverpoint cg_adder_cp_a[2];
    cp_a_bitwise_3: coverpoint cg_adder_cp_a[3];
    cp_b: coverpoint cg_adder_cp_b {bins bin_0_15[] = {[0 : 15]};}
    cp_carry: coverpoint cg_adder_cp_carry {bins FALSE = {0}; bins TRUE = {1};}
    cx_a_carry: cross cp_a, cp_carry;
  endgroup : cg_adder

  cg_adder cg_adder_inst = new;

  always @(cg_adder_sample) begin
    cg_adder_inst.sample();
  end
endmodule
`endif
