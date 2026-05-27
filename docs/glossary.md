---
title: Glossary
---
# Glossary

Term-level cross-reference. The reference and how-to pages link
**every term** that appears here back to this page on first use.

> 🇰🇷 [한국어](ko/glossary.md) · English below.

## bin

The smallest unit of coverage — a named set of values. In
cocotbext-fcov a single bin is held by a [`BinItem`](reference/bins/item.md);
several bins (each with its own name) live inside a
[`BinGroup`](reference/bins/group.md). On the SystemVerilog side
each bin becomes one `bins <name> = {<values>}` line inside a
`coverpoint`.

## BinItem / BinGroup / Bin\*

The three layers of the bin abstraction:

- **`BinItem`** — one named bin. Atomic.
- **`BinGroup`** — ordered named container of `BinItem`s.
- **`Bin*`** — 17 `BinGroup` subclasses (`BinSingle`, `BinUniform`,
  `BinRange`, `BinDict`, `BinEnum`, `BinBool`, `BinExp`, `BinMinMax`,
  `BinMinMaxUniform`, `BinMinMaxExp`, `BinWindow`, `BinOneHot`,
  `BinDefault`, `BinOutOfSpec`, `BinBitwise`, `BinTransition`,
  `BinCustom`) that specialise the constructor for one common
  pattern.

See [`reference/bins/`](reference/bins/) and
[`explanations/bin-type-hierarchy.md`](explanations/bin-type-hierarchy.md).

## coverpoint

A single observation surface — one signal sampled into one set of
bins. In cocotbext-fcov a [`CoverPoint`](reference/coverage/coverpoint.md)
declares `bins` + optional `ignore_bins` / `illegal_bins`. On the SV
side it becomes `<name>: coverpoint <signal> { <bins...> }`.

## cross

A combination coverpoint over **two or more** existing coverpoints.
Captures the cross-product of their bin sets. cocotbext-fcov uses
[`Cross`](reference/coverage/cross.md); SV emits
`<name>: cross <cp1>, <cp2>, ...;`.

## covergroup

A named group of coverpoints + crosses that fire on the same
sample event. cocotbext-fcov calls this a
[`CoverGroup`](reference/coverage/covergroup.md); SV emits
`covergroup <name>; ... endgroup`.

## sample / hit / closure

- **sample** — record one observation. Python: `cg.sample()`. SV:
  `cg_inst.sample();`.
- **hit** — a bin received at least one sample matching its value
  set. Hit count = number of matching samples.
- **closure** — every bin in the spec has ≥ 1 hit. Coverage closure
  is the verification goal.

## coverage model

A `CoverageModel` subclass that bundles several covergroups into a
single SV module — the unit `make_coverage` writes out. See
[`reference/coverage/model.md`](reference/coverage/model.md).

## coverage collector

The runtime glue between a Python coverage model and a cocotb DUT
handle. Subclass [`CoverageCollector`](reference/coverage/model.md),
instantiate inside a `@cocotb.test`, and it binds every covergroup
to the SV-side `cov_model` instance.

## ignore_bins

A bin (or combination of bins, for cross) that should *not* count
toward coverage even if hit. The simulator quietly drops it. Use
when an observation is uninteresting (e.g. all-zero op + zero
result is trivially true).

## illegal_bins

A bin (or combination) that should *never* be hit. The simulator
flags any hit as an error. Use when the combination would indicate
a design bug.

## ref= (CoverPoint)

A keyword argument on [`CoverPoint`](reference/coverage/coverpoint.md)
that asks the emit pipeline to reuse the wire of an existing
coverpoint instead of declaring a new one. The two coverpoints
sample the same SV signal but apply different bin sets — e.g.
`BinExp` magnitude buckets *and* `BinOneHot` patterns on the same
input.

## sim-emit / sim-hit

The two grades of `> Verified (sim-...)` binding the pilots use:

- **`sim-emit`** — the generated SV parses + compiles, the cocotb
  testbench boots, and `cg.sample()` calls reach without exception.
  Verilator 5.038–5.042 provides this much because covergroup hit
  counting is no-op (issue verilator/#7099).
- **`sim-hit`** — a commercial simulator (VCS / Questa / Xcelium)
  records actual bin hit counts.

See [`examples/README.md`](../examples/README.md).

## make_coverage

The CLI shipped with cocotbext-fcov that walks a Python file for
`CoverageModel` instances and writes the corresponding `coverage.sv`
+ `coverage.md` (spec table). See
[`reference/scripts/make-coverage.md`](reference/scripts/make-coverage.md).

## COVERIGN

A Verilator warning class meaning *"this covergroup construct is
syntactically parsed but ignored at runtime"*. cocotbext-fcov
pilots run with `-Wno-COVERIGN` because the warning would
otherwise cap the Verilator build. See
[`explanations/architecture.md`](explanations/architecture.md).

## BASH_ENV

A bash environment variable that, when set, causes every
non-interactive bash subshell to source the named file. Some hosts
set `BASH_ENV=/etc/environment` globally, which resets `PATH` and
breaks the EDA tool lookup inside cocotb's recursive `$(MAKE)`.
`examples/_lib/Makefile.common` unsets `BASH_ENV` to neutralise
this.
