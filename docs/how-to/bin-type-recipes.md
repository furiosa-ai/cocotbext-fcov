---
title: Picking the right Bin* for a coverage spec
covers_components: [bins.type]
---
# Picking the right `Bin*` for a coverage spec

> Cookbook: real-world coverage tasks mapped onto the seventeen predefined `Bin*` patterns.

> 🇰🇷 [한국어 버전](../ko/how-to/bin-type-recipes.md) · English below.

## TL;DR

| | |
|---|---|
| **Goal** | Stop hand-crafting `BinGroup`s — pick one of the predefined patterns. |
| **When to use** | Any coverpoint where the bin shape matches a well-known distribution (range / exp / boundary / window / enum / ...). |
| **Key APIs** | All classes on [bins/type.md](../reference/bins/type.md) |

This page answers:
- "I need to cover all values of N-bit signal" — which `Bin*`?
- "I need exponential bucketing" — which `Bin*`?
- "I need to cover endpoints + interior" — which `Bin*`?

For the **full per-type signature + emit example** of every predefined
`Bin*`, jump to [`reference/bins/type.md`](../reference/bins/type.md).
This page focuses on **picking the right one by intent** (the decision
table below) plus a few **domain-flavored worked examples**.

## Decision table

| Coverage intent | Use |
|---|---|
| Single value, no sub-binning | `BinSingle(value)` |
| Full N-bit range, one open array | `BinUniform(N)` or `BinRange(N)` |
| Full N-bit range, split into `K` sub-bins | `BinUniform(N, num=K)` |
| Subrange `[a, b)` | `BinUniform(a, b)` or `BinRange(a, b)` |
| Enum / named values | `BinDict({...})` or `BinEnum(EnumCls)` |
| Booleans | `BinBool()` |
| Exponential / log-scale | `BinExp(stop, base=B)` |
| Endpoints + uniform interior | `BinMinMax(min, max, num=K)` |
| Endpoints + exponential interior | `BinMinMaxExp(min, max, base=B)` |
| One-hot bit pattern | `BinOneHot(width=W)` |
| Sliding bit pattern | `BinWindow(seed, width=W, shift=S)` |
| Default catch-all | `BinDefault()` |
| Per-bit `0`/`1` for each bit | `BinBitwise(width=W)` |
| Transition chains | `BinTransition((a, b, c), ...)` |
| "Out of spec" doc marker (no SV emit) | `BinOutOfSpec()` |

## Worked examples

### Latency histogram (exponential)

```python
cp_lat = CoverPoint(BinExp(1024, base=2), name="cp_latency")
```

Full API: [`bins/type.md#binexp`](../reference/bins/type.md#binexp).

### Burst length with boundary cases

```python
cp_burst = CoverPoint(BinMinMax(min=1, max=256, num=6), name="cp_burst")
```

Full API: [`bins/type.md#binminmax`](../reference/bins/type.md#binminmax) (boundary + uniform interior; see also [`#binminmaxuniform`](../reference/bins/type.md#binminmaxuniform) which is the renamed alias).

### Address one-hot decode

```python
cp_addr_oh = CoverPoint(BinOneHot(width=8), name="cp_addr_onehot")
```

Full API: [`bins/type.md#binonehot`](../reference/bins/type.md#binonehot).

### Strobe transition (idle → request → response → idle)

```python
cp_strobe = CoverPoint(
    BinTransition((0, 1, 2, 0), (0, 1, 0)),
    name="cp_strobe",
)
```

Full API: [`bins/type.md#bintransition`](../reference/bins/type.md#bintransition).

### Combine multiple patterns on one coverpoint (`BinGroup.__add__`)

```python
# 0..3 as 4 single-value bins + boundary/exp on 4..15.
cp_a = CoverPoint(
    BinUniform(4, num=4) + BinMinMaxExp(min=4, max=15, base=2),
    name="cp_a",
)
# Emits 8 bins:
#   bin_0_3[4] = {[0:3]};  bin_4 = {4};  bin_5_7 = {[5:7]};
#   bin_8_14 = {[8:14]};   bin_15 = {15};
```

For *two coverpoints sharing one signal*, use `ref=` instead — see
[`reference/coverage/coverpoint.md`](../reference/coverage/coverpoint.md#multi-axis-coverage-on-one-source-signal).

> Verified: [`tests/pytest/test_bin_type.py`](../../tests/pytest/test_bin_type.py) · [`tests/pytest/test_bin_emit_snapshots.py`](../../tests/pytest/test_bin_emit_snapshots.py)
>
> Verified (sim-hit): [`tests/cocotb/matrix_multiplier/`](../../tests/cocotb/matrix_multiplier/) — paired pilot exercising `BinUniform` + `BinMinMaxExp` + `BinMinMax` (including the `BinGroup.__add__` hybrid pattern) on a 2×2 matrix multiplier DUT.

## When the predefined patterns don't fit

Drop to [`BinGroup` / `BinCustom`](../reference/bins/group.md) and hand-build the dict.

## See also

- [../reference/bins/type.md](../reference/bins/type.md) — every predefined type's signature + example.
- [../explanations/bin-type-hierarchy.md](../explanations/bin-type-hierarchy.md) — why these patterns exist and how they relate.
