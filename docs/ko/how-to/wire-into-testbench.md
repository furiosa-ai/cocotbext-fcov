---
source: ../../how-to/wire-into-testbench.md
source_hash: bootstrap
title: cocotb testbench 에 cov_model wiring 하기
---
# `cov_model` 을 cocotb testbench 에 wiring 하기

> `make_coverage` 가 emit 한 SystemVerilog 모듈을 실행 중인 cocotb
> 테스트에 연결한다 — SV wrapper 모양, Python 쪽 동작, wire mismatch
> 시 대처법.

<!-- KO mirror of ../../how-to/wire-into-testbench.md -->

## TL;DR

| | |
|---|---|
| **목표** | cocotb 테스트 boot 후 DUT handle 에서 `cov_model` 찾아 sampling 시작. |
| **사용 시점** | `coverage_spec.py` 작성 + `make_coverage` 실행 후. 첫 `cg.sample()` 호출 이전. |
| **Key APIs** | `CoverageModel(name=...)`, `CoverageCollector(dut, cov_model=...)`, SV `tb_top.sv` wrapper 관례 |

이 페이지가 답하는 질문:
- SV testbench top 이 무엇을 instantiate 해야 하나?
- `CoverageCollector` 가 SV instance 를 어떻게 찾나?
- Compile 시 어떤 macro 가 필요?
- Wire 가 안 맞을 때 무엇이 잘못되나?

## 개요

**역할**. Python coverage spec 과 SV runtime 사이 wiring story. Spec
작성과 [architecture 다이어그램](../explanations/architecture.md)
이해 이후의 step.

**다루지 않는 것**:
- Spec 작성 → [`build-coverage-hierarchy.md`](build-coverage-hierarchy.md).
- Sampling cadence → [`sampling-in-cocotb.md`](sampling-in-cocotb.md).
- 정확한 emit layout → [`../../reference/sv-emission-model.md`](../../reference/sv-emission-model.md).

## Step 1 — `coverage.sv` 생성

```bash
make_coverage -f coverage_spec.py -sv coverage.sv -md coverage.md --overwrite
```

출력은 `` `ifdef COCOTBEXT_FCOV `` 로 gate — compile 시
`+define+COCOTBEXT_FCOV` 전달. Pilot 의
[`Makefile.common`](../../../examples/_lib/Makefile.common) 이 자동
처리.

## Step 2 — SV testbench wrapper

DUT 와 cov_model 모듈 **둘 다** instantiate. `cov_model` instance
이름은 Python `name=` 과 매칭 필수:

```sv
`timescale 1ns/1ps

module tb_top();
  // DUT 신호 + instance
  logic clk, rst;
  logic [31:0] data;
  my_dut dut(.clk(clk), .rst(rst), .data(data));

  // cov_model instance -- name == CoverageModel(name=...)
  cov_model cov_model();
endmodule
```

> Verified (sim-hit): [`examples/register_sampling/tb_top.sv`](../../../examples/register_sampling/tb_top.sv)

## Step 3 — cocotb collector

```python
import cocotb
from cocotbext.fcov import CoverageCollector
from coverage_spec import RegfileCovModel


class RegfileCollector(CoverageCollector):
    """Thin wrapper -- connect() 로직 상속."""


@cocotb.test()
async def test_regfile(dut):
    cov_model = RegfileCovModel(name="cov_model")
    collector = RegfileCollector(dut, cov_model=cov_model)

    cg = collector.cov.cg_regfile

    # ... stimulus + sampling ...
```

SV 측 instance 가 성공적으로 resolve 되면 collector 가
`Coverage enabled for cov_model` 로그 출력. `Coverage instance
cov_model does not exist in dut!` 가 보이면 — SV instance 이름이
model 이름과 다름. Step 2 확인.

> Verified (sim-hit): [`examples/register_sampling/tb_regfile.py`](../../../examples/register_sampling/tb_regfile.py)

## Step 4 — 다중 model testbench

Block 이 여러 coverage 도메인 (예: protocol + perf + SVA-style) 을
쓰면 wrapper 에 각각 instantiate 하고 collector 에 dict 전달:

```sv
module tb_top();
  my_dut dut(...);
  cov_protocol cov_protocol();
  cov_perf     cov_perf();
endmodule
```

```python
collector = TopCollector(
    dut,
    cov_model={
        "cov_protocol": ProtocolCovModel(),
        "cov_perf":     PerfCovModel(),
    },
)
```

각 model 이 dict key 로 collector 에서 접근 가능:
`collector.cov_protocol.cg_xxx`, `collector.cov_perf.cg_yyy`.

## Step 5 — Simulator 선택

| Simulator | Build | Run | Functional coverage |
|-----------|-------|-----|---------------------|
| **Verilator 5.038–5.042** | ✓ `-Wno-COVERIGN` + `ifndef VERILATOR` patch (`always @(sample) cg_inst.sample();` 라인) | ✓ | ✗ no-op (covergroup 미구현) |
| **VCS** | ✓ `-cm assert+...` | ✓ | ✓ `simv.vdb` → `urg` |
| **Questa** | ✓ `+cover=bcefxs` | ✓ `-coverage` | ✓ `cov_*.ucdb` → `vcover` |

`examples/_lib/Makefile.common` 이 `SIM=verilator/vcs/questa` 에
따라 자동 flag + patch 적용.

## 흔한 실패 mode

| 증상 | 원인 | 해결 |
|------|------|------|
| `Coverage instance cov_model does not exist in dut!` | SV instance 이름 불일치 | SV instance 이름을 `CoverageModel(name=...)` 와 일치 |
| `No coverpoint signal cg_xxx_cp_yyy` | Spec 에 `CoverPoint` 추가 했는데 `coverage.sv` 재생성 안 함 | `make_coverage` 재실행 (또는 `make coverage.sv`) |
| `Class method 'sample' not found in class 'cg_xxx'` | `ifndef VERILATOR` patch 없이 Verilator build | `_lib/Makefile.common` 사용 또는 동일 regex sub 적용 |
| `Identifier 'AND' has not been declared` | `Cross.ignore_bins`/`illegal_bins` `value_spec` 에 bin-name string 전달 | Integer 값 사용: `int(Op.AND)` |
| `binsof(None) intersect ...` | commit `769533f` 이전 cocotbext-fcov | Update; Cross cp-remap fix 가 그 commit 에 land |

## 관련 문서

- [`build-coverage-hierarchy.md`](build-coverage-hierarchy.md) — wiring 이전 design pass.
- [`sampling-in-cocotb.md`](sampling-in-cocotb.md) — wiring 이후 sample loop.
- [`../../reference/sv-emission-model.md`](../../reference/sv-emission-model.md) — `make_coverage` 가 emit 하는 정확한 module shape.
- [`../../reference/coverage/model.md`](../../reference/coverage/model.md) — `CoverageModel` + `CoverageCollector` API.
- [`../../examples/README.md`](../../../examples/README.md) — pilot 관례; 모든 pilot 가 본 how-to 의 worked example.
- [`../glossary.md`](../glossary.md) — 용어 정의.
- [`../../how-to/wire-into-testbench.md`](../../how-to/wire-into-testbench.md) — English 원본.
