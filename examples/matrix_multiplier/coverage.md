## cov_model (MatmulCovModel)

### Covergroup cg_matmul

| Coverpoint   | Width   | Bin Type   |   # of Bins | Bins                             | Ignore Bins   | Illegal Bins   |
|--------------|---------|------------|-------------|----------------------------------|---------------|----------------|
| cp_a0        | [3:0]   | Custom     |           8 | [0:3]/4, 4, [5:7], [8:14], 15    |               |                |
| cp_b0        | [3:0]   | Custom     |           8 | [0:3]/4, 4, [5:7], [8:14], 15    |               |                |
| cp_c0        | [8:0]   | MinMax     |           5 | 0, [1:449]/3, 450                |               |                |
| cp_c0_mmexp  | [8:0]   | MinMaxExp  |          11 | 0, 1, [2:3], ..., [256:449], 450 |               |                |
| cp_valid_o   | [0:0]   | Bool       |           2 | FALSE(0), TRUE(1)                |               |                |

| Cross    | Coverpoints   |   # of Bins |
|----------|---------------|-------------|
| cx_a0_b0 | cp_a0, cp_b0  |          64 |

