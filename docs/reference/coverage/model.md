---
title: CoverageModel + CoverageCollector
component_type: coverage_model
layer: coverage
src_path: cocotbext/fcov/coverage.py
src_symbols: [CoverageModel, CoverageCollector, compact_index, traverse_type, get_markdown_list]
related_guides: [sampling-in-cocotb]
---
# CoverageModel + CoverageCollector

> Top-level container that bundles [`CoverGroup`](covergroup.md)s into a single SystemVerilog module; the collector binds it to a live cocotb DUT.

## TL;DR

| | |
|---|---|
| **What** | `CoverageModel` is the package-level wrapper that emits one SV module containing every covergroup; `CoverageCollector` is the runtime glue that connects a model to a DUT handle. |
| **When to use** | Always — one model per spec file; one collector per test. |
| **Key links** | [covergroup.md](covergroup.md) · [../scripts/make-coverage.md](../scripts/make-coverage.md) |
| **Position** | [CoverGroup](covergroup.md) (N) → [**CoverageModel** + **CoverageCollector**] → cocotb DUT handle ([full chain](../../explanations/architecture.md)) |

## Overview

- **`CoverageModel`**: subclass it; attach `CoverGroup` instances as class attributes. Emits a single SV module that wires every covergroup. Suitable for handing to [`make_coverage`](../scripts/make-coverage.md) for `.sv`/`.md` generation.
- **`CoverageCollector`**: subclass it; assign `cov_model` and call `connect_coverage(dut, cov_model)` to bind covergroup instances to the DUT.
- **Helpers** (`compact_index`, `traverse_type`, `get_markdown_list`): utility functions used by `make_coverage` when walking model trees and rendering output.

**Does NOT cover:**

- Individual coverpoint / cross semantics → [`coverpoint.md`](coverpoint.md) / [`cross.md`](cross.md).
- Bin spec patterns → [`../bins/`](../bins/index.md).
- CLI flags for generation → [`../scripts/make-coverage.md`](../scripts/make-coverage.md).

## Quick example

```python
from cocotbext.fcov import CoverageModel, CoverGroup, CoverPoint, BinBool, BinRange

class CustomCoverGroup1(CoverGroup):
    cp_bool = CoverPoint(BinBool())

class CustomCoverGroup2(CoverGroup):
    cp_range = CoverPoint(BinRange(10))

class CustomCovModel(CoverageModel):
    cg1 = CustomCoverGroup1()
    cg2 = CustomCoverGroup2()

cov_model = CustomCovModel(name="cov_model")
# module cov_model();
#   covergroup cg1 ... endgroup
#   covergroup cg2 ... endgroup
# endmodule
```

> Verified: [`tests/pytest/test_coverage_model.py`](../../../tests/pytest/test_coverage_model.py)

## Usage patterns

### Multiple covergroups under one model

```python
class CustomCovModel(CoverageModel):
    cg_axi  = AxiCoverGroup()
    cg_apb  = ApbCoverGroup()
    cg_perf = PerfCoverGroup()
```

### Connect a model to a DUT in a cocotb test

```python
class MyCollector(CoverageCollector):
    cov_model = CustomCovModel(name="cov_model")

collector = MyCollector(dut, cov_model=CustomCovModel(name="cov_model"))
```

### Generate `.sv` + `.md` outputs

```bash
make_coverage -f coverage_spec.py -sv coverage.sv -md coverage.md --overwrite
```

See [`../scripts/make-coverage.md`](../scripts/make-coverage.md) for the full CLI.

### Generated SV module structure

`CoverageModel.systemverilog()` produces a single SV module:

```sv
`ifdef COCOTBEXT_FCOV
module cov_model ();
  // wires for every CoverPoint signal (one per cp, unless ref=)
  wire [3:0] cg_xxx_cp_yyy;
  wire       cg_xxx_sample;
  ...

  // one covergroup per CoverGroup attribute
  covergroup cg_xxx;
    cp_yyy: coverpoint cg_xxx_cp_yyy { bins ... }
    cx_zzz: cross cp_a, cp_b;
  endgroup : cg_xxx
  cg_xxx cg_xxx_inst = new;
  always @(cg_xxx_sample) begin cg_xxx_inst.sample(); end

  // ... next covergroup ...
