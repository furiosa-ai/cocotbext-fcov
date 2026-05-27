---
title: Reference
---
# Reference

Information-oriented documentation. One page per public class, mirroring `cocotbext/fcov/` 1:1. Each page carries:

- **TL;DR table** — what + when to use + key links.
- **API summary table** — signature · returns · summary per public symbol.
- **Quick example + Usage patterns** — minimal runnable snippets bound to pytest cases via `> Verified:`.

Reference pages describe, not teach. Routes to other quadrants:

- **Task walkthroughs** → [`../how-to/`](../how-to/)
- **Learning sequences** → [`../tutorials/`](../tutorials/)
- **Conceptual orientation** → [`../explanations/`](../explanations/)

## Symbol index

- [by-symbol.md](by-symbol.md) — alphabetical lookup across every public symbol.

## Layout

- [bins/](bins/) — `BinItem`, `BinGroup`, predefined `Bin*` types.
  - [bins/item.md](bins/item.md) — `BinItem`, `LanguageType`.
  - [bins/group.md](bins/group.md) — `BinGroup`, `BinCustom`.
  - [bins/type.md](bins/type.md) — 16 specialised `Bin*` types (`BinSingle`, `BinUniform`, `BinRange`, `BinDict`, `BinEnum`, `BinBool`, `BinExp`, `BinMinMax`, `BinMinMaxUniform`, `BinMinMaxExp`, `BinWindow`, `BinOneHot`, `BinDefault`, `BinOutOfSpec`, `BinBitwise`, `BinTransition`) — plus `BinCustom` documented on `bins/group.md` for 17 total.
- [coverage/](coverage/) — coverage primitives.
  - [coverage/coverpoint.md](coverage/coverpoint.md) — `CoverPoint`.
  - [coverage/cross.md](coverage/cross.md) — `Cross`.
  - [coverage/covergroup.md](coverage/covergroup.md) — `CoverGroup`.
  - [coverage/model.md](coverage/model.md) — `CoverageModel`, `CoverageCollector`.
- [scripts/](scripts/) — CLI utilities.
  - [scripts/make-coverage.md](scripts/make-coverage.md) — generate `.sv` + `.md` from Python coverage models.
- [sv-emission-model.md](sv-emission-model.md) — the exact SystemVerilog module shape `make_coverage` emits; cross-cuts `bins/` + `coverage/`.
