`ifdef FUNC_COV
`endif
`ifdef COCOTBEXT_FCOV
module cov_model ();
  wire [1:0] cg_regfile_cp_addr;
  wire [5:0] cg_regfile_cp_data;
  wire [1:0] cg_regfile_cp_op;
  wire [2:0] cg_regfile_cp_size;
  wire cg_regfile_sample;

  covergroup cg_regfile;
    cp_addr: coverpoint cg_regfile_cp_addr {
      bins R0 = {0}; bins R1 = {1}; bins R2 = {2}; bins R3 = {3};
    }
    cp_data: coverpoint cg_regfile_cp_data {bins bin_0_63[64] = {[0 : 63]}; bins others = default;}
    cp_op: coverpoint cg_regfile_cp_op {bins NONE = {0}; bins READ = {1}; bins WRITE = {2};}
    cp_op_trans: coverpoint cg_regfile_cp_op {
      bins write_after_read = (1 => 2); bins read_after_write = (2 => 1);
    }
    cp_size: coverpoint cg_regfile_cp_size {
      bins size_1 = {1}; bins size_2 = {2}; bins size_4 = {4};
    }
    cx_op_addr: cross cp_op, cp_addr;
  endgroup : cg_regfile

  cg_regfile cg_regfile_inst = new;

  `ifndef VERILATOR
  always @(cg_regfile_sample) begin
    cg_regfile_inst.sample();
  end
  `endif
endmodule
`endif
