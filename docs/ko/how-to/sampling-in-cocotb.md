---
source: ../../how-to/sampling-in-cocotb.md
source_hash: bootstrap
title: cocotb 테스트에서 coverage sample 하기
---
# cocotb 테스트에서 coverage sample 하기

> 실행 중인 cocotb 테스트에서 coverpoint 값을 driving 하고
> SystemVerilog `sample()` event를 trigger 해서 coverage를 기록한다.

<!-- KO mirror of ../../how-to/sampling-in-cocotb.md -->

## TL;DR

| | |
|---|---|
| **목표** | `CoverageCollector`를 DUT에 wiring 하고, transaction마다 coverpoint 값을 set 하고, `sample()`을 호출한다. |
| **사용 시점** | [첫 coverage model](../tutorials/first-coverage-model.md)을 만든 다음, 실제 stimulus로 채우고 싶을 때. |
| **Key APIs** | `CoverageCollector`, `CoverGroup.set`, `CoverGroup.sample`, `cp.value`, `cp <= value` |

이 페이지가 답하는 질문:

- Python `CoverGroup`이 SV-side covergroup instance에 어떻게 도달하나?
- `.sample()`은 언제 trigger 하나 — clock edge, handshake, transaction마다?
- precondition이 성립할 때만 sample 하려면?

## 개요

**역할**. Collector는 cocotb 쪽에 살고, [`make_coverage`](../../reference/scripts/make-coverage.md)가 emit 한 SV module은 DUT 쪽에 산다. 둘을 연결하는 것은 `connect()` 한 번이다. 그 다음에는 model의 모든 covergroup instance가 attribute 경로로 접근 가능하다.

**다루지 않는 것**:

- Model 구축 → [tutorials/first-coverage-model.md](../tutorials/first-coverage-model.md).
- Bin spec 선택 → [bin-type-recipes.md](bin-type-recipes.md).

## Collector wiring

```python
import cocotb
from cocotbext.fcov import CoverageCollector
from coverage_spec import TxnCovModel


class MyCollector(CoverageCollector):
    cov_model = TxnCovModel(name="cov_model")


@cocotb.test()
async def test_basic(dut):
    collector = MyCollector(dut, cov_model=TxnCovModel(name="cov_model"))
    # ... stimulus ...
```

> Verified: [`tests/pytest/test_coverage_model.py`](../../../tests/pytest/test_coverage_model.py)

## Transaction마다 sample

권장 패턴은 transaction당 `sample()` 한 번이다 (혹은 coverpoint가 register를 추적한다면 clock당).

```python
cg = collector.cov_model.cg_txn

cg.set(cp_opcode=op, cp_size=size, cp_secure=secure)
cg.sample()

# 혹은 __call__로 더 간결하게:
cg(cp_opcode=op, cp_size=size, cp_secure=secure)
```

## Precondition으로 sample

Coverage 대상이 아닌 transaction은 `sample()`을 건너뛴다:

```python
if not valid_handshake:
    return
cg(cp_opcode=op, cp_size=size, cp_secure=secure)
```

## 개별 update 시 `<=` 사용

```python
cg.cp_opcode <= op
cg.cp_size   <= size
cg.sample()
```

## 현재 값 read

```python
state = cg.get()  # {"cp_opcode": <Opcode.READ>, "cp_size": 3, "cp_secure": False}
```

## 관련 문서

- [tutorials/first-coverage-model.md](../tutorials/first-coverage-model.md) — 본 가이드가 sample 하는 model 구축.
- [reference/coverage/covergroup.md](../../reference/coverage/covergroup.md) — `CoverGroup` API.
- [reference/coverage/model.md](../../reference/coverage/model.md) — `CoverageCollector` API.
- [../../how-to/sampling-in-cocotb.md](../../how-to/sampling-in-cocotb.md) — English 원본.
