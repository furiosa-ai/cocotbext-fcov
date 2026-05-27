---
title: Predefined Bin Types
component_type: bin_type
layer: bins
src_path: cocotbext/fcov/bins/type.py
src_symbols: [BinSingle, BinUniform, BinRange, BinDict, BinEnum, BinBool, BinExp, BinMinMax, BinMinMaxUniform, BinMinMaxExp, BinWindow, BinOneHot, BinDefault, BinOutOfSpec, BinBitwise, BinTransition]
related_guides: [bin-type-recipes]
---
# Predefined Bin Types

> Sixteen specialised `BinGroup` subclasses + [`BinCustom`](group.md#bincustom)
> (the no-specialisation marker subclass, documented on `group.md` since
> its surface is identical to `BinGroup`). 17 public `Bin*` types in total.

## TL;DR

| | |
|---|---|
| **What** | Drop-in `BinGroup` subclasses — pass them to [`CoverPoint`](../coverage/coverpoint.md) instead of hand-building a `BinGroup`. |
| **When to use** | Almost always; the predefined patterns cover ~90% of real coverage shapes. Fall back to [`BinGroup` / `BinCustom`](group.md) for hand-curated sets. |
| **Key links** | [group.md](group.md) · [item.md](item.md) · [../coverage/coverpoint.md](../coverage/coverpoint.md) · [../../explanations/bin-type-hierarchy.md](../../explanations/bin-type-hierarchy.md) |
| **Position** | [BinItem](item.md) → [**Bin* (17 subclasses of BinGroup)**](group.md) → [CoverPoint](../coverage/coverpoint.md) → [CoverGroup](../coverage/covergroup.md) → [CoverageModel](../coverage/model.md) ([full chain](../../explanations/architecture.md)) |

## Overview

- **Role**: Each subclass takes pattern-specific constructor args (`range`, `Enum`, `min`/`max`, `width`, ...) and builds a normalised `BinGroup` underneath.
- **Inheritance** (simplified): every class derives from [`BinGroup`](group.md); the diagram + rationale live in the [explanations page](../../explanations/bin-type-hierarchy.md).

**Does NOT cover:**

- Hand-curated arbitrary bin sets → [`BinGroup` / `BinCustom`](group.md).
- Combining bins from multiple sources → [`BinGroup.__add__`](group.md#api-summary).

## Quick example

```python
from cocotbext.fcov import (
    CoverPoint, BinSingle, BinRange, BinBool, BinMinMax, BinTransition,
)

# Single value
CoverPoint(BinSingle(7))                       # bins bin_7 = {7};

# Range
CoverPoint(BinRange(10, 20))                   # bins bin_10_19[] = {[10:19]};

# Boolean
CoverPoint(BinBool(), format="b")              # bins FALSE = {'b0}; TRUE = {'b1};

# Min/max boundary coverage
CoverPoint(BinMinMax(min=100, max=200, num=5))
# bins bin_100 = {100};
# bins bin_101_199[3] = {[101:199]};
# bins bin_200 = {200};

# Transition chain
CoverPoint(BinTransition((1, 2, 3), (4, 5, 6)))
# bins bin_1_3 = (1 => 2 => 3);
# bins bin_4_6 = (4 => 5 => 6);
```

> Verified: [`tests/pytest/test_bin_type.py`](../../../tests/pytest/test_bin_type.py)

## Pattern catalog

### `BinSingle`

Single bin around one value or range.

```python
CoverPoint(BinSingle(1))               # bins bin_1 = {1};
CoverPoint(BinSingle(range(10)))       # bins bin_0_9 = {[0:9]};
```

### `BinUniform`

Open-array range split evenly via `num`. Used like Python's `range()`.

```python
CoverPoint(BinUniform(10))                       # bins bin_0_9[] = {[0:9]};
CoverPoint(BinUniform(10, 20, num=5))            # bins bin_10_19[5] = {[10:19]};
```

### `BinRange`

Same as `BinUniform` but always open-array (no `num`).

```python
CoverPoint(BinRange(10))            # bins bin_0_9[] = {[0:9]};
CoverPoint(BinRange(10, 20))        # bins bin_10_19[] = {[10:19]};
```

### `BinDict`

Bins built from `{name: value}`.

```python
CoverPoint(BinDict({"FALSE": 0, "TRUE": 1}), format="b")
# bins FALSE = {'b0}; TRUE = {'b1};
```

### `BinEnum`

Bins derived from a Python `Enum`.

```python
class Bool(Enum): FALSE = 0; TRUE = 1
CoverPoint(BinEnum(Bool), format="b")
# bins FALSE = {'b0}; TRUE = {'b1};
```

### `BinBool`

One-liner for the boolean two-bin pattern.

```python
CoverPoint(BinBool())     # bins FALSE = {'b0}; TRUE = {'b1};
```

### `BinExp`

Exponential bucketing. Used like `range()` with `base=`.

```python
CoverPoint(BinExp(100, base=10))
# bins bin_0 = {0};
# bins bin_1_9 = {[1:9]};
# bins bin_10_99 = {[10:99]};
```

### `BinMinMax`

Uniform bins with explicit boundary bins on `min` and `max`.

```python
CoverPoint(BinMinMax(min=100, max=200, num=5))
# bins bin_100 = {100};
# bins bin_101_199[3] = {[101:199]};
# bins bin_200 = {200};
```

### `BinMinMaxUniform`

Renamed alias for `BinMinMax` — use this name when paired with `BinMinMaxExp` for code-review clarity (the `Uniform` suffix makes the contrast obvious).

### `BinMinMaxExp`

Exponential bucketing with explicit boundary bins.

```python
CoverPoint(BinMinMaxExp(min=100, max=200, base=2))
# bins bin_100 = {100};
# bins bin_101_127 = {[101:127]};
# bins bin_128_199 = {[128:199]};
# bins bin_200 = {200};
```

### `BinWindow`

Sliding bit-pattern: `window` shifted left by `shift` bits, repeatedly.

```python
CoverPoint(BinWindow(0x6, width=6, shift=2))
# bins bin_0x6  = {'h6};
# bins bin_0x18 = {'h18};
# bins bin_0x20 = {'h20};
```

### `BinOneHot`

One bin per single-bit pattern across `width` bits.

```python
CoverPoint(BinOneHot(width=3, format="b"))
# bins bin_0b1   = {'b1};
# bins bin_0b10  = {'b10};
# bins bin_0b100 = {'b100};
```

### `BinDefault`

Single default catch-all.

```python
CoverPoint(BinDefault())          # bins others = default;
```

### `BinOutOfSpec`

Documentation-only marker — emits nothing in SV; renders as `"Out of spec"` in Markdown.

### `BinBitwise`

Per-bit `0`/`1` coverage for a `width`-bit signal.

```python
CoverPoint(BinBitwise(3), name="cp_bitwise", group="cg_predefined")
# cp_bitwise_0: coverpoint cg_predefined_cp_bitwise[0];
# cp_bitwise_1: coverpoint cg_predefined_cp_bitwise[1];
# cp_bitwise_2: coverpoint cg_predefined_cp_bitwise[2];
```

### `BinTransition`

Multi-bin transition coverage.

```python
CoverPoint(BinTransition((1, 2, 3), (4, 5, 6), ([7, 8, 9], range(10, 20))))
# bins bin_1_3 = (1 => 2 => 3);
# bins bin_4_6 = (4 => 5 => 6);
# bins bin_7_19 = (7, 8, 9 => [10:19]);
```

## Options & API

### API summary

| Symbol (signature) | Inherits | Source | Summary |
|---|---|---|---|
| `BinSingle(value, width=None, name=None, prefix="bin", format=None)` | `BinGroup` | `bins/type.py:23` | One bin around `value` (int or range). |
| `BinUniform(*args, width=None, num=0, name=None, prefix="bin", format=None)` | `BinGroup` | `bins/type.py:48` | Open-array range, optionally split into `num` sub-bins. |
| `BinRange(*args, width=None, name=None, prefix="bin", format=None)` | `BinUniform` | `bins/type.py:85` | Open-array range; no `num`. |
| `BinDict(bins: dict, width=None, prefix="bin", format=None)` | `BinGroup` | `bins/type.py:103` | Bins from `{name: value}` mapping. |
| `BinEnum(enums, width=None, prefix=None, format=None)` | `BinDict` | `bins/type.py:132` | Bins from a Python `Enum`. |
| `BinBool(prefix=None, format=None)` | `BinEnum` | `bins/type.py:167` | Boolean `FALSE`/`TRUE` bins. |
| `BinExp(*args, width=None, base=2, prefix="bin", format=None)` | `BinGroup` | `bins/type.py:182` | Exponential bucket range. |
| `BinMinMax(min=None, max=None, width=None, num=3, name=None, prefix="bin", format=None)` | `BinUniform` | `bins/type.py:236` | Boundary bins + interior uniform. |
| `BinMinMaxUniform(...)` | `BinMinMax` | `bins/type.py:295` | Alias for `BinMinMax`. |
| `BinMinMaxExp(min=None, max=None, width=None, base=2, prefix="bin", format=None)` | `BinExp, BinMinMax` | `bins/type.py:303` | Boundary bins + interior exponential. |
| `BinWindow(window=1, width=None, shift=None, prefix="bin", format="x")` | `BinGroup` | `bins/type.py:230` | Sliding bit-pattern bin set. |
| `BinOneHot(width=None, prefix="bin", format="x")` | `BinWindow` | `bins/type.py:384` | One bin per single-bit pattern. |
| `BinDefault(width=None, prefix="bin", format=None)` | `BinGroup` | `bins/type.py:395` | Default catch-all bin. |
| `BinOutOfSpec(prefix="bin", format=None)` | `BinGroup` | `bins/type.py:408` | Documentation-only marker. |
| `BinBitwise(width=None, prefix="bin", format=None)` | `BinGroup` | `bins/type.py:431` | Per-bit `0`/`1` spec. |
| `BinTransition(*trans_bins, width=None, prefix="bin", format=None)` | `BinGroup` | `bins/type.py:455` | Multi-bin transition spec. |

Full method contracts live in the docstrings. All shared `BinGroup` methods (`systemverilog`, `markdown`, `update`, ...) are documented on the [`group.md`](group.md) page.

## See also

- [group.md](group.md) — base class; the shared API.
- [item.md](item.md) — atomic `BinItem` underneath.
- [../coverage/coverpoint.md](../coverage/coverpoint.md) — primary consumer.
- [../../explanations/bin-type-hierarchy.md](../../explanations/bin-type-hierarchy.md) — *why* each pattern exists.
- [../../how-to/bin-type-recipes.md](../../how-to/bin-type-recipes.md) — picking the right `Bin*` for a real task.
