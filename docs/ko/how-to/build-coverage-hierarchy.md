---
source: ../../how-to/build-coverage-hierarchy.md
source_hash: bootstrap
title: Coverage 계층 build 하기
---
# Coverage 계층 build 하기

> 하나의 Python coverage spec 을 atomic `BinItem` 부터 `CoverageModel`
> 까지 step 별로 따라가면서 각 step 이 scaling 패턴 어디에 속하는지
> 매핑한다.

<!-- KO mirror of ../../how-to/build-coverage-hierarchy.md -->

## TL;DR

| | |
|---|---|
| **목표** | Coverage spec 의 각 piece 가 chain 의 어느 layer (atom / container / coverpoint / cross / covergroup / model) 에 속하는지 결정하고, 선택들이 compound 되는 양상 이해. |
| **사용 시점** | 새 coverage model 을 설계하거나 flat 한 것을 refactor 하거나 다른 사람의 spec 을 "이 layer 가 맞나?" 관점에서 review 할 때. |
| **Key APIs** | `BinItem`, `BinGroup`, [17 `Bin*` type](../../reference/bins/type.md), `CoverPoint`, `Cross`, `CoverGroup`, `CoverageModel` |

이 페이지가 답하는 질문:
- 어느 layer 가 naming / ordering / dispatch / sample timing 을 owner?
- 단일 Python list 가 언제 `Bin*` predefined type 이 되나?
- `ref=` 와 `Cross` 가 기존 coverpoint 를 어떻게 reuse 하나?
- `CoverageModel` 하나로 충분한가, 여러 개가 필요한가?

## 개요

**역할**. Step 별 design guide. 각 step 은 기존 pilot 중 하나에서
실제 패턴을 가져와 선택의 실제 reference 가 있도록 한다. Full
architecture 다이어그램은 [`explanations/architecture.md`](../explanations/architecture.md)
에 있다.

**다루지 않는 것**:
- 의도별 Bin-type 선택 → [`bin-type-recipes.md`](bin-type-recipes.md).
- Runtime sample() 경로 → [`sampling-in-cocotb.md`](sampling-in-cocotb.md).
- DUT ↔ cov_model wrapper plumbing → [`wire-into-testbench.md`](wire-into-testbench.md).

## Step 1 — Atom: `BinItem` (직접 사용 드물다)

대부분 user 는 `BinItem` 을 직접 만들지 않는다. Atomic layer 가
존재하는 이유:

- `CoverPoint(...)` 에 전달된 list 가 자동으로 `BinItem` 이 되도록
- transition chain 을 `>>` / `<<` 로 hand-build 할 수 있도록 (inline
  `"=>"` shorthand 가 어색할 때)

직접 `BinItem` 사용은 흔하지 않아 docs-boost pilot 중 어느 것도
사용 안 함.

> Verified: [`tests/pytest/test_bin_item.py`](../../../tests/pytest/test_bin_item.py)

## Step 2 — Container: `Bin*` type 선택

기본 선택은 17 개 [`Bin*` predefined type](../../reference/bins/type.md)
중 하나 — 한 공통 패턴 (range, enum, exponential, min/max, one-hot,
transition, ...) 에 대해 `BinGroup` 생성자를 특화한 것.
[`bin-type-recipes.md`](bin-type-recipes.md) 가 decision table.

어느 것도 안 맞으면 `BinGroup({...})` 또는 `BinCustom({...})` 으로
fallback 하고 bin 이름을 명시.

> Verified: [`tests/pytest/test_bin_emit_snapshots.py`](../../../tests/pytest/test_bin_emit_snapshots.py)

## Step 3 — 한 signal, 한 관찰: `CoverPoint`

각 `Bin*` 를 `CoverPoint` 로 감싼다. CoverPoint 가 owner:

- bin set 의 **signal**,
- 선택적 `ignore_bins` / `illegal_bins`,
- Python 측 `cp.value = ...` driver,
- SV 측 `<group>_<cp>` wire.

**같은 signal 의 multi-axis**: `ref=` 로 wire 공유.

