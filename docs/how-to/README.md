---
title: How-to guides
---
# How-to guides

Task-oriented recipes. Each one assumes you already have a coverage model — start with [tutorials/first-coverage-model.md](../tutorials/first-coverage-model.md) if you don't.

| Page | Task |
|------|------|
| [build-coverage-hierarchy.md](build-coverage-hierarchy.md) | Design a coverage spec — walk one Python spec from `BinItem` up to `CoverageModel`. |
| [bin-type-recipes.md](bin-type-recipes.md) | Pick the right predefined `Bin*` for a coverage spec (decision table). |
| [cross-with-ignore-illegal.md](cross-with-ignore-illegal.md) | Filter cross-product coverage with `ignore_bins` / `illegal_bins`. |
| [sampling-in-cocotb.md](sampling-in-cocotb.md) | Sample coverage from a cocotb test (driving `cp.value`, calling `sample()`). |
| [wire-into-testbench.md](wire-into-testbench.md) | Wire `cov_model` into a cocotb testbench — SV wrapper + `CoverageCollector` lookup + simulator selection + failure modes. |
