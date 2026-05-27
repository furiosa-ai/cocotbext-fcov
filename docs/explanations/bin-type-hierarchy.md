---
title: The Bin* type hierarchy
---
# The `Bin*` type hierarchy

> Why `cocotbext-fcov` ships seventeen predefined bin types and how they relate.

<!-- KO mirror: see ko/explanations/bin-type-hierarchy.md -->

## TL;DR

| | |
|---|---|
| **What** | Every `Bin*` class is a `BinGroup` subclass; the inheritance graph encodes which shapes share normalisation logic. |
| **Read this when** | The reference list of types feels overwhelming and you want a mental map. |
| **Mental hooks** | Atom (`BinItem`) → container (`BinGroup`) → pattern subclasses; "range family" vs "boundary family" vs "shape family". |

## Overview

`BinItem` is the atom — one named bin holding values, ranges, or a transition chain. `BinGroup` is the container — an ordered named dict of `BinItem`s. The seventeen predefined classes are each one constructor specialisation: they take pattern-specific arguments (`range`-style positional args, an `Enum`, `min`/`max`, `width`, ...) and stuff a normalised `BinGroup` underneath.

**The point** of the hierarchy is to keep the predefined classes' constructors **small** — one pattern per class — while sharing all the heavy rendering, equality, and merging logic in `BinGroup`. The result is a library where a user can pick a class name as a coverage-intent declaration (`BinMinMax`, `BinOneHot`, ...) and the SV emission follows mechanically.

## The atom: `BinItem`

A `BinItem` holds:

- `items`: a list of ints / ranges / nested `BinItem`s.
- `next`: optional pointer to the next link in a transition chain.
- `name`, `num`, `width`, `prefix`, `format`: rendering metadata.

It is rarely used directly. End users normally hand values to a `BinGroup` (or a `Bin*` subclass) and let the container wrap them in `BinItem`s automatically.

## The container: `BinGroup`

A `BinGroup` is a `Dict[str, BinItem]` with iteration / `[]` / `len` / `keys` / `values` / `items` delegates, plus `+` for merging. Its constructor accepts almost any shape — dict, list of `(name, value)` pairs, list of bare values, another `BinGroup`, even a bare `range` as syntactic sugar.

Subclasses don't override the container behaviour; they only override the constructor.

## The three families

Predefined `Bin*` classes cluster into three loose families. Names matter more than precise lineage — pick the family that matches your coverage intent.

### Range family — derived from a `range(*args)` spec

```
BinGroup
├── BinSingle(value)              # one bin around one value/range
├── BinUniform(*args, num=)       # open-array range, split via num
│   └── BinRange(*args)           # alias with num=0 hardcoded
├── BinExp(*args, base=)          # exponential bucketing
└── BinDict(dict)                 # mapping {name: value}
    └── BinEnum(Enum)             # bins from an Enum
        └── BinBool()             # boolean two-bin shortcut
```

### Boundary family — explicit `min` + `max` boundary bins

```
BinUniform
└── BinMinMax(min, max, num=, ...)        # boundary + uniform interior
    ├── BinMinMaxUniform                  # alias, clearer name
    └── BinMinMaxExp(min, max, base=)     # boundary + exponential interior
```

`BinMinMaxExp` multi-inherits `(BinExp, BinMinMax)` — it composes both behaviours.

### Shape family — patterns tied to bit-level structure

```
BinGroup
├── BinWindow(window, width=, shift=)     # sliding bit pattern
│   └── BinOneHot(width=)                 # one bit per slot
├── BinDefault()                          # catch-all
├── BinOutOfSpec()                        # doc-only marker
├── BinBitwise(width=)                    # per-bit 0/1
└── BinTransition(*trans_bins)            # multi-bin transition
```

## When this model breaks down

- **`BinMinMaxExp` is the only multi-inheritance node.** If you need *both* boundary bins and a non-exponential interior bucketing, write a [`BinCustom`](../reference/bins/group.md) — extending the hierarchy further has not been worth the API-surface cost.
- **`BinOutOfSpec` emits nothing in SystemVerilog.** It is documentation-only — present so the Markdown spec table can carry an "out of spec" row.
- **Format strings are not inherited.** Each class sets its own default `format=` (`"x"` for `BinWindow` / `BinOneHot`, `None` everywhere else); override per coverpoint when needed.
- **`prefix` defaults vary.** Most classes use `"bin"`; `BinEnum` and `BinBool` default to `None` because their names come from the enum members.

## See also

- [../reference/bins/group.md](../reference/bins/group.md) — `BinGroup` API.
- [../reference/bins/type.md](../reference/bins/type.md) — every subclass with its signature + example.
- [../how-to/bin-type-recipes.md](../how-to/bin-type-recipes.md) — picking the right class for a real task.
