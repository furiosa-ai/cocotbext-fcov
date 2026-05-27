`ifdef FUNC_COV
`endif
`ifdef COCOTBEXT_FCOV
module cov_model ();
  wire cg_dff_cp_q;
  wire cg_dff_sample;

  covergroup cg_dff;
    cp_q: coverpoint cg_dff_cp_q {bins FALSE = {0}; bins TRUE = {1};}
    cp_q_trans: coverpoint cg_dff_cp_q {bins up = (0 => 1); bins down = (1 => 0);}
  endgroup : cg_dff

  cg_dff cg_dff_inst = new;

  always @(cg_dff_sample) begin
    cg_dff_inst.sample();
  end
endmodule
`endif
