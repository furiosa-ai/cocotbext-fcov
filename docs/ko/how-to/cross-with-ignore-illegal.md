---
source: ../../how-to/cross-with-ignore-illegal.md
source_hash: bootstrap
title: Cross — ignore_bins / illegal_bins
---
# Cross — `ignore_bins` / `illegal_bins`

> Cross-product coverage에서 의미 없는 조합 (`ignore_bins`) 이나 금지된
> 조합 (`illegal_bins`) 을 필터링한다.

<!-- KO mirror of ../../how-to/cross-with-ignore-illegal.md -->

## TL;DR

| | |
|---|---|
| **목표** | `Cross(..., ignore_bins=[...], illegal_bins=[...])` clause로 SystemVerilog `binsof ... intersect ...` chain을 올바르게 emit. |
| **사용 시점** | Coverpoint cross product에 (a) 설계상 발생 불가한 조합 (`ignore_bins`), 또는 (b) 절대 발생하면 안 되는 조합 (`illegal_bins`) 이 있을 때. |
| **Key APIs** | `Cross`, clause schema `{"name", "terms"}`, term shape `(cp, value_spec[, negate])` |

이 페이지가 답하는 질문:

- `terms` list에 무엇이 들어가나?
- `value_spec`은 어떤 shape을 받나?
- 한 term을 negate 하려면?

## 개요

**역할**. Cross-level 필터는 cross matrix를 closure 가능한 크기로 유지한다. 각 clause는 하나의 SV `binsof(cp) intersect {...}` chain으로 변환되며, term들은 `&&`로 결합된다.

**다루지 않는 것**:

- Coverpoint별 `ignore_bins` — [`CoverPoint`](../../reference/coverage/coverpoint.md)에 직접 설정한다.
- 각 coverpoint에 맞는 `Bin*` 선택 → [bin-type-recipes.md](bin-type-recipes.md).

## Clause 구조

```python
{
    "name":  "<sv_identifier>",            # required
    "terms": [
        (<cp>, <value_spec>),              # 2-tuple
        (<cp>, <value_spec>, <negate>),    # 3-tuple
    ],
}
```

## 예제

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
```

> Verified: [`tests/pytest/test_cross.py`](../../../tests/pytest/test_cross.py)

## `value_spec` 형태

| 형태 | `intersect {...}` 내부에 emit 되는 것 |
|------|----------------------------------|
| `str` | spec as-is — 예: `"WRAP"`, `"1, 3, 5"`, `"[17:256]"` |
| `int` | 단일 값 — 예: `7` → `{7}` |
| `range` | step==1: `[start:stop-1]`; step>1: comma-joined |
| `list` / `tuple` / `set` | int + range mix를 comma-joined — 예: `{1, 3, [5:7]}` |
| `as_string(lang=LanguageType.SystemVerilog)` 메소드 있는 object | 렌더된 문자열을 그대로 사용 |

## Term negate

3-tuple 형태로 negate prefix 부착:

```python
{"name": "il_not_wr_at_0",
 "terms": [(cp_op, "WRITE", True), (cp_size, 0)]}
# illegal_bins il_not_wr_at_0 = !binsof(cp_op) intersect {WRITE} && binsof(cp_size) intersect {0};
```

## 관련 문서

- [reference/coverage/cross.md](../../reference/coverage/cross.md) — `Cross` API 전체.
- [reference/coverage/coverpoint.md](../../reference/coverage/coverpoint.md) — coverpoint별 ignore / illegal.
- [../../how-to/cross-with-ignore-illegal.md](../../how-to/cross-with-ignore-illegal.md) — English 원본.
