---
source: ../../explanations/bin-type-hierarchy.md
source_hash: bootstrap
title: Bin* 타입 계층
---
# `Bin*` 타입 계층

> `cocotbext-fcov`가 17개의 predefined bin 타입을 제공하는 이유와 서로의 관계.

<!-- KO mirror of ../../explanations/bin-type-hierarchy.md -->

## TL;DR

| | |
|---|---|
| **무엇** | 모든 `Bin*` 클래스는 `BinGroup`의 서브클래스이고, 상속 그래프는 어떤 shape들이 normalisation 로직을 공유하는지를 인코딩한다. |
| **읽는 시점** | 타입 목록이 너무 많아 보이고 mental map이 필요할 때. |
| **Mental hook** | atom (`BinItem`) → container (`BinGroup`) → pattern 서브클래스; "range family" vs "boundary family" vs "shape family". |

## 개요

`BinItem`은 atom — 한 named bin이 값, range, 또는 transition chain을 담는다. `BinGroup`은 container — `BinItem`들의 순서 있는 named dict. 17개의 predefined 클래스는 각각 하나의 생성자 specialisation이다: 패턴별 인자 (`range`-style positional, `Enum`, `min`/`max`, `width`, ...) 를 받아 normalised `BinGroup`을 내부에 둔다.

**핵심 의도**는 predefined 클래스들의 생성자를 **작게** — 패턴 하나당 클래스 하나 — 유지하면서, rendering / 동등성 / 병합 같은 무거운 로직은 `BinGroup`에서 공유하는 것이다. 결과적으로 사용자는 클래스 이름을 coverage-intent 선언처럼 고르면 (`BinMinMax`, `BinOneHot`, ...) SV emission이 기계적으로 따라온다.

## Atom: `BinItem`

`BinItem`이 담는 것:

- `items`: int / range / 중첩 `BinItem` 리스트.
- `next`: transition chain의 다음 link (optional).
- `name`, `num`, `width`, `prefix`, `format`: rendering metadata.

직접 사용은 드물다. 보통 값을 `BinGroup` (또는 `Bin*` 서브클래스) 에 전달하면 container가 자동으로 `BinItem`으로 wrap 한다.

## Container: `BinGroup`

`BinGroup`은 `Dict[str, BinItem]`이며 iteration / `[]` / `len` / `keys` / `values` / `items` 위임 + `+`로 병합을 지원한다. 생성자는 거의 모든 shape을 받는다 — dict, `(name, value)` pair list, bare value list, 다른 `BinGroup`, 심지어 bare `range`까지.

서브클래스는 container 동작을 override 하지 않고, 생성자만 override 한다.

## 세 family

Predefined `Bin*` 클래스들은 세 개의 loose family로 묶인다. 정확한 계보보다는 coverage 의도에 맞는 family를 고르면 된다.

### Range family — `range(*args)` spec에서 파생

```
BinGroup
├── BinSingle(value)              # 한 값/range당 한 bin
├── BinUniform(*args, num=)       # open-array range, num으로 분할
│   └── BinRange(*args)           # num=0 hardcoded alias
├── BinExp(*args, base=)          # exponential bucketing
└── BinDict(dict)                 # {name: value} mapping
    └── BinEnum(Enum)             # Enum에서 bin 생성
        └── BinBool()             # boolean 두-bin shortcut
```

### Boundary family — 명시적 `min` + `max` 경계 bin

```
BinUniform
└── BinMinMax(min, max, num=, ...)        # 경계 + uniform interior
    ├── BinMinMaxUniform                  # alias, 더 명확한 이름
    └── BinMinMaxExp(min, max, base=)     # 경계 + exponential interior
```

`BinMinMaxExp`는 `(BinExp, BinMinMax)`를 multi-inherit — 두 동작을 합성.

### Shape family — bit-level 구조에 묶인 패턴

```
BinGroup
├── BinWindow(window, width=, shift=)     # sliding bit pattern
│   └── BinOneHot(width=)                 # slot당 한 비트
├── BinDefault()                          # catch-all
├── BinOutOfSpec()                        # doc-only marker
├── BinBitwise(width=)                    # 각 bit별 0/1
└── BinTransition(*trans_bins)            # multi-bin transition
```

## 이 model이 깨지는 경계

- **`BinMinMaxExp`는 유일한 multi-inherit node**. 경계 bin + non-exponential interior가 필요하면 [`BinCustom`](../../reference/bins/group.md)으로 직접 만든다. 계층을 더 확장하는 것은 API 표면 비용 대비 가치가 없다고 판단되었다.
- **`BinOutOfSpec`은 SystemVerilog에 아무것도 emit 하지 않는다**. Markdown spec table에 "out of spec" 행이 들어가도록 하는 documentation-only marker.
- **Format string은 상속되지 않는다**. 각 클래스가 자체 default `format=`을 가진다 (`BinWindow` / `BinOneHot`은 `"x"`, 나머지는 `None`); coverpoint별로 override 가능.
- **`prefix` default도 다르다**. 대부분 `"bin"`이지만 `BinEnum`과 `BinBool`은 `None`이다 — 이름이 enum member에서 오기 때문.

## 관련 문서

- [reference/bins/group.md](../../reference/bins/group.md) — `BinGroup` API.
- [reference/bins/type.md](../../reference/bins/type.md) — 모든 서브클래스의 시그니처와 예제.
- [how-to/bin-type-recipes.md](../how-to/bin-type-recipes.md) — 실제 task에 맞는 클래스 선택.
- [../../explanations/bin-type-hierarchy.md](../../explanations/bin-type-hierarchy.md) — English 원본.
