---
source: ../README.md
source_hash: bootstrap
title: cocotbext-fcov 한국어 문서
---
# cocotbext-fcov 한국어 문서

cocotb testbench 를 위한 functional coverage closure 헬퍼. Python
으로 coverage model 을 선언하고, SystemVerilog `covergroup` +
Markdown coverage table 을 자동 emit 한다.

> 🇺🇸 [English](../README.md)

## 어디부터 시작하나

| 하고 싶은 것 | 열어볼 페이지 |
|---|---|
| 첫 coverage model 을 end-to-end 로 만든다 | [tutorials/first-coverage-model.md](tutorials/first-coverage-model.md) |
| 계층 구조에 따라 coverage spec 을 설계한다 | [how-to/build-coverage-hierarchy.md](how-to/build-coverage-hierarchy.md) |
| `cov_model` 을 cocotb testbench 에 wiring 한다 | [how-to/wire-into-testbench.md](how-to/wire-into-testbench.md) |
| 실행 중인 cocotb 테스트에서 coverage 를 sample 한다 | [how-to/sampling-in-cocotb.md](how-to/sampling-in-cocotb.md) |
| Cross + ignore / illegal bin 으로 필터링한다 | [how-to/cross-with-ignore-illegal.md](how-to/cross-with-ignore-illegal.md) |
| Coverage spec 에 맞는 `Bin*` 를 선택한다 | [how-to/bin-type-recipes.md](how-to/bin-type-recipes.md) |
| 6-layer class chain (BinItem→…→Collector) 을 이해한다 | [explanations/architecture.md](explanations/architecture.md) |
| 17 개 `Bin*` 종류의 상속 트리를 이해한다 | [explanations/bin-type-hierarchy.md](explanations/bin-type-hierarchy.md) |
| 용어 정의 | [glossary.md](glossary.md) |
| 특정 class / function 을 찾는다 (영문, KO 미러 없음) | [../reference/by-symbol.md](../reference/by-symbol.md) |
| API reference (영문, KO 미러 없음) | [../reference/](../reference/) |

## 레이아웃 (Diátaxis)

- [`how-to/`](how-to/) — task 지향 recipe; 5 페이지 KO 미러 완료.
- [`tutorials/`](tutorials/) — handheld walk; 1 페이지 KO 미러.
- [`explanations/`](explanations/) — 개념 정리; 2 페이지 KO 미러.
- [`glossary.md`](glossary.md) — 용어 정의 (KO 미러).
- Reference (`../reference/`) 는 영문만 유지 — 표면이 거의 영어
  identifier 라서 한국어로 mirror 가치가 낮다는 `TRANSLATION_POLICY.md`
  결정. 필요시 영문 페이지 직접 참조.

## 설치

```bash
pip install ./cocotbext-fcov
```

## 관련 문서

- [`TRANSLATION_POLICY.md`](TRANSLATION_POLICY.md) — KO 미러 번역 규칙.
- [`../README.md`](../README.md) — English 원본 README.
- [GitHub](https://github.com/furiosa-ai/cocotbext-fcov) — issues + source.
