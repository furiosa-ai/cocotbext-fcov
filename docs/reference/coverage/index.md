---
title: coverage
---
# `cocotbext.fcov.coverage`

Coverage primitives. One page per class.

| Page | Symbols | Use it for |
|------|---------|------------|
| [coverpoint.md](coverpoint.md) | `CoverPoint` | Single SV `coverpoint` over a value-set spec. |
| [cross.md](cross.md) | `Cross` | SV `cross` over two or more `CoverPoint`s. |
| [covergroup.md](covergroup.md) | `CoverGroup` | Container of coverpoints + crosses → one SV `covergroup`. |
| [model.md](model.md) | `CoverageModel`, `CoverageCollector`, helpers | Top-level container → one SV module. |

## See also

- [../bins/](../bins/) — bin spec primitives consumed by `CoverPoint`.
- [../scripts/make-coverage.md](../scripts/make-coverage.md) — emit `.sv` + `.md` from `CoverageModel` instances.
