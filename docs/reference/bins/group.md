---
title: BinGroup
component_type: bin_group
layer: bins
src_path: cocotbext/fcov/bins/group.py
src_symbols: [BinGroup, BinCustom]
related_guides: [bin-type-recipes]
---
# BinGroup

> Ordered named container of [`BinItem`](item.md) instances — the object handed to [`CoverPoint`](../coverage/coverpoint.md) as `bins=`.

## TL;DR

| | |
|---|---|
| **What** | Dict-like store mapping bin names to `BinItem`s; renders as `bins ...` block. |
| **When to use** | When you want full control over bin names / set — bypassing the predefined [`Bin*` patterns](type.md). For common shapes, prefer [`type.md`](type.md). |
| **Key links** | [item.md](item.md) · [type.md](type.md) · [../coverage/coverpoint.md](../coverage/coverpoint.md) |
| **Position** | [BinItem](item.md) → [**BinGroup**] → [CoverPoint](../coverage/coverpoint.md) → [CoverGroup](../coverage/covergroup.md) → [CoverageModel](../coverage/model.md) ([full chain](../../explanations/architecture.md)) |

## Overview

- **Role**: Holds a `Dict[str, BinItem]`; iteration / `[]` / `len` / `keys` / `values` / `items` all delegate. Supports `+` for merging.
- **Subclasses**: every predefined type in [`type.md`](type.md) inherits from `BinGroup` and specialises the constructor for one pattern.

**Does NOT cover:**

- Single-value / pattern-shaped construction → [`Bin*` predefined types](type.md).
- Atomic per-bin rendering → [`BinItem`](item.md).

## Quick example

```python
from cocotbext.fcov import BinGroup, CoverPoint

g = BinGroup({"LOW": range(10), "HIGH": range(10, 20)})
assert len(g) == 2 and "LOW" in g.keys()

cp = CoverPoint(g, name="cp_range")
# bins LOW  = {[0:9]};
# bins HIGH = {[10:19]};
```

> Verified: [`tests/pytest/test_bin_group.py`](../../../tests/pytest/test_bin_group.py)

## Usage patterns

### Construct from `dict` (named bins)

```python
BinGroup({"FALSE": 0, "TRUE": 1})
```

### Construct from iterable of `(name, value)` pairs

```python
BinGroup([("low", range(10)), ("mid", range(10, 20)), ("high", range(20, 30))])
```

### Construct from iterable of bare values (auto-naming)

```python
BinGroup([1, 5, 9])
```

Auto-names follow [`BinItem.suggest_name`](item.md#api-summary).

### Merge / concatenate

```python
g = BinGroup({"LOW": range(10)}) + BinGroup({"HIGH": range(10, 20)})
```

### Render

```python
g.systemverilog()  # 'bins LOW = {[0:9]};\nbins HIGH = {[10:19]};'
g.markdown()       # '[0:9], [10:19]'
```

## Invariants + edge cases

### Constructor dispatch — accepted shapes

The `bins=` argument accepts many shapes via `_to_bin_item` dispatch:

| Input | Interpreted as |
|-------|----------------|
| `None` | empty group (no bins) |
| `BinGroup` | copy of the source group's bin dict |
| `range` (step==1) | single open-array bin `[start:stop-1]` |
| `dict[name, value]` | one bin per entry, key as name |
| iterable of `(name, value)` | same as dict but order-preserving |
| iterable of `(name, value, num)` | same + explicit SV array size |
| iterable of bare values | auto-named per-value bins |
| iterable of `BinItem` | preserved verbatim |

### Duplicate-name detection

```python
BinGroup([("a", 1), ("a", 2)])
# AssertionError: There are some duplicated bin names in BinGroup
```

The `_update_bins` setter asserts the post-dispatch dict has the
same length as the input list — any naming collision is rejected
immediately. (This also catches accidental same-min/max auto-names
on transition bins; the [simple_dff](../../../examples/simple_dff/)
pilot's README captures the gotcha.)

### `type` property — drives SV emission name

`BinGroup` and its subclasses expose `self.type`, derived from
`__class__.__name__` (stripping `Bin` prefix / `Group` suffix). It
is used by the Markdown emitter to decide whether to apply
`shorten` (custom groups keep the full list; predefined types
abbreviate long ones).

```python
BinGroup({"a": 0}).type       # 'Custom'
BinSingle(7).type             # 'Single'
BinUniform(10).type           # 'Uniform'
```

### Width aggregation

Setting `width` explicitly takes precedence. Otherwise:

```python
BinGroup({"a": 0, "b": 0xff}).width      # 8
BinGroup({"x": range(1024)}).width       # 10
BinGroup({}).width                       # None
```

The aggregator takes the max across contained `BinItem.width`s,
treating `None`-width items (default bins) as transparent.

## BinCustom

Marker subclass of `BinGroup` with the **identical surface** —
constructor, methods, properties, semantics are all inherited
unchanged. The only difference: `BinCustom.type` returns `'Custom'`,
which (a) tells the Markdown emitter not to abbreviate long lists
and (b) signals reader intent ("these bins were hand-curated; do
not auto-replace with a predefined `Bin*`").

```python
from cocotbext.fcov import BinCustom

cp_states = CoverPoint(BinCustom({"IDLE": 0, "BUSY": 1, "DONE": 7}))
# emits the same SV as BinGroup({"IDLE":0, ...}); just preserves
# the "hand-curated" semantic.
```

Use it when none of the [17 predefined `Bin*` types](type.md) fits
the pattern *and* the bin set is small enough to enumerate
verbatim.

> Verified: [`tests/pytest/test_bin_group.py`](../../../tests/pytest/test_bin_group.py)

## Options & API

### API summary

| Symbol (signature) | Source | Returns | Summary |
|---|---|---|---|
| `BinGroup(bins=None, width=None, prefix="bin", format=None)` | `cocotbext/fcov/bins/group.py:33` | -- | Construct from dict / iterable / `BinGroup`. |
| `BinGroup.update(bins)` / `add(bins)` / `append(bin)` | `cocotbext/fcov/bins/group.py:210` | `None` | Mutating bin-set updates. |
| `BinGroup.keys()` / `values()` / `items()` | `cocotbext/fcov/bins/group.py:201` | dict views | Standard mapping accessors. |
| `BinGroup.empty()` | `cocotbext/fcov/bins/group.py:198` | `bool` | True if no bins. |
| `BinGroup.systemverilog(format=None, keyword="bins")` | `cocotbext/fcov/bins/group.py:219` | `str` | Render every bin as `;`-terminated SV clauses. |
| `BinGroup.markdown(format=None, shorten=None, enum=False)` | `cocotbext/fcov/bins/group.py:242` | `str` | Render every bin as a Markdown spec fragment. |
| `BinGroup.type` / `bins` / `width` / `min` / `max` / `num` | properties | varies | Derived metadata. |
| `BinCustom(...)` | `cocotbext/fcov/bins/type.py:11` | `BinGroup` | Marker subclass; identical surface. |

## See also

- [item.md](item.md) — atomic `BinItem` stored inside.
- [type.md](type.md) — common predefined `Bin*` subclasses.
- [../../explanations/bin-type-hierarchy.md](../../explanations/bin-type-hierarchy.md) — `Bin*` inheritance + why each pattern exists.
