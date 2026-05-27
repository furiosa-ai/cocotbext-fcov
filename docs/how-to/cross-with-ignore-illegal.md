---
title: Cross with ignore_bins / illegal_bins
prerequisites: [first-coverage-model]
covers_components: [coverage.cross]
---
# Cross with `ignore_bins` / `illegal_bins`

> Filter cross-product coverage to skip nonsensical combinations
> (`ignore_bins`) or flag forbidden combinations (`illegal_bins`).

> 🇰🇷 [한국어 버전](../ko/how-to/cross-with-ignore-illegal.md) · English below.

## TL;DR

| | |
|---|---|
| **Goal** | Write `Cross(..., ignore_bins=[...], illegal_bins=[...])` clauses that emit the right SystemVerilog `binsof ... intersect ...` chains. |
| **When to use** | When the cross product over coverpoints contains combinations that either (a) cannot occur by design (`ignore_bins`) or (b) must never occur and are bugs (`illegal_bins`). |
| **Key APIs** | `Cross`, clause schema `{"name", "terms"}`, term shape `(cp, value_spec[, negate])` |

This page answers:
- What goes in a `terms` list?
- What value_spec shapes are accepted?
- How do I negate one term?

## Overview

**Role.** Cross-level filters keep the cross matrix small enough to close. Each clause maps to one SV `binsof(cp) intersect {...}` chain joined by `&&` across terms.

**Does NOT cover:**

- Per-coverpoint `ignore_bins` — set those on the [`CoverPoint`](../reference/coverage/coverpoint.md).
- Picking the right `Bin*` for each coverpoint → [bin-type-recipes.md](bin-type-recipes.md).

## Clause shape

```python
{
    "name":  "<sv_identifier>",            # required
    "terms": [
        (<cp>, <value_spec>),              # 2-tuple
        (<cp>, <value_spec>, <negate>),    # 3-tuple
    ],
}
```

## Worked example

```python
from cocotbext.fcov import CoverPoint, Cross, BinEnum, BinUniform
from enum import Enum

class Op(Enum):
    READ = 0; WRITE = 1; WRAP = 2

cp_op   = CoverPoint(BinEnum(Op),   name="cp_op")
cp_size = CoverPoint(BinUniform(16), name="cp_size")

cx = Cross(
    [cp_op, cp_size],
    name="cx_op_size",
    ignore_bins=[
        {"name": "ig_wrap_big_size",
         "terms": [(cp_op, "WRAP"), (cp_size, "[8:15]")]},
    ],
    illegal_bins=[
        {"name": "il_read_at_0",
         "terms": [(cp_op, "READ"), (cp_size, 0)]},
    ],
)
# cx_op_size: cross cp_op, cp_size {
#   ignore_bins ig_wrap_big_size = binsof(cp_op) intersect {WRAP} && binsof(cp_size) intersect {[8:15]};
#   illegal_bins il_read_at_0    = binsof(cp_op) intersect {READ} && binsof(cp_size) intersect {0};
# }
```

> Verified: [`tests/pytest/test_cross.py`](../../tests/pytest/test_cross.py)
>
> Verified (sim-hit): [`examples/opcode_cross/`](../../examples/opcode_cross/) — paired pilot exercising `Cross` + `ignore_bins` + `illegal_bins` on a 4-op ALU DUT.

## Value-spec shapes

| Form | Emitted inside `intersect {...}` |
|------|----------------------------------|
| `str` | spec as-is — e.g. `"WRAP"`, `"1, 3, 5"`, `"[17:256]"` |
| `int` | single value — e.g. `7` → `{7}` |
| `range` | `[start:stop-1]` (step==1) or comma-joined items (step>1) |
| `list` / `tuple` / `set` | comma-joined mix of ints + ranges — e.g. `{1, 3, [5:7]}` |
| object with `as_string(lang=LanguageType.SystemVerilog)` | rendered string used verbatim |

## Negate one term

The 3-tuple form sets a negation prefix:

```python
{"name": "il_not_wr_at_0",
 "terms": [(cp_op, "WRITE", True), (cp_size, 0)]}
# illegal_bins il_not_wr_at_0 = !binsof(cp_op) intersect {WRITE} && binsof(cp_size) intersect {0};
```

## See also

- [../reference/coverage/cross.md](../reference/coverage/cross.md) — full `Cross` API.
- [../reference/coverage/coverpoint.md](../reference/coverage/coverpoint.md) — per-coverpoint ignore / illegal.
