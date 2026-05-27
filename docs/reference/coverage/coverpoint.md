---
title: CoverPoint
component_type: coverpoint
layer: coverage
src_path: cocotbext/fcov/coverage.py
src_symbols: [CoverPoint]
related_guides: [sampling-in-cocotb, bin-type-recipes]
---
# CoverPoint

> Single SystemVerilog `coverpoint` over a [`BinGroup`](../bins/group.md) — the primitive unit of functional coverage in a [`CoverGroup`](covergroup.md).

## TL;DR

| | |
|---|---|
| **What** | One coverpoint: a value-set spec plus optional ignore / illegal bins. |
| **When to use** | Whenever you want a SystemVerilog `coverpoint <name>: coverpoint <signal>;` block declared from Python. |
| **Key links** | [../bins/group.md](../bins/group.md) · [../bins/type.md](../bins/type.md) · [covergroup.md](covergroup.md) · [cross.md](cross.md) |
| **Position** | [BinItem](../bins/item.md) → [BinGroup](../bins/group.md) → [**CoverPoint**] → [CoverGroup](covergroup.md) → [CoverageModel](model.md) ([full chain](../../explanations/architecture.md)) |

## Overview

- **Role**: Carries the bin spec (`bins`), ignore set (`ignore_bins`), illegal set (`illegal_bins`), width, prefix, and format. Renders as a single SV `coverpoint` block via [`covergroup.systemverilog()`](covergroup.md).
- **Sampling**: at runtime, the parent [`CoverGroup`](covergroup.md) writes the observed value into `cp.value`; the SV side samples the corresponding `cg.sample()`.
- **Reuse via `ref`**: passing `ref=<other_cp>` shares the source signal and skips emitting a new wire — useful when two coverpoints need to track the same value with different bins.

**Does NOT cover:**

- Grouping multiple coverpoints → [`CoverGroup`](covergroup.md).
- Cross-product coverage between coverpoints → [`Cross`](cross.md).

## Quick example

```python
from cocotbext.fcov import CoverPoint, BinRange, BinBool

cp_range = CoverPoint(BinRange(10), name="cp_range")
cp_bool  = CoverPoint(BinBool(),     name="cp_bool")

# 1, 5 — integer single values
CoverPoint([1, 5])
# bins bin_1 = {1};
# bins bin_5 = {5};

# range objects
CoverPoint([range(10), range(10, 20)])
# bins bin_0_9   = {[0:9]};
# bins bin_10_19 = {[10:19]};

# nested iterables (each becomes one named multi-value bin)
CoverPoint([[1, 2], (3, 5, 7)])
# bins bin_1_2 = {1, 2};
# bins bin_3_7 = {3, 5, 7};

# transition shorthand inside a bare list
CoverPoint([[1, "=>", 2], [range(10, 20), "=>", range(20, 30)]])
# bins bin_1_2  = {1 => 2};
# bins bin_10_29 = {[10:19] => [20:29]};
```

> Verified: [`tests/pytest/test_coverpoint.py`](../../../tests/pytest/test_coverpoint.py)

## Usage patterns

### Direct value-list spec

`CoverPoint(<list>)` accepts the same shapes as [`BinGroup(<list>)`](../bins/group.md). Internally the list is normalised into a `BinGroup`.

```python
CoverPoint([1, 5])                  # two single-value bins
CoverPoint([range(10), range(10, 20)])  # two range bins
```

### Pre-built `BinGroup` / predefined `Bin*` spec

```python
CoverPoint(BinRange(10))
CoverPoint(BinMinMax(min=0, max=255, num=5))
```

### Ignore / illegal bins

`ignore_bins` and `illegal_bins` accept the same spec shape as `bins`.

```python
CoverPoint(BinRange(256), ignore_bins=[0], illegal_bins=BinSingle(0xff))
```

### Reuse the same source signal (`ref`)

```python
cp_addr   = CoverPoint(BinUniform(1<<32), name="cp_addr")
cp_addr_4kb = CoverPoint(BinSingle(0xfff), ref=cp_addr, name="cp_addr_4kb")
```

