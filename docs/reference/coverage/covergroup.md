---
title: CoverGroup
component_type: covergroup
layer: coverage
src_path: cocotbext/fcov/coverage.py
src_symbols: [CoverGroup]
related_guides: [sampling-in-cocotb]
---
# CoverGroup

> Container of [`CoverPoint`](coverpoint.md) + [`Cross`](cross.md) members — emits one SystemVerilog `covergroup`. The unit at which the cocotb side calls `.sample()`.

## TL;DR

| | |
|---|---|
| **What** | A class with `CoverPoint` / `Cross` class attributes. Instances bind those members to live signals on a DUT. |
| **When to use** | Whenever you have a coherent group of coverpoints that should be sampled together (typically on one clock edge or one transaction). |
| **Key links** | [coverpoint.md](coverpoint.md) · [cross.md](cross.md) · [model.md](model.md) |
| **Position** | [CoverPoint](coverpoint.md) + [Cross](cross.md) → [**CoverGroup**] → [CoverageModel](model.md) → [CoverageCollector](model.md) ([full chain](../../explanations/architecture.md)) |

## Overview

- **Role**: Subclass `CoverGroup`, attach `CoverPoint` / `Cross` as **class attributes**, instantiate. Each instance owns deep copies of the coverpoints/crosses (so the same `CoverGroup` subclass can be instantiated multiple times under different parents).
- **Naming**: when constructed inside a [`CoverageModel`](model.md), the attribute name becomes the SV covergroup name; alternatively, pass `name="..."` to the constructor.
- **Sampling**: call `cg.set(...)` (or write the coverpoint values directly) and then `cg.sample()`; the SV runtime samples the corresponding `cg_<name>.sample()` event.

**Does NOT cover:**

- Bin specs → [`bins/`](../bins/index.md).
- Per-coverpoint sampling — `sample()` is collective at the covergroup level.
- Connecting to a real DUT — that's the [`CoverageCollector`](model.md#coveragecollector) job.

## Quick example

```python
from cocotbext.fcov import CoverGroup, CoverPoint, Cross, BinBool, BinRange

class CustomCoverGroup(CoverGroup):
    cp_bool       = CoverPoint(BinBool())
    cp_range      = CoverPoint(BinRange(10))
    cx_bool_range = Cross([cp_bool, cp_range])

cg = CustomCoverGroup(name="cg_custom")
# covergroup cg_custom;
#   cp_bool: coverpoint cg_custom_cp_bool {
#     bins FALSE = {0};
#     bins TRUE  = {1};
#   }
#   cp_range: coverpoint cg_custom_cp_range {
#     bins bin_0_9 = {[0:9]};
#   }
#   cx_bool_range: cross cp_bool, cp_range;
# endgroup
```

> Verified: [`tests/pytest/test_covergroup.py`](../../../tests/pytest/test_covergroup.py)

## Usage patterns

### Drive + sample at runtime

```python
cg = CustomCoverGroup(name="cg_custom")

# Either: write to individual coverpoints
cg.cp_bool  <= True
cg.cp_range <= 7

# Or: set them all in one call
cg.set(cp_bool=True, cp_range=7)
# Or via __call__:
cg(cp_bool=True, cp_range=7)

cg.sample()
```

### Read back current values

```python
cg.get()   # {"cp_bool": True, "cp_range": 7}
```

### Attach to a DUT (typically via `CoverageCollector`)

```python
cg.connect(dut.cov_instance)
```

### Class-attribute discovery + instance independence

`CoverGroup.__new__` runs `_copy_coverpoints()`, which deep-copies
each class-level `CoverPoint` and `Cross` into the new instance.
Two consequences:

1. **Multiple instantiations are independent.** A `CoverGroup`
   subclass instantiated twice — say one per channel — gets two
   completely separate hit-count states.

   ```python
   class ChannelCov(CoverGroup):
       cp_addr = CoverPoint(BinRange(256))

   cg_chan0 = ChannelCov(name="cg_chan0")
   cg_chan1 = ChannelCov(name="cg_chan1")
   # cg_chan0.cp_addr is NOT cg_chan1.cp_addr -- different objects.
   ```

2. **`Cross.ignore_bins` / `illegal_bins` cp references are
   remapped to the instance copies** (since commit
   `769533f`). Earlier versions would emit `binsof(None) intersect ...`
   because the cp inside ignore/illegal clauses still pointed at
   the un-named class-level template. See the
   [opcode_cross](../../../tests/cocotb/opcode_cross/) pilot README
   for the full diagnosis.

### Sample event mechanics

`cg.sample()` queues the current `cp.value` snapshot and fires the
async `_sample` loop, which:

1. Drives each `_handler.value` (the SV wire holding the coverpoint
   value).
2. Toggles `cg_<name>_sample` (the wire watched by
   `always @(cg_<name>_sample) cg_<name>_inst.sample();` in the
   emitted SV).
3. Waits for the sample wire to settle before processing the next
   queued value.

Calling `cg.sample()` from cocotb without `await`-ing anything
afterwards is safe — the async loop drains its own queue.

> Verified (sim-hit): [`tests/cocotb/simple_dff/tb_dff.py`](../../../tests/cocotb/simple_dff/tb_dff.py)

## Options & API

### API summary

| Symbol (signature) | Source | Returns | Summary |
|---|---|---|---|
| `CoverGroup(name=None, log_level="INFO")` | `cocotbext/fcov/coverage.py:534` | -- | Construct an instance with deep-copied coverpoints. |
| `CoverGroup.set(values=dict(), **kwargs)` | `cocotbext/fcov/coverage.py:653` | `None` | Set coverpoint values via dict or keyword. |
| `CoverGroup.get()` | `cocotbext/fcov/coverage.py:642` | `Dict[str, Any]` | Current coverpoint values. |
| `CoverGroup.__call__(**kwargs)` | `cocotbext/fcov/coverage.py:691` | `None` | Sugar: set values, then `sample()`. |
| `CoverGroup.sample()` | `cocotbext/fcov/coverage.py:705` | `None` | Trigger the SV sample event. |
| `CoverGroup.connect(coverage_instance)` | `cocotbext/fcov/coverage.py:623` | `None` | Attach to a live cocotb DUT instance. |
| `CoverGroup.set_name(name=None, seperator="_")` | `cocotbext/fcov/coverage.py:611` | `None` | Rename the covergroup + cascade to children. |
| `CoverGroup.systemverilog()` | `cocotbext/fcov/coverage.py:740` | `str` | Emit the SV `covergroup ... endgroup` block. |
| `CoverGroup.markdown(name=None)` | `cocotbext/fcov/coverage.py:748` | `str` | Render as Markdown spec table. |
| `CoverGroup.sample_name` / `instance_name` / `sv_wire` / `sv_instance` | properties | `str` | Naming helpers used during SV emission. |

## See also

- [coverpoint.md](coverpoint.md) — member type.
- [cross.md](cross.md) — member type.
- [model.md](model.md) — covergroups assembled into one top-level model.
- [../../how-to/sampling-in-cocotb.md](../../how-to/sampling-in-cocotb.md) — wiring `sample()` to clock / handshake events.
