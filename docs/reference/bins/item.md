---
title: BinItem
component_type: bin_item
layer: bins
src_path: cocotbext/fcov/bins/item.py
src_symbols: [BinItem, LanguageType]
related_guides: [bin-type-recipes]
---
# BinItem

> Atomic bin: one or more values, a range, or a transition chain — renderable as Python string, SystemVerilog `bins ...` clause, or Markdown fragment.

## TL;DR

| | |
|---|---|
| **What** | The smallest unit of coverage — one named bin. |
| **When to use** | Directly: rarely; almost always wrapped via [`BinGroup`](group.md) or a [`Bin*` predefined type](type.md). Construct a `BinItem` only when you need to hand-craft a transition chain. |
| **Key links** | [group.md](group.md) · [type.md](type.md) · [../coverage/coverpoint.md](../coverage/coverpoint.md) |
| **Position** | [**BinItem**] → [BinGroup](group.md) → [CoverPoint](../coverage/coverpoint.md) → [CoverGroup](../coverage/covergroup.md) → [CoverageModel](../coverage/model.md) ([full chain](../../explanations/architecture.md)) |

## Overview

- **Role**: Holds the value spec (`items`) and optional transition `next`, plus name / num / width / format metadata. Rendering methods (`as_string`, `systemverilog`, `markdown`) drive emission.
- **Construction**: end users typically pass values directly to [`CoverPoint`](../coverage/coverpoint.md) or to a [predefined `Bin*` type](type.md), which wraps them in `BinItem`s internally.

**Does NOT cover:**

- Grouping multiple bins under one coverpoint → [`BinGroup`](group.md).
- Pattern-shaped bin sets (single / uniform / exp / minmax / ...) → [`Bin*` types](type.md).

## Quick example

```python
from cocotbext.fcov import BinItem

# Single value
b = BinItem(items=5)
assert b.as_string() == "5"

# Range
b = BinItem(items=range(10))
assert b.as_string() == "[0:9]"

# Transition chain: 1 => 2 => 3
b = BinItem(items=1) >> 2 >> 3
assert b.as_string() == "1 => 2 => 3"
```

> Verified: [`tests/pytest/test_bin_item.py`](../../../tests/pytest/test_bin_item.py)

## Usage patterns

### Construct from raw value

`BinItem` accepts an int, a `range`, a list / tuple of either, or an iterable yielding the transition marker `"=>"` between values.

```python
BinItem(items=[1, 5, 9])             # bins bin_1_9 = {1, 5, 9}
BinItem(items=[range(10), range(20, 30)])  # bins bin_0_29 = {[0:9], [20:29]}
```

### Build a transition chain via `>>` / `<<`

```python
chain = BinItem(items=1) >> 2 >> 3   # 1 => 2 => 3
chain = 1 << BinItem(items=2)        # 1 => 2
```

### Render for SystemVerilog vs Markdown

```python
b = BinItem(items=range(10), num=5, name="bin_0_9")
b.systemverilog()  # 'bins bin_0_9[5] = {[0:9]}'
b.markdown()       # '[0:9]/5'
```

## Invariants + edge cases

### Transition vs. value bin — all-or-nothing

The setter on `items` asserts every entry is either *all* values
(ints + `range`s) or *all* transition `BinItem`s. Mixing the two
raises `AssertionError`:

```python
BinItem(items=[1, BinItem(items=1) >> 2])
# AssertionError: All bin items ... should be same!
```

### `width` is derived from min/max when unset

```python
BinItem(items=range(256)).width     # 8
BinItem(items=-5).width              # 4 (sign bit + 3-bit magnitude)
BinItem(items=[]).width              # None (default bin has no width)
```

The explicit `width=` parameter overrides the derived value and is
preserved across `as_string(lang=SystemVerilog)` for SV
size-prefixed literals (`'8'h3`).

### `range`-with-step special case

A `range(start, stop, step)` with `step > 1` is treated as a single
SV "stepped" bin (emitted as `{[start:stop-1]} with (item % step == offset)`)
when it is the only item; nested inside a longer list it is flattened to
the individual values.

```python
BinItem(items=range(0, 10, 2))
# bins bin_0_8[] = {[0:9]} with (item % 2 == 0)

BinItem(items=[range(0, 10, 2), 5])
# bins bin_0_8 = {0, 2, 4, 6, 8, 5}     # flattened
```

### Operator contract — `>>` / `<<` / `+`

| Operator | Effect | Constraint |
|---|---|---|
| `a >> b` | append `b` as next link in a's transition chain | a may or may not already be a transition |
| `a << b` | reverse: prepend a in front of b's chain | a's existing `next` is preserved |
| `a + b`  | concatenate value lists (merges items) | b must not be a transition (TypeError) |

`format` and `prefix` propagate through `+` / `>>` / `<<` to the
result.

## LanguageType (enum)

```python
from cocotbext.fcov.bins.item import LanguageType
LanguageType.Default          # 0 — Python-string rendering
LanguageType.SystemVerilog    # 1 — SV-string rendering
```

`IntEnum` used by `BinItem.as_string(lang=...)` and by `Cross`
`value_spec` objects that implement `as_string(lang=...)`. The two
members tell the renderer whether to emit Python-style commas or
SV `{[a:b]}` syntax. Reachable as `cocotbext.fcov.bins.item.LanguageType`
(not re-exported at top level).

## Options & API

### API summary

| Symbol (signature) | Source | Returns | Summary |
|---|---|---|---|
| `LanguageType` | `cocotbext/fcov/bins/item.py:7` | -- | `IntEnum`: `Default` / `SystemVerilog`. |
| `BinItem(items=None, width=None, next=None, name=None, num=1, prefix="bin", format="d")` | `cocotbext/fcov/bins/item.py:49` | -- | Construct one atomic bin. |
| `BinItem.suggest_name(prefix=None, seperator="_", format=None)` | `cocotbext/fcov/bins/item.py:343` | `str` | Auto-name from min/max values. |
| `BinItem.add(items)` / `append(item)` | `cocotbext/fcov/bins/item.py:365` | `None` | Append more values to the bin. |
| `BinItem.as_string(lang=Default, format=None, seperator=",", shorten=False)` | `cocotbext/fcov/bins/item.py:427` | `str` | Render value set as a string. |
| `BinItem.systemverilog(format=None, keyword="bins")` | `cocotbext/fcov/bins/item.py:466` | `str` | Render as `<keyword> <name> = ...` clause. |
| `BinItem.markdown(format=None, shorten=True, enum=False)` | `cocotbext/fcov/bins/item.py:505` | `str` | Render as Markdown spec fragment. |
| `BinItem.min` / `max` / `width` / `num` | properties | `int` / `None` | Derived metadata. |
| `BinItem.is_default()` | `cocotbext/fcov/bins/item.py:263` | `bool` | True if no items (default bin). |

Full method contracts live in the source docstrings.

## See also

- [group.md](group.md) — `BinGroup` is the typical user-facing container.
- [type.md](type.md) — predefined `Bin*` patterns wrap `BinItem` internally.
- [../coverage/coverpoint.md](../coverage/coverpoint.md) — how `BinItem`s reach a SystemVerilog `coverpoint`.
