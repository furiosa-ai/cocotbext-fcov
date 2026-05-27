`ifdef FUNC_COV
`endif
`ifdef COCOTBEXT_FCOV
module cov_model ();
  wire cg_counter_cp_overflow;
  wire [3:0] cg_counter_cp_value;
  wire cg_counter_sample;

  covergroup cg_counter;
    cp_overflow: coverpoint cg_counter_cp_overflow {bins FALSE = {0}; bins TRUE = {1};}
    cp_value: coverpoint cg_counter_cp_value {bins bin_0_15[] = {[0 : 15]};}
    cx_val_ovf: cross cp_value, cp_overflow;
  endgroup : cg_counter

  cg_counter cg_counter_inst = new;

  always @(cg_counter_sample) begin
    cg_counter_inst.sample();
  end
endmodule
`endif
