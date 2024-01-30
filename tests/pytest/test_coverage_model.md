## cov_model (TestCoverage)

### Covergroup cg_list_{0, 3}

| Coverpoint            | Width   | Bin Type   |   # of Bins | Bins               | Ignore Bins   | Illegal Bins   |
|-----------------------|---------|------------|-------------|--------------------|---------------|----------------|
| cp_bitwise            | [3:0]   | Bitwise    |           8 | 0, 1 for each bit  |               |                |
| cp_onehot             | [3:0]   | OneHot     |           4 | 0x1, 0x2, 0x4, 0x8 |               |                |
| cp_single_list_0      | [0:0]   | Single     |           1 | 0                  |               |                |
| cp_single_list_1      | [3:0]   | Single     |           1 | 10                 |               |                |
| cp_single_list_2      | [4:0]   | Single     |           1 | 20                 |               |                |
| cp_uniform_list_{0-2} | [3:0]   | Uniform    |          10 | [0:9]/10           |               |                |
| cp_width              | [3:0]   | Uniform    |          16 | [0:15]/16          |               |                |

| Cross             | Coverpoints           |   # of Bins |
|-------------------|-----------------------|-------------|
| cx_onehot_bitwise | cp_onehot, cp_bitwise |          32 |

### Covergroup cg_list_{1-2}

| Coverpoint            | Width   | Bin Type   |   # of Bins | Bins                     | Ignore Bins   | Illegal Bins   |
|-----------------------|---------|------------|-------------|--------------------------|---------------|----------------|
| cp_bitwise            | [4:0]   | Bitwise    |          10 | 0, 1 for each bit        |               |                |
| cp_onehot             | [4:0]   | OneHot     |           5 | 0x1, 0x2, 0x4, 0x8, 0x10 |               |                |
| cp_single_list_0      | [0:0]   | Single     |           1 | 0                        |               |                |
| cp_single_list_1      | [3:0]   | Single     |           1 | 10                       |               |                |
| cp_single_list_2      | [4:0]   | Single     |           1 | 20                       |               |                |
| cp_uniform_list_{0-2} | [3:0]   | Uniform    |          10 | [0:9]/10                 |               |                |
| cp_width              | [4:0]   | Uniform    |          32 | [0:31]/32                |               |                |

| Cross             | Coverpoints           |   # of Bins |
|-------------------|-----------------------|-------------|
| cx_onehot_bitwise | cp_onehot, cp_bitwise |          50 |

### Covergroup cg_list_4

| Coverpoint            | Width   | Bin Type   |   # of Bins | Bins                           | Ignore Bins   | Illegal Bins   |
|-----------------------|---------|------------|-------------|--------------------------------|---------------|----------------|
| cp_bitwise            | [5:0]   | Bitwise    |          12 | 0, 1 for each bit              |               |                |
| cp_onehot             | [5:0]   | OneHot     |           6 | 0x1, 0x2, 0x4, 0x8, 0x10, 0x20 |               |                |
| cp_single_list_0      | [0:0]   | Single     |           1 | 0                              |               |                |
| cp_single_list_1      | [3:0]   | Single     |           1 | 10                             |               |                |
| cp_single_list_2      | [4:0]   | Single     |           1 | 20                             |               |                |
| cp_uniform_list_{0-2} | [3:0]   | Uniform    |          10 | [0:9]/10                       |               |                |
| cp_width              | [5:0]   | Uniform    |          64 | [0:63]/64                      |               |                |

| Cross             | Coverpoints           |   # of Bins |
|-------------------|-----------------------|-------------|
| cx_onehot_bitwise | cp_onehot, cp_bitwise |          72 |

### Covergroup cg_repeat_{0-2}

| Coverpoint            | Width   | Bin Type   |   # of Bins | Bins               | Ignore Bins   | Illegal Bins   |
|-----------------------|---------|------------|-------------|--------------------|---------------|----------------|
| cp_bitwise            | [3:0]   | Bitwise    |           8 | 0, 1 for each bit  |               |                |
| cp_onehot             | [3:0]   | OneHot     |           4 | 0x1, 0x2, 0x4, 0x8 |               |                |
| cp_single_list_0      | [0:0]   | Single     |           1 | 0                  |               |                |
| cp_single_list_1      | [3:0]   | Single     |           1 | 10                 |               |                |
| cp_single_list_2      | [4:0]   | Single     |           1 | 20                 |               |                |
| cp_uniform_list_{0-2} | [3:0]   | Uniform    |          10 | [0:9]/10           |               |                |
| cp_width              | [3:0]   | Uniform    |          16 | [0:15]/16          |               |                |

| Cross             | Coverpoints           |   # of Bins |
|-------------------|-----------------------|-------------|
| cx_onehot_bitwise | cp_onehot, cp_bitwise |          32 |

### Covergroup cg_single

| Coverpoint            | Width   | Bin Type   |   # of Bins | Bins               | Ignore Bins   | Illegal Bins   |
|-----------------------|---------|------------|-------------|--------------------|---------------|----------------|
| cp_bitwise            | [3:0]   | Bitwise    |           8 | 0, 1 for each bit  |               |                |
| cp_onehot             | [3:0]   | OneHot     |           4 | 0x1, 0x2, 0x4, 0x8 |               |                |
| cp_single_list_0      | [0:0]   | Single     |           1 | 0                  |               |                |
| cp_single_list_1      | [3:0]   | Single     |           1 | 10                 |               |                |
| cp_single_list_2      | [4:0]   | Single     |           1 | 20                 |               |                |
| cp_uniform_list_{0-2} | [3:0]   | Uniform    |          10 | [0:9]/10           |               |                |
| cp_width              | [3:0]   | Uniform    |          16 | [0:15]/16          |               |                |

| Cross             | Coverpoints           |   # of Bins |
|-------------------|-----------------------|-------------|
| cx_onehot_bitwise | cp_onehot, cp_bitwise |          32 |

