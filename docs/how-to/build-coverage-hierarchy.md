---
title: Build a coverage hierarchy
prerequisites: [first-coverage-model]
covers_components: [bins.item, bins.group, coverage.coverpoint, coverage.cross, coverage.covergroup, coverage.model]
---
# Build a coverage hierarchy

> Walk one Python coverage spec from the atomic `BinItem` layer up to
> a `CoverageModel`, mapping each step to a pattern that scales.

> 🇰🇷 [한국어 버전](../ko/how-to/build-coverage-hierarchy.md) · English below.

## TL;DR

| | |
|---|---|
| **Goal** | Decide where each piece of a coverage spec belongs in the chain — atom, container, coverpoint, cross, covergroup, model — and how the choices compound. |
| **When to use** | Designing a fresh coverage model, refactoring a flat one, or reviewing someone else's spec for "is this the right layer?" |
| **Key APIs** | `BinItem`, `BinGroup`, [17 `Bin*` types](../reference/bins/type.md), `CoverPoint`, `Cross`, `CoverGroup`, `CoverageModel` |

This page answers:
- Which layer owns naming, ordering, dispatch, and sample timing?
- When does a single Python list become a `Bin*` predefined type?
- How do `ref=` and `Cross` reuse existing coverpoints?
- When is one `CoverageModel` enough vs. several?

## Overview

**Role.** Step-by-step design guide. Each step lands a concrete
pattern from one of the existing pilots so the choice has a runnable
reference. The full architecture diagram lives at
[`explanations/architecture.md`](../explanations/architecture.md).

**Does NOT cover:**
- Bin-type selection by intent → [`bin-type-recipes.md`](bin-type-recipes.md).
- The runtime sample() path → [`sampling-in-cocotb.md`](sampling-in-cocotb.md).
- DUT ↔ cov_model wrapper plumbing → [`wire-into-testbench.md`](wire-into-testbench.md).

## Step 1 — Atom: `BinItem` (rarely direct)

Most users *never* construct `BinItem` directly. The atomic layer
exists so that:

- a list passed to `CoverPoint(...)` can become `BinItem`s automatically,
- transition chains can be hand-built with `>>` / `<<` when the
  inline `"=>"` shorthand is awkward.

Direct `BinItem` is rare enough that none of the docs-boost pilots
use it.

> Verified: [`tests/pytest/test_bin_item.py`](../../tests/pytest/test_bin_item.py)

## Step 2 — Container: pick a `Bin*` type

The default move is to pick one of the 17 [`Bin*` predefined
types](../reference/bins/type.md) — they specialise the
`BinGroup` constructor for one common pattern (range, enum,
exponential, min/max, one-hot, transition, ...). The
[`bin-type-recipes.md`](bin-type-recipes.md) how-to is the decision
table.

When none of them fit, fall back to `BinGroup({...})` or
`BinCustom({...})` and name the bins explicitly.

> Verified: [`tests/pytest/test_bin_emit_snapshots.py`](../../tests/pytest/test_bin_emit_snapshots.py)

## Step 3 — One signal, one observation: `CoverPoint`

Wrap each `Bin*` in a `CoverPoint`. The CoverPoint owns:

- the **signal** the bins are checked against,
- optional `ignore_bins` / `illegal_bins`,
- the Python-side `cp.value = ...` driver,
- the SV-side `<group>_<cp>` wire.

**Multiple axes on one signal**: pass `ref=` to share the wire.

```python
cp_a_exp     = CoverPoint(BinExp(16, base=2))
cp_a_bitwise = CoverPoint(BinBitwise(4), ref=cp_a_exp)
```

> Verified (sim-emit): [`tests/cocotb/adder/coverage_spec.py`](../../tests/cocotb/adder/coverage_spec.py)

## Step 4 — Combinations: `Cross`

When per-coverpoint coverage isn't enough — you need to verify a
*combination* of values — add a `Cross`:

```python
cx_op_addr = Cross([cp_op, cp_addr], name="cx_op_addr")
```

Cross also carries `ignore_bins` / `illegal_bins`. **Use integer
values, not bin names**, in the term `value_spec` (SV LRM 19.5):

```python
Cross([cp_op, cp_zero],
      ignore_bins=[{"name": "ig_and_zero",
                    "terms": [(cp_op, int(Op.AND)), (cp_zero, 1)]}])
```

> Verified (sim-emit): [`tests/cocotb/opcode_cross/coverage_spec.py`](../../tests/cocotb/opcode_cross/coverage_spec.py)

## Step 5 — Group: `CoverGroup`

Subclass `CoverGroup` and attach `CoverPoint` + `Cross` as **class
attributes**. The subclass becomes a reusable template — instantiate
it once per logical instance.

```python
class RegfileCoverGroup(CoverGroup):
    cp_addr  = CoverPoint(BinDict({"R0": 0, "R1": 1, "R2": 2, "R3": 3}))
    cp_op    = CoverPoint(BinEnum(Op))
    cx_op_addr = Cross([cp_op, cp_addr])
```

Per-instance hit counts are independent — `cg_chan0` and `cg_chan1`
of the same `CoverGroup` subclass track separate hit buckets.

> Verified (sim-hit): [`tests/cocotb/register_sampling/coverage_spec.py`](../../tests/cocotb/register_sampling/coverage_spec.py) — domain-spread regfile pilot.
>
> Verified (sim-hit): [`tests/cocotb/simple_counter/coverage_spec.py`](../../tests/cocotb/simple_counter/coverage_spec.py) — minimum 3-axis (`BinRange` + `BinBool` + `Cross`) `CoverGroup` template.

## Step 6 — Module: `CoverageModel`

The model bundles 1+ covergroup *instances* into one SV module
that `make_coverage` writes out. A single project typically has one
model per testbench block.

```python
class RegfileCovModel(CoverageModel):
    cg_regfile = RegfileCoverGroup()

cov_model = RegfileCovModel(name="cov_model")
```

The module-level `cov_model` instance is what `make_coverage`
discovers when it walks the file.

> Verified (sim-hit): [`tests/cocotb/register_sampling/coverage_spec.py`](../../tests/cocotb/register_sampling/coverage_spec.py)

## When to split into several models

| Signal | Split |
|--------|-------|
| Different testbench blocks (e.g. AXI vs APB) | one model per block |
| Different sample cadences (e.g. cycle-level vs transaction-level) | typically split — each model gets one sample wire |
| Same block, same cadence, > 100 covergroups | optional split for build time |

Each model becomes a separate `module <name> ()` in the emitted
`coverage.sv`. The cocotb [`CoverageCollector`](../reference/coverage/model.md)
accepts a dict of `{name: CoverageModel}` for multi-model setups.

## See also

- [`../tutorials/first-coverage-model.md`](../tutorials/first-coverage-model.md) — happy-path tutorial that follows this hierarchy end to end.
- [`bin-type-recipes.md`](bin-type-recipes.md) — which `Bin*` to pick at Step 2.
- [`sampling-in-cocotb.md`](sampling-in-cocotb.md) — runtime sample-and-hit path.
- [`wire-into-testbench.md`](wire-into-testbench.md) — wrapping `cov_model` into a DUT testbench.
- [`../explanations/architecture.md`](../explanations/architecture.md) — full diagram + sample-flow walkthrough.
- [`../glossary.md`](../glossary.md) — term definitions.
