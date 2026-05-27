# Symbol Index

> Alphabetical lookup for every public class / function re-exported
> from `cocotbext.fcov` (top-level `__init__.py`). Method-level rows
> are grouped with their class — check the class's page for the full
> list. CLI flags live on each `scripts/*.md` page.

**Total:** 27 top-level public symbols across 9 pages.
`LanguageType` (a public enum on [`bins/item.md`](bins/item.md#languagetype-enum))
is reachable via `from cocotbext.fcov.bins.item import LanguageType` but is
not re-exported from the top level.

| Symbol | Page | Summary |
|--------|------|---------|
| `BinBitwise` | [bins/type.md](bins/type.md#binbitwise) | Per-bit 0/1 coverage spec for a width-bit signal. |
| `BinBool` | [bins/type.md](bins/type.md#binbool) | Boolean two-bin set (`FALSE = 0`, `TRUE = 1`). |
| `BinCustom` | [bins/group.md](bins/group.md#bincustom) | Hand-curated bin set with no auto-naming. |
| `BinDefault` | [bins/type.md](bins/type.md#bindefault) | Single default catch-all bin. |
| `BinDict` | [bins/type.md](bins/type.md#bindict) | Bin set built from `{name: value}` mapping. |
| `BinEnum` | [bins/type.md](bins/type.md#binenum) | Bin set derived from a Python `Enum`. |
| `BinExp` | [bins/type.md](bins/type.md#binexp) | Exponential-bucket bin set over `range(*args)`. |
| `BinGroup` | [bins/group.md](bins/group.md#bingroup) | Ordered named container of `BinItem` instances. |
| `BinItem` | [bins/item.md](bins/item.md#binitem) | A single named bin: values / ranges / transition chain. |
| `BinMinMax` | [bins/type.md](bins/type.md#binminmax) | Uniform bins with explicit boundary bins on `min`/`max`. |
| `BinMinMaxExp` | [bins/type.md](bins/type.md#binminmaxexp) | Exponential bins with explicit boundary bins on `min`/`max`. |
| `BinMinMaxUniform` | [bins/type.md](bins/type.md#binminmaxuniform) | Alias for `BinMinMax`. |
| `BinOneHot` | [bins/type.md](bins/type.md#binonehot) | One-hot bin set across `width` bits. |
| `BinOutOfSpec` | [bins/type.md](bins/type.md#binoutofspec) | Documentation-only marker for out-of-spec rows. |
| `BinRange` | [bins/type.md](bins/type.md#binrange) | Open-array range bin (no per-value sub-binning). |
| `BinSingle` | [bins/type.md](bins/type.md#binsingle) | One coverage bin around a single value or range. |
| `BinTransition` | [bins/type.md](bins/type.md#bintransition) | Multi-bin transition coverage spec. |
| `BinUniform` | [bins/type.md](bins/type.md#binuniform) | Range bin split evenly via `num`. |
| `BinWindow` | [bins/type.md](bins/type.md#binwindow) | Sliding-window bit-pattern bin set. |
| `compact_index` | [coverage/model.md](coverage/model.md#helpers) | Compact a sparse index list into `range`s where contiguous. |
| `CoverageCollector` | [coverage/model.md](coverage/model.md#collector-lifecycle-cocotb) | Base class binding a coverage model to a cocotb DUT. |
| `CoverageModel` | [coverage/model.md](coverage/model.md) | Top-level container of `CoverGroup`s; emits one SV module. |
| `CoverGroup` | [coverage/covergroup.md](coverage/covergroup.md#covergroup) | Container of `CoverPoint`s + `Cross`es; emits one SV `covergroup`. |
| `CoverPoint` | [coverage/coverpoint.md](coverage/coverpoint.md#coverpoint) | Single SV `coverpoint` over a value-set spec. |
| `Cross` | [coverage/cross.md](coverage/cross.md#cross) | SV `cross` over two or more `CoverPoint`s. |
| `get_markdown_list` | [coverage/model.md](coverage/model.md#helpers) | Render a traversed coverage tree as Markdown list. |
| `traverse_type` | [coverage/model.md](coverage/model.md#helpers) | Walk a Python object tree yielding instances of a target class. |
