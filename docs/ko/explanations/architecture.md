---
source: ../../explanations/architecture.md
source_hash: bootstrap
title: Coverage class 계층
---
# Coverage class 계층

> 모든 reference 페이지가 이 페이지로 link 한다 — "이 class 는 어디에
> 위치하나?" 의 단일 출처. 다이어그램은 이 페이지에서만 한 번 보고,
> 다른 reference 페이지는 한 줄짜리 breadcrumb 만 보여준다.

<!-- KO mirror of ../../explanations/architecture.md -->

## TL;DR

| | |
|---|---|
| **무엇** | Python coverage spec → SystemVerilog `covergroup` → runtime hit count 로 이어지는 6-layer chain. |
| **읽는 시점** | Reference 페이지를 열었는데 inline breadcrumb (`**Position:** ...`) 만으로 부족할 때. |
| **Mental hook** | atom → container → coverpoint → covergroup → model → collector. |

## Chain

```
BinItem        ← atom: named bin 하나 (값, range, 또는 transition chain)
   │
   │ wrapped by
   ▼
BinGroup       ← container: BinItem 의 ordered dict; 17 개 predefined Bin* type 의 base
   │
   │ consumed as bins= by
   ▼
CoverPoint     ← value-set spec 하나에 대응되는 SystemVerilog `coverpoint`
   │
   │  +  Cross  (2 개 이상 CoverPoint 를 묶은 cross declaration 하나)
   ▼
CoverGroup     ← sample() 이 fire 되는 단위; SystemVerilog `covergroup` 하나
   │
   │ assembled into
   ▼
CoverageModel  ← SystemVerilog 모듈 하나 (make_coverage 가 emit)
   │
   │ connected to cocotb DUT handle via
   ▼
CoverageCollector
```

## 왜 6 layer 인가

각 layer 가 하나의 축을 factor out 한다:

- **`BinItem`** 은 value space (ints / ranges / transitions) 를 소유.
  사용자가 직접 만드는 일은 드물고, `BinGroup` 과 `Bin*` predefined
  type 이 값을 자동으로 wrap.
- **`BinGroup`** 은 bin set 의 naming + ordering + equality 를 소유.
  모든 `Bin*` predefined type 은 `BinGroup` 의 서브클래스로 생성자만
  특화.
- **`CoverPoint`** 가 bin 을 SV signal 하나에 binding + `ignore_bins`
  / `illegal_bins` 추가 + runtime `cp.value` driver 제공.
- **`Cross`** 는 coverpoint 의 spec 을 다시 쓰지 않고 결합.
- **`CoverGroup`** 은 coverpoint / cross 집합을 sample event 하나에
  묶고 SV `covergroup` declaration 하나를 emit.
- **`CoverageModel`** 은 covergroup 을 한 SV 모듈로 묶음 —
  `make_coverage` 가 `.sv` 파일을 쓰는 boundary.
- **`CoverageCollector`** 가 runtime glue: cocotb DUT handle 의
  `dut.<model_name>` 을 lookup 하고 모든 covergroup 의 signal +
  sample wire 를 Python `_drive` / `_sample` async loop 에 attach.

## Sample 호출의 흐름

```
cocotb test  -- cg.cp_val <= 1
              -- cg.sample()
                      │
                      ▼
Python (cocotbext-fcov)  CoverPoint._drive  →  _handler.value (wire) toggle
                                            +  cg_<name>_sample wire toggle
                      │
                      ▼
SystemVerilog (cov_model)  always @(cg_<name>_sample)
                                cg_<name>_inst.sample();
                      │
                      ▼
Simulator               매칭된 값에 대해 per-bin hit counter 증가
```

`always @(<sample wire>) <cg_inst>.sample();` 블록이 Python driver 와
SV runtime 사이의 다리. Verilator 에서는 이 블록을 `ifndef VERILATOR`
로 감싼다 — Verilator 5.038 ~ 5.049 가 covergroup `.sample()` 을
구현하지 않기 때문 (issue verilator/#7099). VCS / Questa 는 정상
실행하고 simulator 가 bin hit 을 기록한다.

## Pilot 별 chain 위치

| Pilot | Layer focus |
|---|---|
| `tests/cocotb/simple_dff/` | `BinBool` + `BinTransition` on a 1-bit Q — 가장 작은 pilot; chain wiring 검증. |
| `tests/cocotb/simple_counter/` | `BinRange` + `BinBool` + `Cross` — 첫 multi-coverpoint pilot. |
| `tests/cocotb/adder/` | `BinUniform` + `BinBitwise` + `BinBool` + `Cross` — `ref=` (한 wire 의 multi-axis). |
| `tests/cocotb/register_sampling/` | 6 Bin\* + Cross — register-file domain spread. |
| `tests/cocotb/opcode_cross/` | `BinEnum` + `BinExp` + `BinOneHot` + Cross + ignore/illegal_bins. |
| `tests/cocotb/matrix_multiplier/` | `BinUniform` + `BinMinMaxExp` (조합) + `BinMinMax` — range / magnitude 패턴. |

## 이 mental model 이 깨지는 경계

- **`BinItem` 을 user code 에서 직접 쓰는** 경우 — 대부분 `Bin*` type
  으로 대체 가능한 신호. Atom 이 public API 인 이유는 transition
  chain 을 hand-build 해야 할 때를 위함.
- **`CoverageModel` 한 모듈** — covergroup 이 수백 개라면 (block 별
  하나씩) 여러 `CoverageModel` 서브클래스 권고. 각자 별도 SV 모듈;
  `make_coverage` 파일을 여러 개 두는 것도 OK.
- **비표준 DUT shape 의 `CoverageCollector`** — collector 는
  `dut.<model_name>` 을 lookup; SV testbench 가 `cov_model` 을 깊은
  hierarchy 에 wrap 했다면 top-level dut 가 아닌 inner handle 을
  넘겨야 한다.

## 관련 문서

- [`../../reference/bins/`](../../reference/bins/) — `BinItem` / `BinGroup` /
  17 predefined `Bin*` type.
- [`../../reference/coverage/`](../../reference/coverage/) — `CoverPoint` /
  `Cross` / `CoverGroup` / `CoverageModel` / `CoverageCollector`.
- [`bin-type-hierarchy.md`](bin-type-hierarchy.md) — `Bin*` family 내부
  상속 tree (이 페이지의 chain view 와 orthogonal).
- [`../../tests/cocotb/README.md`](../../../tests/cocotb/README.md) —
  pilot 이 이 chain 에 어떻게 매핑되는가.
- [`../../explanations/architecture.md`](../../explanations/architecture.md) — English 원본.