```python
cp_a_exp     = CoverPoint(BinExp(16, base=2))
cp_a_bitwise = CoverPoint(BinBitwise(4), ref=cp_a_exp)
```

> Verified (sim-emit): [`examples/adder/coverage_spec.py`](../../../examples/adder/coverage_spec.py)

## Step 4 — 조합: `Cross`

각 coverpoint coverage 만으로 부족할 때 — 값들의 *조합* 을 verify
하고 싶을 때 — `Cross` 추가:

```python
cx_op_addr = Cross([cp_op, cp_addr], name="cx_op_addr")
```

Cross 도 `ignore_bins` / `illegal_bins` 를 carry. **term 의
`value_spec` 에는 bin 이름 아닌 integer 값 사용** (SV LRM 19.5):

```python
Cross([cp_op, cp_zero],
      ignore_bins=[{"name": "ig_and_zero",
                    "terms": [(cp_op, int(Op.AND)), (cp_zero, 1)]}])
```

> Verified (sim-emit): [`examples/opcode_cross/coverage_spec.py`](../../../examples/opcode_cross/coverage_spec.py)

## Step 5 — Group: `CoverGroup`

`CoverGroup` 서브클래스를 만들고 `CoverPoint` + `Cross` 를 **class
attribute** 로 attach. 서브클래스가 재사용 가능한 template 가 됨 —
logical instance 당 한 번 instantiate.

```python
class RegfileCoverGroup(CoverGroup):
    cp_addr  = CoverPoint(BinDict({"R0": 0, "R1": 1, "R2": 2, "R3": 3}))
    cp_op    = CoverPoint(BinEnum(Op))
    cx_op_addr = Cross([cp_op, cp_addr])
```

Per-instance hit count 는 독립적 — 같은 `CoverGroup` 서브클래스의
`cg_chan0` 과 `cg_chan1` 이 별도 hit bucket 추적.

> Verified (sim-hit): [`examples/register_sampling/coverage_spec.py`](../../../examples/register_sampling/coverage_spec.py)

## Step 6 — Module: `CoverageModel`

Model 이 1+ covergroup *instance* 를 `make_coverage` 가 작성하는
SV 모듈 하나에 묶는다. 단일 project 는 보통 testbench block 당 한
model.

```python
class RegfileCovModel(CoverageModel):
    cg_regfile = RegfileCoverGroup()

cov_model = RegfileCovModel(name="cov_model")
```

Module-level `cov_model` instance 가 `make_coverage` 가 파일을 walk
할 때 찾는 대상.

> Verified (sim-hit): [`examples/register_sampling/coverage_spec.py`](../../../examples/register_sampling/coverage_spec.py)

## 언제 여러 model 로 split 하나

| Signal | Split |
|--------|-------|
| 다른 testbench block (예: AXI vs APB) | block 당 한 model |
| 다른 sample cadence (예: cycle-level vs transaction-level) | 보통 split — 각 model 이 sample wire 하나 |
| 같은 block + 같은 cadence + > 100 covergroup | build time 위한 optional split |

각 model 이 `coverage.sv` 에서 별도 `module <name> ()` 가 됨. cocotb
[`CoverageCollector`](../../reference/coverage/model.md) 는 multi-model
setup 을 위해 `{name: CoverageModel}` dict 를 accept.

## 관련 문서

- [`../tutorials/first-coverage-model.md`](../tutorials/first-coverage-model.md) — end-to-end happy-path tutorial.
- [`bin-type-recipes.md`](bin-type-recipes.md) — Step 2 에서 어느 `Bin*` 를 고를지.
- [`sampling-in-cocotb.md`](sampling-in-cocotb.md) — runtime sample-and-hit 경로.
- [`wire-into-testbench.md`](wire-into-testbench.md) — DUT testbench 에 `cov_model` wrap.
- [`../explanations/architecture.md`](../explanations/architecture.md) — full 다이어그램 + sample-flow walkthrough.
- [`../glossary.md`](../glossary.md) — 용어 정의.
- [`../../how-to/build-coverage-hierarchy.md`](../../how-to/build-coverage-hierarchy.md) — English 원본.
