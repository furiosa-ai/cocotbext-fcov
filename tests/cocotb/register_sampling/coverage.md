## cov_model (RegfileCovModel)

### Covergroup cg_regfile

| Coverpoint   | Width   | Bin Type   |   # of Bins | Bins                       | Ignore Bins   | Illegal Bins   |
|--------------|---------|------------|-------------|----------------------------|---------------|----------------|
| cp_addr      | [1:0]   | Dict       |           4 | R0(0), R1(1), R2(2), R3(3) |               |                |
| cp_data      | [5:0]   | Custom     |          65 | [0:63]/64, default         |               |                |
| cp_op        | [1:0]   | Enum       |           3 | NONE(0), READ(1), WRITE(2) |               |                |
| cp_op_trans  | [1:0]   | Custom     |           2 | (1 => 2), (2 => 1)         |               |                |
| cp_size      | [2:0]   | Custom     |           3 | 1, 2, 4                    |               |                |

| Cross      | Coverpoints    |   # of Bins |
|------------|----------------|-------------|
| cx_op_addr | cp_op, cp_addr |          12 |

