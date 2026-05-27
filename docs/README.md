---
title: cocotbext-fcov documentation
---
# cocotbext-fcov documentation

Functional-coverage closure helpers for cocotb testbenches. Spec coverage models in Python; emit SystemVerilog `covergroup` declarations + Markdown coverage tables.

> 🇰🇷 [한국어](ko/index.md) · English below.

## Where to start

| If you want to ... | Open |
|---|---|
| Build your first coverage model end-to-end | [tutorials/first-coverage-model.md](tutorials/first-coverage-model.md) |
| Sample coverage from a running cocotb test | [how-to/sampling-in-cocotb.md](how-to/sampling-in-cocotb.md) |
| Look up a specific class / function | [reference/by-symbol.md](reference/by-symbol.md) |
| Understand the `Bin*` type hierarchy | [explanations/bin-type-hierarchy.md](explanations/bin-type-hierarchy.md) |

## Layout (Diátaxis)

- [`reference/`](reference/) — symbol-level surface, one page per class (plus [`sv-emission-model.md`](reference/sv-emission-model.md) for the SV emit shape).
- [`how-to/`](how-to/) — task-oriented recipes; each binds to a pytest case + a cocotb pilot.
- [`tutorials/`](tutorials/) — handheld walks; concrete deliverable at the end.
- [`explanations/`](explanations/) — conceptual orientation: class hierarchy ([`architecture.md`](explanations/architecture.md)) + Bin\* type tree.
- [`glossary.md`](glossary.md) — 12 term cross-reference.
- [`../examples/`](../examples/) — executable pilots (Verilator + VCS + Questa) bound to the how-to guides.
- [`../NOTICE.md`](../NOTICE.md) — third-party attribution.
- [`ko/`](ko/) — Korean mirror (how-to + tutorial + explanations + glossary).

## Install

```bash
pip install ./cocotbext-fcov
```

## See also

- [README.md](../README.md) — project elevator pitch + install + repo conventions.
- [GitHub](https://github.com/furiosa-ai/cocotbext-fcov) — issues + source.
