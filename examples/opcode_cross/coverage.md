## cov_model (AluCovModel)

### Covergroup cg_alu

| Coverpoint     | Width   | Bin Type   |   # of Bins | Bins                          | Ignore Bins   | Illegal Bins   |
|----------------|---------|------------|-------------|-------------------------------|---------------|----------------|
| cp_a           | [3:0]   | Exp        |           5 | 0, 1, [2:3], [4:7], [8:15]    |               |                |
| cp_a_onehot    | [3:0]   | OneHot     |           4 | 0x1, 0x2, 0x4, 0x8            |               |                |
| cp_b           | [3:0]   | Exp        |           5 | 0, 1, [2:3], [4:7], [8:15]    |               |                |
| cp_op          | [1:0]   | Enum       |           4 | ADD(0), SUB(1), AND(2), OR(3) |               |                |
| cp_result_zero | [0:0]   | Bool       |           2 | FALSE(0), TRUE(1)             |               |                |

| Cross      | Coverpoints           |   # of Bins |
|------------|-----------------------|-------------|
| cx_op_zero | cp_op, cp_result_zero |           8 |

