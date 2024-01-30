module cov_model ();
wire cg_list_0_cp_single_list_0;
wire [3:0] cg_list_0_cp_single_list_1;
wire [4:0] cg_list_0_cp_single_list_2;
wire [3:0] cg_list_0_cp_uniform_list_0;
wire [3:0] cg_list_0_cp_uniform_list_1;
wire [3:0] cg_list_0_cp_uniform_list_2;
wire [3:0] cg_list_0_cp_width;
wire cg_list_0_sample;

covergroup cg_list_0;
cp_bitwise_0: coverpoint cg_list_0_cp_width[0];
cp_bitwise_1: coverpoint cg_list_0_cp_width[1];
cp_bitwise_2: coverpoint cg_list_0_cp_width[2];
cp_bitwise_3: coverpoint cg_list_0_cp_width[3];
cp_onehot: coverpoint cg_list_0_cp_width {
bins bin_0x1 = {'h1};
bins bin_0x2 = {'h2};
bins bin_0x4 = {'h4};
bins bin_0x8 = {'h8};}
cp_single_list_0: coverpoint cg_list_0_cp_single_list_0 {
bins bin_0 = {0};}
cp_single_list_1: coverpoint cg_list_0_cp_single_list_1 {
bins bin_10 = {10};}
cp_single_list_2: coverpoint cg_list_0_cp_single_list_2 {
bins bin_20 = {20};}
cp_uniform_list_0: coverpoint cg_list_0_cp_uniform_list_0 {
bins bin_0_9[] = {[0:9]};}
cp_uniform_list_1: coverpoint cg_list_0_cp_uniform_list_1 {
bins bin_0_9[] = {[0:9]};}
cp_uniform_list_2: coverpoint cg_list_0_cp_uniform_list_2 {
bins bin_0_9[] = {[0:9]};}
cp_width: coverpoint cg_list_0_cp_width {
bins bin_0_15[] = {[0:15]};}
cx_onehot_bitwise_0: cross cp_onehot, cp_bitwise_0;
cx_onehot_bitwise_1: cross cp_onehot, cp_bitwise_1;
cx_onehot_bitwise_2: cross cp_onehot, cp_bitwise_2;
cx_onehot_bitwise_3: cross cp_onehot, cp_bitwise_3;
endgroup : cg_list_0

cg_list_0 cg_list_0_inst = new;

always@ (cg_list_0_sample) begin cg_list_0_inst.sample(); end

wire cg_list_1_cp_single_list_0;
wire [3:0] cg_list_1_cp_single_list_1;
wire [4:0] cg_list_1_cp_single_list_2;
wire [3:0] cg_list_1_cp_uniform_list_0;
wire [3:0] cg_list_1_cp_uniform_list_1;
wire [3:0] cg_list_1_cp_uniform_list_2;
wire [4:0] cg_list_1_cp_width;
wire cg_list_1_sample;

covergroup cg_list_1;
cp_bitwise_0: coverpoint cg_list_1_cp_width[0];
cp_bitwise_1: coverpoint cg_list_1_cp_width[1];
cp_bitwise_2: coverpoint cg_list_1_cp_width[2];
cp_bitwise_3: coverpoint cg_list_1_cp_width[3];
cp_bitwise_4: coverpoint cg_list_1_cp_width[4];
cp_onehot: coverpoint cg_list_1_cp_width {
bins bin_0x1 = {'h1};
bins bin_0x2 = {'h2};
bins bin_0x4 = {'h4};
bins bin_0x8 = {'h8};
bins bin_0x10 = {'h10};}
cp_single_list_0: coverpoint cg_list_1_cp_single_list_0 {
bins bin_0 = {0};}
cp_single_list_1: coverpoint cg_list_1_cp_single_list_1 {
bins bin_10 = {10};}
cp_single_list_2: coverpoint cg_list_1_cp_single_list_2 {
bins bin_20 = {20};}
cp_uniform_list_0: coverpoint cg_list_1_cp_uniform_list_0 {
bins bin_0_9[] = {[0:9]};}
cp_uniform_list_1: coverpoint cg_list_1_cp_uniform_list_1 {
bins bin_0_9[] = {[0:9]};}
cp_uniform_list_2: coverpoint cg_list_1_cp_uniform_list_2 {
bins bin_0_9[] = {[0:9]};}
cp_width: coverpoint cg_list_1_cp_width {
bins bin_0_31[] = {[0:31]};}
cx_onehot_bitwise_0: cross cp_onehot, cp_bitwise_0;
cx_onehot_bitwise_1: cross cp_onehot, cp_bitwise_1;
cx_onehot_bitwise_2: cross cp_onehot, cp_bitwise_2;
cx_onehot_bitwise_3: cross cp_onehot, cp_bitwise_3;
cx_onehot_bitwise_4: cross cp_onehot, cp_bitwise_4;
endgroup : cg_list_1

cg_list_1 cg_list_1_inst = new;

always@ (cg_list_1_sample) begin cg_list_1_inst.sample(); end

wire cg_list_2_cp_single_list_0;
wire [3:0] cg_list_2_cp_single_list_1;
wire [4:0] cg_list_2_cp_single_list_2;
wire [3:0] cg_list_2_cp_uniform_list_0;
wire [3:0] cg_list_2_cp_uniform_list_1;
wire [3:0] cg_list_2_cp_uniform_list_2;
wire [4:0] cg_list_2_cp_width;
wire cg_list_2_sample;

covergroup cg_list_2;
cp_bitwise_0: coverpoint cg_list_2_cp_width[0];
cp_bitwise_1: coverpoint cg_list_2_cp_width[1];
cp_bitwise_2: coverpoint cg_list_2_cp_width[2];
cp_bitwise_3: coverpoint cg_list_2_cp_width[3];
cp_bitwise_4: coverpoint cg_list_2_cp_width[4];
cp_onehot: coverpoint cg_list_2_cp_width {
bins bin_0x1 = {'h1};
bins bin_0x2 = {'h2};
bins bin_0x4 = {'h4};
bins bin_0x8 = {'h8};
bins bin_0x10 = {'h10};}
cp_single_list_0: coverpoint cg_list_2_cp_single_list_0 {
bins bin_0 = {0};}
cp_single_list_1: coverpoint cg_list_2_cp_single_list_1 {
bins bin_10 = {10};}
cp_single_list_2: coverpoint cg_list_2_cp_single_list_2 {
bins bin_20 = {20};}
cp_uniform_list_0: coverpoint cg_list_2_cp_uniform_list_0 {
bins bin_0_9[] = {[0:9]};}
cp_uniform_list_1: coverpoint cg_list_2_cp_uniform_list_1 {
bins bin_0_9[] = {[0:9]};}
cp_uniform_list_2: coverpoint cg_list_2_cp_uniform_list_2 {
bins bin_0_9[] = {[0:9]};}
cp_width: coverpoint cg_list_2_cp_width {
bins bin_0_31[] = {[0:31]};}
cx_onehot_bitwise_0: cross cp_onehot, cp_bitwise_0;
cx_onehot_bitwise_1: cross cp_onehot, cp_bitwise_1;
cx_onehot_bitwise_2: cross cp_onehot, cp_bitwise_2;
cx_onehot_bitwise_3: cross cp_onehot, cp_bitwise_3;
cx_onehot_bitwise_4: cross cp_onehot, cp_bitwise_4;
endgroup : cg_list_2

cg_list_2 cg_list_2_inst = new;

always@ (cg_list_2_sample) begin cg_list_2_inst.sample(); end

wire cg_list_3_cp_single_list_0;
wire [3:0] cg_list_3_cp_single_list_1;
wire [4:0] cg_list_3_cp_single_list_2;
wire [3:0] cg_list_3_cp_uniform_list_0;
wire [3:0] cg_list_3_cp_uniform_list_1;
wire [3:0] cg_list_3_cp_uniform_list_2;
wire [3:0] cg_list_3_cp_width;
wire cg_list_3_sample;

covergroup cg_list_3;
cp_bitwise_0: coverpoint cg_list_3_cp_width[0];
cp_bitwise_1: coverpoint cg_list_3_cp_width[1];
cp_bitwise_2: coverpoint cg_list_3_cp_width[2];
cp_bitwise_3: coverpoint cg_list_3_cp_width[3];
cp_onehot: coverpoint cg_list_3_cp_width {
bins bin_0x1 = {'h1};
bins bin_0x2 = {'h2};
bins bin_0x4 = {'h4};
bins bin_0x8 = {'h8};}
cp_single_list_0: coverpoint cg_list_3_cp_single_list_0 {
bins bin_0 = {0};}
cp_single_list_1: coverpoint cg_list_3_cp_single_list_1 {
bins bin_10 = {10};}
cp_single_list_2: coverpoint cg_list_3_cp_single_list_2 {
bins bin_20 = {20};}
cp_uniform_list_0: coverpoint cg_list_3_cp_uniform_list_0 {
bins bin_0_9[] = {[0:9]};}
cp_uniform_list_1: coverpoint cg_list_3_cp_uniform_list_1 {
bins bin_0_9[] = {[0:9]};}
cp_uniform_list_2: coverpoint cg_list_3_cp_uniform_list_2 {
bins bin_0_9[] = {[0:9]};}
cp_width: coverpoint cg_list_3_cp_width {
bins bin_0_15[] = {[0:15]};}
cx_onehot_bitwise_0: cross cp_onehot, cp_bitwise_0;
cx_onehot_bitwise_1: cross cp_onehot, cp_bitwise_1;
cx_onehot_bitwise_2: cross cp_onehot, cp_bitwise_2;
cx_onehot_bitwise_3: cross cp_onehot, cp_bitwise_3;
endgroup : cg_list_3

cg_list_3 cg_list_3_inst = new;

always@ (cg_list_3_sample) begin cg_list_3_inst.sample(); end

wire cg_list_4_cp_single_list_0;
wire [3:0] cg_list_4_cp_single_list_1;
wire [4:0] cg_list_4_cp_single_list_2;
wire [3:0] cg_list_4_cp_uniform_list_0;
wire [3:0] cg_list_4_cp_uniform_list_1;
wire [3:0] cg_list_4_cp_uniform_list_2;
wire [5:0] cg_list_4_cp_width;
wire cg_list_4_sample;

covergroup cg_list_4;
cp_bitwise_0: coverpoint cg_list_4_cp_width[0];
cp_bitwise_1: coverpoint cg_list_4_cp_width[1];
cp_bitwise_2: coverpoint cg_list_4_cp_width[2];
cp_bitwise_3: coverpoint cg_list_4_cp_width[3];
cp_bitwise_4: coverpoint cg_list_4_cp_width[4];
cp_bitwise_5: coverpoint cg_list_4_cp_width[5];
cp_onehot: coverpoint cg_list_4_cp_width {
bins bin_0x1 = {'h1};
bins bin_0x2 = {'h2};
bins bin_0x4 = {'h4};
bins bin_0x8 = {'h8};
bins bin_0x10 = {'h10};
bins bin_0x20 = {'h20};}
cp_single_list_0: coverpoint cg_list_4_cp_single_list_0 {
bins bin_0 = {0};}
cp_single_list_1: coverpoint cg_list_4_cp_single_list_1 {
bins bin_10 = {10};}
cp_single_list_2: coverpoint cg_list_4_cp_single_list_2 {
bins bin_20 = {20};}
cp_uniform_list_0: coverpoint cg_list_4_cp_uniform_list_0 {
bins bin_0_9[] = {[0:9]};}
cp_uniform_list_1: coverpoint cg_list_4_cp_uniform_list_1 {
bins bin_0_9[] = {[0:9]};}
cp_uniform_list_2: coverpoint cg_list_4_cp_uniform_list_2 {
bins bin_0_9[] = {[0:9]};}
cp_width: coverpoint cg_list_4_cp_width {
bins bin_0_63[] = {[0:63]};}
cx_onehot_bitwise_0: cross cp_onehot, cp_bitwise_0;
cx_onehot_bitwise_1: cross cp_onehot, cp_bitwise_1;
cx_onehot_bitwise_2: cross cp_onehot, cp_bitwise_2;
cx_onehot_bitwise_3: cross cp_onehot, cp_bitwise_3;
cx_onehot_bitwise_4: cross cp_onehot, cp_bitwise_4;
cx_onehot_bitwise_5: cross cp_onehot, cp_bitwise_5;
endgroup : cg_list_4

cg_list_4 cg_list_4_inst = new;

always@ (cg_list_4_sample) begin cg_list_4_inst.sample(); end

wire cg_repeat_0_cp_single_list_0;
wire [3:0] cg_repeat_0_cp_single_list_1;
wire [4:0] cg_repeat_0_cp_single_list_2;
wire [3:0] cg_repeat_0_cp_uniform_list_0;
wire [3:0] cg_repeat_0_cp_uniform_list_1;
wire [3:0] cg_repeat_0_cp_uniform_list_2;
wire [3:0] cg_repeat_0_cp_width;
wire cg_repeat_0_sample;

covergroup cg_repeat_0;
cp_bitwise_0: coverpoint cg_repeat_0_cp_width[0];
cp_bitwise_1: coverpoint cg_repeat_0_cp_width[1];
cp_bitwise_2: coverpoint cg_repeat_0_cp_width[2];
cp_bitwise_3: coverpoint cg_repeat_0_cp_width[3];
cp_onehot: coverpoint cg_repeat_0_cp_width {
bins bin_0x1 = {'h1};
bins bin_0x2 = {'h2};
bins bin_0x4 = {'h4};
bins bin_0x8 = {'h8};}
cp_single_list_0: coverpoint cg_repeat_0_cp_single_list_0 {
bins bin_0 = {0};}
cp_single_list_1: coverpoint cg_repeat_0_cp_single_list_1 {
bins bin_10 = {10};}
cp_single_list_2: coverpoint cg_repeat_0_cp_single_list_2 {
bins bin_20 = {20};}
cp_uniform_list_0: coverpoint cg_repeat_0_cp_uniform_list_0 {
bins bin_0_9[] = {[0:9]};}
cp_uniform_list_1: coverpoint cg_repeat_0_cp_uniform_list_1 {
bins bin_0_9[] = {[0:9]};}
cp_uniform_list_2: coverpoint cg_repeat_0_cp_uniform_list_2 {
bins bin_0_9[] = {[0:9]};}
cp_width: coverpoint cg_repeat_0_cp_width {
bins bin_0_15[] = {[0:15]};}
cx_onehot_bitwise_0: cross cp_onehot, cp_bitwise_0;
cx_onehot_bitwise_1: cross cp_onehot, cp_bitwise_1;
cx_onehot_bitwise_2: cross cp_onehot, cp_bitwise_2;
cx_onehot_bitwise_3: cross cp_onehot, cp_bitwise_3;
endgroup : cg_repeat_0

cg_repeat_0 cg_repeat_0_inst = new;

always@ (cg_repeat_0_sample) begin cg_repeat_0_inst.sample(); end

wire cg_repeat_1_cp_single_list_0;
wire [3:0] cg_repeat_1_cp_single_list_1;
wire [4:0] cg_repeat_1_cp_single_list_2;
wire [3:0] cg_repeat_1_cp_uniform_list_0;
wire [3:0] cg_repeat_1_cp_uniform_list_1;
wire [3:0] cg_repeat_1_cp_uniform_list_2;
wire [3:0] cg_repeat_1_cp_width;
wire cg_repeat_1_sample;

covergroup cg_repeat_1;
cp_bitwise_0: coverpoint cg_repeat_1_cp_width[0];
cp_bitwise_1: coverpoint cg_repeat_1_cp_width[1];
cp_bitwise_2: coverpoint cg_repeat_1_cp_width[2];
cp_bitwise_3: coverpoint cg_repeat_1_cp_width[3];
cp_onehot: coverpoint cg_repeat_1_cp_width {
bins bin_0x1 = {'h1};
bins bin_0x2 = {'h2};
bins bin_0x4 = {'h4};
bins bin_0x8 = {'h8};}
cp_single_list_0: coverpoint cg_repeat_1_cp_single_list_0 {
bins bin_0 = {0};}
cp_single_list_1: coverpoint cg_repeat_1_cp_single_list_1 {
bins bin_10 = {10};}
cp_single_list_2: coverpoint cg_repeat_1_cp_single_list_2 {
bins bin_20 = {20};}
cp_uniform_list_0: coverpoint cg_repeat_1_cp_uniform_list_0 {
bins bin_0_9[] = {[0:9]};}
cp_uniform_list_1: coverpoint cg_repeat_1_cp_uniform_list_1 {
bins bin_0_9[] = {[0:9]};}
cp_uniform_list_2: coverpoint cg_repeat_1_cp_uniform_list_2 {
bins bin_0_9[] = {[0:9]};}
cp_width: coverpoint cg_repeat_1_cp_width {
bins bin_0_15[] = {[0:15]};}
cx_onehot_bitwise_0: cross cp_onehot, cp_bitwise_0;
cx_onehot_bitwise_1: cross cp_onehot, cp_bitwise_1;
cx_onehot_bitwise_2: cross cp_onehot, cp_bitwise_2;
cx_onehot_bitwise_3: cross cp_onehot, cp_bitwise_3;
endgroup : cg_repeat_1

cg_repeat_1 cg_repeat_1_inst = new;

always@ (cg_repeat_1_sample) begin cg_repeat_1_inst.sample(); end

wire cg_repeat_2_cp_single_list_0;
wire [3:0] cg_repeat_2_cp_single_list_1;
wire [4:0] cg_repeat_2_cp_single_list_2;
wire [3:0] cg_repeat_2_cp_uniform_list_0;
wire [3:0] cg_repeat_2_cp_uniform_list_1;
wire [3:0] cg_repeat_2_cp_uniform_list_2;
wire [3:0] cg_repeat_2_cp_width;
wire cg_repeat_2_sample;

covergroup cg_repeat_2;
cp_bitwise_0: coverpoint cg_repeat_2_cp_width[0];
cp_bitwise_1: coverpoint cg_repeat_2_cp_width[1];
cp_bitwise_2: coverpoint cg_repeat_2_cp_width[2];
cp_bitwise_3: coverpoint cg_repeat_2_cp_width[3];
cp_onehot: coverpoint cg_repeat_2_cp_width {
bins bin_0x1 = {'h1};
bins bin_0x2 = {'h2};
bins bin_0x4 = {'h4};
bins bin_0x8 = {'h8};}
cp_single_list_0: coverpoint cg_repeat_2_cp_single_list_0 {
bins bin_0 = {0};}
cp_single_list_1: coverpoint cg_repeat_2_cp_single_list_1 {
bins bin_10 = {10};}
cp_single_list_2: coverpoint cg_repeat_2_cp_single_list_2 {
bins bin_20 = {20};}
cp_uniform_list_0: coverpoint cg_repeat_2_cp_uniform_list_0 {
bins bin_0_9[] = {[0:9]};}
cp_uniform_list_1: coverpoint cg_repeat_2_cp_uniform_list_1 {
bins bin_0_9[] = {[0:9]};}
cp_uniform_list_2: coverpoint cg_repeat_2_cp_uniform_list_2 {
bins bin_0_9[] = {[0:9]};}
cp_width: coverpoint cg_repeat_2_cp_width {
bins bin_0_15[] = {[0:15]};}
cx_onehot_bitwise_0: cross cp_onehot, cp_bitwise_0;
cx_onehot_bitwise_1: cross cp_onehot, cp_bitwise_1;
cx_onehot_bitwise_2: cross cp_onehot, cp_bitwise_2;
cx_onehot_bitwise_3: cross cp_onehot, cp_bitwise_3;
endgroup : cg_repeat_2

cg_repeat_2 cg_repeat_2_inst = new;

always@ (cg_repeat_2_sample) begin cg_repeat_2_inst.sample(); end

wire cg_single_cp_single_list_0;
wire [3:0] cg_single_cp_single_list_1;
wire [4:0] cg_single_cp_single_list_2;
wire [3:0] cg_single_cp_uniform_list_0;
wire [3:0] cg_single_cp_uniform_list_1;
wire [3:0] cg_single_cp_uniform_list_2;
wire [3:0] cg_single_cp_width;
wire cg_single_sample;

covergroup cg_single;
cp_bitwise_0: coverpoint cg_single_cp_width[0];
cp_bitwise_1: coverpoint cg_single_cp_width[1];
cp_bitwise_2: coverpoint cg_single_cp_width[2];
cp_bitwise_3: coverpoint cg_single_cp_width[3];
cp_onehot: coverpoint cg_single_cp_width {
bins bin_0x1 = {'h1};
bins bin_0x2 = {'h2};
bins bin_0x4 = {'h4};
bins bin_0x8 = {'h8};}
cp_single_list_0: coverpoint cg_single_cp_single_list_0 {
bins bin_0 = {0};}
cp_single_list_1: coverpoint cg_single_cp_single_list_1 {
bins bin_10 = {10};}
cp_single_list_2: coverpoint cg_single_cp_single_list_2 {
bins bin_20 = {20};}
cp_uniform_list_0: coverpoint cg_single_cp_uniform_list_0 {
bins bin_0_9[] = {[0:9]};}
cp_uniform_list_1: coverpoint cg_single_cp_uniform_list_1 {
bins bin_0_9[] = {[0:9]};}
cp_uniform_list_2: coverpoint cg_single_cp_uniform_list_2 {
bins bin_0_9[] = {[0:9]};}
cp_width: coverpoint cg_single_cp_width {
bins bin_0_15[] = {[0:15]};}
cx_onehot_bitwise_0: cross cp_onehot, cp_bitwise_0;
cx_onehot_bitwise_1: cross cp_onehot, cp_bitwise_1;
cx_onehot_bitwise_2: cross cp_onehot, cp_bitwise_2;
cx_onehot_bitwise_3: cross cp_onehot, cp_bitwise_3;
endgroup : cg_single

cg_single cg_single_inst = new;

always@ (cg_single_sample) begin cg_single_inst.sample(); end
endmodule