endmodule
`endif
```

The `always` block is gated only at the `COCOTBEXT_FCOV` macro level
— Verilator users need the `ifndef VERILATOR` patch the pilots'
Makefiles apply, because Verilator 5.038–5.042 doesn't implement
covergroup `.sample()`. See
[`examples/_lib/Makefile.common`](../../../examples/_lib/Makefile.common).

### Collector lifecycle (cocotb)

```python
@cocotb.test()
async def test_x(dut):
    cov_model = CustomCovModel(name="cov_model")    # 1. instantiate
    collector = MyCollector(dut, cov_model=cov_model)  # 2. connect

    # ... stimulus ...

    cov_model.cg_xxx.cp_yyy <= signal_value           # 3. drive
    cov_model.cg_xxx.sample()                         # 4. sample
```

The `CoverageCollector.__init__` looks up `dut.<cov_model.name>`
and, for every covergroup, resolves the SV-side instance via that
handle. If the DUT does not expose the cov_model instance under
the expected name, `CoverageCollector` raises an assertion error
during construction.

### Multiple CoverageModels under one DUT

```python
class TopCollector(CoverageCollector):
    def __init__(self, dut):
        super().__init__(
            dut,
            cov_model={
                "cov_axi":  AxiCovModel(),
                "cov_apb":  ApbCovModel(),
                "cov_perf": PerfCovModel(),
            },
        )
```

The dict form names each model and binds it to `dut.<name>`. The
SV testbench wrapper must instantiate one `module` per model with
matching instance names.

## Options & API

### API summary

| Symbol (signature) | Source | Returns | Summary |
|---|---|---|---|
| `CoverageModel(name=None, log_level="INFO")` | `cocotbext/fcov/coverage.py:784` | -- | Construct a top-level coverage container. |
| `CoverageModel.set_name(name=None, seperator="_")` | `cocotbext/fcov/coverage.py:833` | `None` | Rename + cascade to children. |
| `CoverageModel.connect(dut)` | `cocotbext/fcov/coverage.py:843` | `None` | Attach every covergroup to the DUT. |
| `CoverageModel.systemverilog(name=None)` | `cocotbext/fcov/coverage.py:852` | `str` | Emit one SV module. |
| `CoverageModel.markdown(name=None)` | `cocotbext/fcov/coverage.py:860` | `str` | Emit Markdown spec doc. |
| `CoverageCollector(dut, cov_model, log_level="INFO", **kwargs)` | `cocotbext/fcov/coverage.py:877` | -- | Bind a model to a runtime DUT. |
| `CoverageCollector.connect_coverage(dut, cov_model)` | `cocotbext/fcov/coverage.py:890` | `None` | Resolve the SV-side coverage instance handle. |

### Helpers

| Symbol (signature) | Source | Returns | Summary |
|---|---|---|---|
| `compact_index(index=None)` | `cocotbext/fcov/coverage.py:20` | `str` | Render a sparse index list, compacting contiguous spans to `[a:b]`. |
| `traverse_type(obj, class_type, flatten)` | `cocotbext/fcov/coverage.py:52` | generator | Walk a Python object tree yielding `(name, instance[, idx])` for every `class_type` instance. |
| `get_markdown_list(key, value, seperator="_", use_name=True)` | `cocotbext/fcov/coverage.py:77` | `list[str]` | Render a traversed coverage tree as Markdown. |

## See also

- [covergroup.md](covergroup.md) — the unit of grouping inside a model.
- [../scripts/make-coverage.md](../scripts/make-coverage.md) — CLI emitter.
- [../../tutorials/first-coverage-model.md](../../tutorials/first-coverage-model.md) — handheld walk through building + emitting a model.
- [../../how-to/sampling-in-cocotb.md](../../how-to/sampling-in-cocotb.md) — collector lifecycle inside a cocotb test.
