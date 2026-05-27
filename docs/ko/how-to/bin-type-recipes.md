---
source: ../../how-to/bin-type-recipes.md
source_hash: bootstrap
title: Coverage spec에 맞는 Bin* 선택
---
# Coverage spec에 맞는 `Bin*` 선택

> Cookbook: 실제 coverage task를 17개 predefined `Bin*` 패턴에 매핑한다.

<!-- KO mirror of ../../how-to/bin-type-recipes.md -->

## TL;DR

| | |
|---|---|
| **목표** | `BinGroup`을 직접 짜지 말고 — predefined 패턴 중 하나를 선택. |
| **사용 시점** | Bin 형태가 잘 알려진 분포 (range / exp / boundary / window / enum / ...) 와 일치할 때. |
| **Key APIs** | [bins/type.md](../../reference/bins/type.md)의 모든 클래스 |

이 페이지가 답하는 질문:

- "N-bit signal 의 모든 값을 cover 하고 싶다" — 어떤 `Bin*`?
- "exponential bucketing" — 어떤 `Bin*`?
- "endpoint + interior cover" — 어떤 `Bin*`?

## 결정 table

| Coverage 의도 | 사용 |
|---|---|
| 단일 값, sub-binning 없음 | `BinSingle(value)` |
| N-bit range 전체, open array 하나 | `BinUniform(N)` 또는 `BinRange(N)` |
| N-bit range 전체, `K` 개 sub-bin으로 분할 | `BinUniform(N, num=K)` |
| Subrange `[a, b)` | `BinUniform(a, b)` 또는 `BinRange(a, b)` |
| Enum / 명명된 값들 | `BinDict({...})` 또는 `BinEnum(EnumCls)` |
| Boolean | `BinBool()` |
| Exponential / log scale | `BinExp(stop, base=B)` |
| Endpoint + uniform interior | `BinMinMax(min, max, num=K)` |
| Endpoint + exponential interior | `BinMinMaxExp(min, max, base=B)` |
| One-hot bit pattern | `BinOneHot(width=W)` |
| Sliding bit pattern | `BinWindow(seed, width=W, shift=S)` |
| Default catch-all | `BinDefault()` |
| 각 bit당 `0`/`1` | `BinBitwise(width=W)` |
| Transition chain | `BinTransition((a, b, c), ...)` |
| "Out of spec" doc marker (SV emit 없음) | `BinOutOfSpec()` |

## 예제 모음

### Latency histogram (exponential)

```python
from cocotbext.fcov import CoverPoint, BinExp
cp_lat = CoverPoint(BinExp(1024, base=2), name="cp_latency")
```

> Verified: [`tests/pytest/test_bin_type.py`](../../../tests/pytest/test_bin_type.py)

### Boundary case 포함 burst length

```python
from cocotbext.fcov import CoverPoint, BinMinMax
cp_burst = CoverPoint(BinMinMax(min=1, max=256, num=6), name="cp_burst")
```

### Address one-hot decode

```python
from cocotbext.fcov import CoverPoint, BinOneHot
cp_addr_oh = CoverPoint(BinOneHot(width=8), name="cp_addr_onehot")
```

### Strobe transition (idle → request → response → idle)

```python
from cocotbext.fcov import CoverPoint, BinTransition
cp_strobe = CoverPoint(
    BinTransition((0, 1, 2, 0), (0, 1, 0)),
    name="cp_strobe",
)
```

### 여러 패턴 결합 (`BinGroup.__add__`)

```python
# 0..3은 4 개 single-value bin + 4..15에 boundary/exp 적용.
cp_a = CoverPoint(
    BinUniform(4, num=4) + BinMinMaxExp(min=4, max=15, base=2),
    name="cp_a",
)
# 8 개 bin emit:
#   bin_0_3[4] = {[0:3]};  bin_4 = {4};  bin_5_7 = {[5:7]};
#   bin_8_14 = {[8:14]};   bin_15 = {15};
```

*두 coverpoint 가 한 signal 을 공유*하려면 `ref=` 사용 — 참조:
[`reference/coverage/coverpoint.md`](../../reference/coverage/coverpoint.md#multi-axis-coverage-on-one-source-signal).

> Verified: [`tests/pytest/test_bin_type.py`](../../../tests/pytest/test_bin_type.py) · [`tests/pytest/test_bin_emit_snapshots.py`](../../../tests/pytest/test_bin_emit_snapshots.py)
>
> Verified (sim-hit): [`examples/matrix_multiplier/`](../../../examples/matrix_multiplier/) — `BinUniform` + `BinMinMaxExp` + `BinMinMax` ( `BinGroup.__add__` hybrid 포함 ) 를 2×2 matrix multiplier DUT 에서 검증.

## Predefined 패턴이 안 맞으면

[`BinGroup` / `BinCustom`](../../reference/bins/group.md)으로 직접 dict을 만든다.

## 관련 문서

- [reference/bins/type.md](../../reference/bins/type.md) — 모든 predefined 타입.
- [explanations/bin-type-hierarchy.md](../explanations/bin-type-hierarchy.md) — 왜 이 패턴들이 존재하고 어떻게 상속되나.
- [../../how-to/bin-type-recipes.md](../../how-to/bin-type-recipes.md) — English 원본.
