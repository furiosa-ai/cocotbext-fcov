---
title: Cross
component_type: cross
layer: coverage
src_path: cocotbext/fcov/coverage.py
src_symbols: [Cross]
related_guides: [cross-with-ignore-illegal]
---
# Cross

> SystemVerilog `cross` over two or more [`CoverPoint`](coverpoint.md)s, with optional cross-level ignore / illegal bin clauses.

## TL;DR

| | |
|---|---|
| **What** | One SV `cross` declaration over a list of coverpoints. |
| **When to use** | Whenever per-coverpoint coverage is not enough and you need to verify combinations of values (e.g. `(opcode, mode)` pairs). |
| **Key links** | [coverpoint.md](coverpoint.md) · [covergroup.md](covergroup.md) · [../../how-to/cross-with-ignore-illegal.md](../../how-to/cross-with-ignore-illegal.md) |
| **Position** | [CoverPoint](coverpoint.md) (≥ 2) → [**Cross**] → [CoverGroup](covergroup.md) → [CoverageModel](model.md) ([full chain](../../explanations/architecture.md)) |

## Overview

- **Role**: Lives inside a [`CoverGroup`](covergroup.md) alongside coverpoints. Renders as `<name>: cross <cp1>, <cp2>, ...;`.
- **Ignore / illegal**: each cross-level clause is a `{"name": str, "terms": [(cp, value_spec[, negate]), ...]}` dict. `value_spec` accepts strings (passed through to `intersect {...}`), ints, ranges, lists/tuples/sets, and any object with an `as_string(lang=LanguageType.SystemVerilog)` method.

**Does NOT cover:**

- Per-coverpoint ignore / illegal → set those on the [`CoverPoint`](coverpoint.md) itself.
- Sampling — `Cross` is rendered, not sampled directly; SV samples the cross as part of the covergroup.

## Quick example

```python
from cocotbext.fcov import CoverPoint, Cross, BinBool, BinRange

cp1 = CoverPoint(BinBool(),  name="cp1")
cp2 = CoverPoint(BinRange(10), name="cp2")
cx  = Cross([cp1, cp2], name="cx")
# cx: cross cp1, cp2;
```

> Verified: [`tests/pytest/test_cross.py`](../../../tests/pytest/test_cross.py)

## Usage patterns

### Plain cross

```python
Cross([cp_opcode, cp_size, cp_mode], name="cx_opcode_size_mode")
```

### With cross-level `ignore_bins`

```python
Cross(
    [cp_opcode, cp_size],
    name="cx_oc_size",
    ignore_bins=[
        {"name": "ig_wrap_4b", "terms": [(cp_opcode, "WRAP"), (cp_size, "[8:15]")]},
    ],
)
# ignore_bins ig_wrap_4b = binsof(cp_opcode) intersect {WRAP} && binsof(cp_size) intersect {[8:15]};
```

### Negated term

```python
Cross(
    [cp1, cp2],
    illegal_bins=[
        {"name": "il_not_wr_at_0", "terms": [(cp1, "WRITE", True), (cp2, 0)]},
    ],
)
# illegal_bins il_not_wr_at_0 = !binsof(cp1) intersect {WRITE} && binsof(cp2) intersect {0};
```

### Object-typed `value_spec`

When a `value_spec` carries `as_string(lang=LanguageType.SystemVerilog)`, the rendered string is used directly — useful for handing in a pre-built `BinItem`.

### `value_spec` must be a set of integer values, not bin names

The SV LRM 19.5 `cross_set_expression` accepts a **set of integer
values**, not bin names. The natural-feeling Python form

```python
ignore_bins=[
    {"name":  "ig_and_zero",
     "terms": [(cp_op, "AND"), (cp_result_zero, "TRUE")]},
]
```

emits `binsof(cp_op) intersect {AND}` which both VCS and Questa
reject with `Identifier 'AND' has not been declared`. Pass the
integer encoding — pair the `IntEnum` value to make it readable:

```python
ignore_bins=[
    {"name":  "ig_and_zero",
     "terms": [(cp_op, int(Op.AND)), (cp_result_zero, 1)]},
]
```

> Verified (sim-hit): [`tests/cocotb/opcode_cross/coverage_spec.py`](../../../tests/cocotb/opcode_cross/coverage_spec.py)

### Cross-level `ignore_bins` vs. per-`CoverPoint` `ignore_bins`

| Where | When to use |
|-------|-------------|
| **CoverPoint.ignore_bins** | The bin set of one coverpoint should never count — exclude it for *every* cross it participates in. |
| **Cross.ignore_bins** | A specific *combination* of bins is uninteresting only when crossed together (cp_op=AND × cp_zero=TRUE is trivially true; cp_op=ADD × cp_zero=TRUE is genuinely interesting and must stay). |

Use `illegal_bins` (cross or coverpoint) when the same combination
indicates a design bug — the simulator flags hits as errors.

## Options & API

### API summary

| Symbol (signature) | Source | Returns | Summary |
|---|---|---|---|
| `Cross(coverpoints, name=None, group=None, ignore_bins=(), illegal_bins=())` | `cocotbext/fcov/coverage.py:377` | -- | Construct a cross declaration over a list of coverpoints. |
| `Cross.set_name(name, group)` | `cocotbext/fcov/coverage.py:427` | `None` | Bind to a parent covergroup name. |
| `Cross.sv_declare()` | `cocotbext/fcov/coverage.py:486` | `str` | Render the SV `<name>: cross ...;` declaration. |
| `Cross.markdown(name=None)` | `cocotbext/fcov/coverage.py:517` | `str` | Render as a Markdown spec row. |
| `Cross.coverpoints` / `ignore_bins` / `illegal_bins` | attributes | list | Construction-time inputs preserved verbatim. |

### `ignore_bins` / `illegal_bins` clause schema

Each entry:

```python
{
    "name": "<sv_identifier>",            # required
    "terms": [
        (<cp>, <value_spec>),             # 2-tuple
        (<cp>, <value_spec>, <negate>),   # 3-tuple
    ],
}
```

`value_spec` accepted forms:

| Form | Emitted |
|---|---|
| `str` | `binsof(cp) intersect {<spec>}` verbatim |
| `int` | `binsof(cp) intersect {N}` |
| `range` | `binsof(cp) intersect {[start:stop-1]}` (step==1) or comma-joined |
| `list` / `tuple` / `set` | `binsof(cp) intersect {<comma-joined mix>}` |
| object with `as_string(lang=LanguageType.SystemVerilog)` | rendered string used directly |

## See also

- [coverpoint.md](coverpoint.md) — the building block.
- [covergroup.md](covergroup.md) — how a `Cross` lives inside a covergroup.
- [../../how-to/cross-with-ignore-illegal.md](../../how-to/cross-with-ignore-illegal.md) — worked recipes for cross-level filters.
