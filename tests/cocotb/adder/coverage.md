## cov_model (AdderCovModel)

### Covergroup cg_adder

| Coverpoint   | Width   | Bin Type   |   # of Bins | Bins              | Ignore Bins   | Illegal Bins   |
|--------------|---------|------------|-------------|-------------------|---------------|----------------|
| cp_a         | [3:0]   | Uniform    |          16 | [0:15]/16         |               |                |
| cp_a_bitwise | [3:0]   | Bitwise    |           8 | 0, 1 for each bit |               |                |
| cp_b         | [3:0]   | Uniform    |          16 | [0:15]/16         |               |                |
| cp_carry     | [0:0]   | Bool       |           2 | FALSE(0), TRUE(1) |               |                |

| Cross      | Coverpoints    |   # of Bins |
|------------|----------------|-------------|
| cx_a_carry | cp_a, cp_carry |          32 |

