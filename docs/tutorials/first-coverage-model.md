---
title: Your first coverage model
---
# Your first coverage model

> Walk-through for a contributor new to `cocotbext-fcov`: define one
> covergroup in Python, attach it to a `CoverageModel`, and emit a
> SystemVerilog `.sv` + Markdown `.md` pair via `make_coverage`.

<!-- KO mirror: see ko/tutorials/first-coverage-model.md -->

## TL;DR

| | |
|---|---|
| **Goal** | One `coverage_spec.py` + one generated `coverage.sv` + one generated `coverage.md`, end-to-end. |
| **Time** | 15 minutes. |
| **You'll need** | `pip install ./cocotbext-fcov` (editable install OK), Python 3.10+. |
| **Verified backing** | [`tests/pytest/test_coverage_model.py`](../../tests/pytest/test_coverage_model.py) |

## Setup

```bash
pip install -e .
```

Verify the CLI is on `PATH`:

```bash
make_coverage --help
```

## Step 1 — declare a covergroup

Create `coverage_spec.py` next to wherever you intend to keep the spec:

```python
from enum import Enum
from cocotbext.fcov import (
    CoverageModel, CoverGroup, CoverPoint, Cross,
    BinBool, BinRange, BinEnum,
)


class Opcode(Enum):
    READ  = 0
    WRITE = 1
    NOP   = 2


class TxnCoverGroup(CoverGroup):
    cp_opcode = CoverPoint(BinEnum(Opcode), format="b")
    cp_size   = CoverPoint(BinRange(8))           # bins bin_0_7[]
    cp_secure = CoverPoint(BinBool())
    cx_opcode_size = Cross([cp_opcode, cp_size])
```

Observable result: file exists. No error on import:

```bash
python -c "import coverage_spec; print('ok')"
```

## Step 2 — wrap it in a `CoverageModel`

Append to `coverage_spec.py`:

```python
class TxnCovModel(CoverageModel):
    cg_txn = TxnCoverGroup()


cov_model = TxnCovModel(name="cov_model")
```

The trailing instance is what `make_coverage` will find when it walks the module.

Observable result:

```bash
python -c "from coverage_spec import cov_model; print(cov_model.systemverilog()[:80])"
# module cov_model();
#   wire [1:0] cg_txn_cp_opcode;
#   ...
```

## Step 3 — emit `.sv` + `.md`

```bash
make_coverage -f coverage_spec.py -sv coverage.sv -md coverage.md --overwrite
```

Observable result: two new files appear.

```bash
head -3 coverage.sv
# `ifdef COCOTBEXT_FCOV
# module cov_model();
#   ...
head -3 coverage.md
# ## cov_model
#
# ### cg_txn
```

## What you just built

A single-file Python source-of-truth for one covergroup, with a generated SystemVerilog module ready to be included in the DUT and a Markdown spec doc ready to be reviewed by humans. Edits to `coverage_spec.py` re-flow through `make_coverage` into both outputs.

> Verified (sim-hit): [`tests/cocotb/simple_dff/`](../../tests/cocotb/simple_dff/) — same shape with a vendored cocotb D-FF DUT, ready to run on Verilator (sim-emit) / VCS / Questa (sim-hit).

## Next steps

- **For sampling the covergroup from a real cocotb test**: [how-to/sampling-in-cocotb.md](../how-to/sampling-in-cocotb.md).
- **For more bin shapes** (exp, min/max, transition, one-hot, ...): [reference/bins/type.md](../reference/bins/type.md) + [how-to/bin-type-recipes.md](../how-to/bin-type-recipes.md).
- **For cross-level ignore / illegal filters**: [how-to/cross-with-ignore-illegal.md](../how-to/cross-with-ignore-illegal.md).
- **For the `Bin*` inheritance map**: [explanations/bin-type-hierarchy.md](../explanations/bin-type-hierarchy.md).

## See also

- [reference/coverage/model.md](../reference/coverage/model.md) — `CoverageModel` API.
- [reference/scripts/make-coverage.md](../reference/scripts/make-coverage.md) — CLI flags.
- [tests/cocotb/simple_dff/](../../tests/cocotb/simple_dff/) — paired pilot (CC0-vendored DUT).
