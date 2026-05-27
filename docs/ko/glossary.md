---
source: ../glossary.md
source_hash: bootstrap
title: Glossary (용어집)
---
# Glossary — 용어집

용어 수준 cross-reference. Reference 와 how-to 페이지가 처음 등장 시
모든 용어를 이 페이지로 link 한다.

> 🇺🇸 [English](../glossary.md)

## bin

가장 작은 coverage 단위 — 값들의 named set. cocotbext-fcov 에서는 단일
bin 이 [`BinItem`](../reference/bins/item.md) 으로 저장되고, 여러 bin
(각자 이름) 이 [`BinGroup`](../reference/bins/group.md) 안에 모인다.
SystemVerilog 측에서는 각 bin 이 `coverpoint` 안의
`bins <name> = {<values>}` 한 줄이 된다.

## BinItem / BinGroup / Bin\*

Bin 추상화의 세 레이어:

- **`BinItem`** — named bin 하나. Atomic.
- **`BinGroup`** — `BinItem` 의 ordered named container.
- **`Bin*`** — 17 개 `BinGroup` 서브클래스 (`BinSingle`, `BinUniform`,
  `BinRange`, `BinDict`, `BinEnum`, `BinBool`, `BinExp`, `BinMinMax`,
  `BinMinMaxUniform`, `BinMinMaxExp`, `BinWindow`, `BinOneHot`,
  `BinDefault`, `BinOutOfSpec`, `BinBitwise`, `BinTransition`,
  `BinCustom`) — 각각 한 가지 패턴에 특화된 생성자.

참조: [`reference/bins/`](../reference/bins/),
[`explanations/bin-type-hierarchy.md`](explanations/bin-type-hierarchy.md).

## coverpoint

한 관찰 표면 — 하나의 signal 을 하나의 bin set 으로 sampling.
cocotbext-fcov 의 [`CoverPoint`](../reference/coverage/coverpoint.md) 가
`bins` + 선택적 `ignore_bins` / `illegal_bins` 를 선언한다. SV 측에서는
`<name>: coverpoint <signal> { <bins...> }`.

## cross

**둘 이상의** 기존 coverpoint 의 조합 coverage. 각 bin set 의
cross-product 를 캡처. cocotbext-fcov 는 [`Cross`](../reference/coverage/cross.md)
사용; SV 는 `<name>: cross <cp1>, <cp2>, ...;` emit.

## covergroup

같은 sample 이벤트에서 함께 fire 하는 coverpoint + cross 의 named
group. cocotbext-fcov 는 [`CoverGroup`](../reference/coverage/covergroup.md);
SV 는 `covergroup <name>; ... endgroup`.

## sample / hit / closure

- **sample** — 한 observation 을 기록. Python: `cg.sample()`. SV:
  `cg_inst.sample();`.
- **hit** — bin 이 값-매치 sample 을 최소 1 회 받은 상태. Hit count =
  매치 sample 의 수.
- **closure** — spec 의 모든 bin 이 ≥ 1 hit. Coverage closure 가
  verification 목표.

## coverage model

여러 covergroup 을 단일 SV 모듈로 묶는 `CoverageModel` 서브클래스 —
`make_coverage` 가 출력하는 단위. 참조:
[`reference/coverage/model.md`](../reference/coverage/model.md).

## coverage collector

Python coverage model 과 cocotb DUT handle 사이의 runtime glue.
[`CoverageCollector`](../reference/coverage/model.md) 를 서브클래스로
만들고 `@cocotb.test` 안에서 인스턴스화하면, 모든 covergroup 이
SV 측 `cov_model` 인스턴스에 binding 된다.

## ignore_bins

Hit 되더라도 coverage 에 count 하지 않을 bin (또는 cross 에 대한
조합). Simulator 가 조용히 drop. 관찰이 uninteresting 할 때 사용
(예: all-zero op + zero result 는 trivially true).

## illegal_bins

**절대** hit 되면 안 되는 bin (또는 조합). Simulator 가 hit 시
error 처리. 조합이 design bug 를 시사할 때 사용.

## ref= (CoverPoint)

[`CoverPoint`](../reference/coverage/coverpoint.md) 의 keyword argument —
emit pipeline 에게 새 wire 선언 대신 기존 coverpoint 의 wire 재사용을
요청. 두 coverpoint 가 같은 SV signal 을 sampling 하되 다른 bin set
적용 — 예: 같은 input 에 `BinExp` 크기 bucket *과* `BinOneHot` 패턴
양쪽.

## sim-emit / sim-hit

Pilot 이 사용하는 `> Verified (sim-...)` binding 의 두 단계:

- **`sim-emit`** — 생성된 SV 가 parse + compile 되고, cocotb
  testbench 가 boot 되며, `cg.sample()` 호출이 exception 없이 도달.
  Verilator 5.038 ~ 5.042 가 이 수준까지만 제공 — covergroup hit
  counting 이 no-op (issue verilator/#7099).
- **`sim-hit`** — commercial simulator (VCS / Questa / Xcelium) 가
  실제 bin hit count 를 기록.

참조: [`../../tests/cocotb/README.md`](../../tests/cocotb/README.md).

## make_coverage

cocotbext-fcov 가 제공하는 CLI. Python 파일을 walk 해서
`CoverageModel` 인스턴스를 찾고 해당 `coverage.sv` + `coverage.md`
(spec table) 를 생성. 참조:
[`reference/scripts/make-coverage.md`](../reference/scripts/make-coverage.md).

## COVERIGN

Verilator warning class — *"이 covergroup construct 는 syntax 만
parse 하고 runtime 에는 ignore 한다"*. cocotbext-fcov pilot 은
warning 이 Verilator build 를 막지 않도록 `-Wno-COVERIGN` 으로 실행.
참조: [`explanations/architecture.md`](explanations/architecture.md).

## BASH_ENV

Bash 환경 변수 — set 되면 모든 비대화형 bash subshell 이 지정된
파일을 source 한다. 일부 host 는 `BASH_ENV=/etc/environment` 를
전역 set 해서 `PATH` 가 reset 되고 cocotb 의 재귀 `$(MAKE)` 안에서
EDA 도구 lookup 이 깨진다. `tests/cocotb/_lib/Makefile.common` 이
`BASH_ENV` 를 unset 하여 이를 무효화한다.
