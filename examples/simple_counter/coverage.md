## cov_model (CounterCovModel)

### Covergroup cg_counter

| Coverpoint   | Width   | Bin Type   |   # of Bins | Bins              | Ignore Bins   | Illegal Bins   |
|--------------|---------|------------|-------------|-------------------|---------------|----------------|
| cp_overflow  | [0:0]   | Bool       |           2 | FALSE(0), TRUE(1) |               |                |
| cp_value     | [3:0]   | Range      |          16 | [0:15]/16         |               |                |

| Cross      | Coverpoints           |   # of Bins |
|------------|-----------------------|-------------|
| cx_val_ovf | cp_value, cp_overflow |          32 |

