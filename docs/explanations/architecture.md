---
title: Coverage class hierarchy
---
# Coverage class hierarchy

> Every reference page links here for "where does this class sit?" Use this
> diagram once; every other ref page just shows a one-line breadcrumb.

<!-- KO mirror: see ko/explanations/architecture.md -->

## TL;DR

| | |
|---|---|
| **What** | The six-layer chain that takes a Python coverage spec to a SystemVerilog `covergroup` and back to runtime hit counts. |
| **Read this when** | You opened a reference page and the inline breadcrumb (`**Position:** ...`) is not enough. |
| **Mental hooks** | atom → container → coverpoint → covergroup → model → collector. |

## The chain

```
BinItem        ← atom: one named bin (values, ranges, or transition chain)
   │
   │ wrapped by
   ▼
BinGroup       ← container: ordered dict of BinItem; base for 17 predefined Bin* types
   │
   │ consumed as bins= by
   ▼
CoverPoint     ← one SystemVerilog `coverpoint` over a value-set spec
   │
   │  +  Cross  (≥ 2 CoverPoints combined into one cross declaration)
   ▼
CoverGroup     ← one SystemVerilog `covergroup`; the unit at which sample() fires
   │
   │ assembled into
   ▼
CoverageModel  ← one SystemVerilog module (emitted by `make_coverage`)
   │
   │ connected to the cocotb DUT handle via
   ▼
CoverageCollector
```

## Why six layers

Each layer factors out one axis:

- **`BinItem`** owns the value space (ints / ranges / transitions). End users
  rarely construct it directly; `BinGroup` and the `Bin*` predefined types wrap
  values automatically.
- **`BinGroup`** owns naming + ordering + equality of a bin set. Every `Bin*`
  predefined type subclasses `BinGroup` and only specialises the constructor.
- **`CoverPoint`** binds bins to one SV signal + adds `ignore_bins` /
  `illegal_bins` + the runtime `cp.value` driver.
- **`Cross`** combines coverpoints without rewriting either's spec.
- **`CoverGroup`** binds a set of coverpoints / crosses to one sample event and
  emits one SV `covergroup` declaration.
- **`CoverageModel`** packs covergroups into one SV module — the boundary at
  which `make_coverage` writes a `.sv` file.
- **`CoverageCollector`** is the runtime glue: it looks up `dut.<model_name>`
  in the cocotb DUT handle and attaches every covergroup's signal + sample
  wires to Python-side `_drive` / `_sample` async loops.

## How a sample call flows

```
cocotb test  -- cg.cp_val <= 1
              -- cg.sample()
                      │
                      ▼
Python (cocotbext-fcov)  CoverPoint._drive  →  toggles _handler.value (wire)
                                            +  toggles cg_<name>_sample wire
                      │
                      ▼
SystemVerilog (cov_model)  always @(cg_<name>_sample)
                                cg_<name>_inst.sample();
                      │
                      ▼
Simulator               increments the per-bin hit counter for the matched value
```

The `always @(<sample wire>) <cg_inst>.sample();` block is the bridge between
the Python driver and the SV runtime. On Verilator this block is gated behind
`` `ifndef VERILATOR `` because Verilator 5.038–5.049 does not implement
covergroup `.sample()` (issue verilator/#7099). On VCS / Questa the block runs
normally and the simulator records bin hits.

## Where each pilot sits in the chain

| Pilot | Layer focus |
|---|---|
| `tests/cocotb/simple_dff/` | `BinBool` + `BinTransition` on a 1-bit register's `Q` — the smallest pilot; proves the chain is wired. |
| `tests/cocotb/simple_counter/` | `BinRange` + `BinBool` + `Cross` — first multi-coverpoint pilot. |
| `tests/cocotb/adder/` | `BinUniform` + `BinBitwise` + `BinBool` + `Cross` — `ref=` (multi-axis on one wire). |
| `tests/cocotb/register_sampling/` | 6 Bin\* + Cross — register-file domain spread. |
| `tests/cocotb/opcode_cross/` | `BinEnum` + `BinExp` + `BinOneHot` + Cross + ignore/illegal_bins. |
| `tests/cocotb/matrix_multiplier/` | `BinUniform` + `BinMinMaxExp` (combined) + `BinMinMax` — range / magnitude patterns. |

## When this model breaks down

- **`BinItem` directly in user code** — almost always a sign you should be using
  a `Bin*` type. The atom is exposed in the public API mostly so transition
  chains can be hand-built when the convenience constructors do not fit.
- **`CoverageModel` as a single module** — when a project has hundreds of
  covergroups, you may want multiple `CoverageModel` subclasses (one per
  block). Each becomes its own SV module; multiple `make_coverage` files are
  fine.
- **`CoverageCollector` with a non-standard DUT shape** — the collector looks
  up `dut.<model_name>`; when the SV testbench wraps `cov_model` deep in a
  hierarchy, you need to pass the inner handle, not the top-level dut.

## See also

- [`../reference/bins/`](../reference/bins/) — `BinItem` / `BinGroup` / 17
  predefined `Bin*` types.
- [`../reference/coverage/`](../reference/coverage/) — `CoverPoint` / `Cross`
  / `CoverGroup` / `CoverageModel` / `CoverageCollector`.
- [`bin-type-hierarchy.md`](bin-type-hierarchy.md) — the inheritance tree
  *within* the `Bin*` family (orthogonal to this page's chain view).
- [`../../tests/cocotb/README.md`](../../tests/cocotb/README.md) — how the
  pilots map onto this chain.