### Drive the sampled value at runtime

```python
cp_range.value = sig.value
# or: cp_range <= sig.value
```

### Multi-axis coverage on one source signal

Two coverpoints can share the same SV wire by passing `ref=`. The
emit pipeline allocates the wire for the first cp and skips the
re-declaration on the second.

```python
cp_a_exp     = CoverPoint(BinExp(16, base=2))             # exp buckets
cp_a_uniform = CoverPoint(BinUniform(16, num=4),
                          ref=cp_a_exp)                   # same wire, 4 partitions
```

SV emit (one wire, two coverpoint blocks):

```sv
wire [3:0] cg_cp_a_exp;
covergroup cg ;
  cp_a_exp:     coverpoint cg_cp_a_exp { bins bin_0 = {0}; bins bin_1 = {1}; ... }
  cp_a_uniform: coverpoint cg_cp_a_exp { bins bin_0_15[4] = {[0:15]}; }
endgroup
```

> Verified (sim-hit): [`tests/cocotb/adder/coverage_spec.py`](../../../tests/cocotb/adder/coverage_spec.py) (BinUniform + BinBitwise on operand A via ref=)

### `BinOutOfSpec` skips the value drive

A `CoverPoint(BinOutOfSpec(), ref=cp_other)` emits the doc-only
"out of spec" Markdown marker. cocotbext-fcov's `_drive` skips
setting the SV wire for such coverpoints — useful when the parent
coverpoint is wide enough that the 1-bit out-of-spec wire would
otherwise raise a `Logic` conversion error.

> Verified: [`tests/pytest/test_coverpoint.py`](../../../tests/pytest/test_coverpoint.py)

### `signal` property — auto-named wire

The SV wire name is `<group>_<cp_name>` (composed by `set_name`
during covergroup elaboration). Use the `signal` property only
when you need to reference the wire from raw SV — most users
never read it.

```python
>>> cp_range.signal
'cg_xxx_cp_range'
```

## Options & API

### API summary

| Symbol (signature) | Source | Returns | Summary |
|---|---|---|---|
| `CoverPoint(bins, ignore_bins=None, illegal_bins=None, width=None, name=None, group=None, ref=None, prefix="bin", format=None, log_level="INFO")` | `cocotbext/fcov/coverage.py:112` | -- | Construct a coverpoint from a `BinGroup` / list / predefined `Bin*`. |
| `CoverPoint.value` (property) | `cocotbext/fcov/coverage.py:207` | `Any` | Last-sampled value; setter writes the value for next `sample()`. |
| `CoverPoint.__le__(value)` | `cocotbext/fcov/coverage.py:230` | `None` | Sugar for `cp.value = value`. |
| `CoverPoint.set_name(name, group)` | `cocotbext/fcov/coverage.py:306` | `None` | Bind the coverpoint to a parent covergroup name. |
| `CoverPoint.connect(coverage_instance)` | `cocotbext/fcov/coverage.py:310` | `None` | Attach to the runtime cocotb DUT instance. |
| `CoverPoint.systemverilog()` (via parent) | `cocotbext/fcov/coverage.py:336` | `str` | Emit the SV `coverpoint <name>: coverpoint <signal> {...};` block. |
| `CoverPoint.markdown(name=None, shorten=None)` | `cocotbext/fcov/coverage.py:360` | `str` | Render as a Markdown spec row. |
| `CoverPoint.min` / `max` / `width` / `num` / `signal` | properties | varies | Derived metadata. |

Full method contracts live in the source docstrings.

## See also

- [../bins/group.md](../bins/group.md) — the `bins=` container.
- [../bins/type.md](../bins/type.md) — predefined `Bin*` patterns.
- [covergroup.md](covergroup.md) — how a `CoverPoint` lives inside a covergroup.
- [cross.md](cross.md) — combining multiple coverpoints into a cross.
- [../../how-to/sampling-in-cocotb.md](../../how-to/sampling-in-cocotb.md) — driving `cp.value` from a cocotb test.
