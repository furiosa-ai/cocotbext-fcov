---
title: Wire cov_model into a cocotb testbench
prerequisites: [first-coverage-model, sampling-in-cocotb]
covers_components: [coverage.model]
---
# Wire `cov_model` into a cocotb testbench

> Connect the SystemVerilog module that `make_coverage` emits to a
> running cocotb test — what the SV wrapper looks like, what the
> Python side does, what to do when the wires don't match.

> 🇰🇷 [한국어 버전](../ko/how-to/wire-into-testbench.md) · English below.

## TL;DR

| | |
|---|---|
| **Goal** | Have a cocotb test boot, look up `cov_model` on the DUT handle, and start sampling. |
| **When to use** | After defining `coverage_spec.py` and running `make_coverage`. Before the first `cg.sample()` call. |
| **Key APIs** | `CoverageModel(name=...)`, `CoverageCollector(dut, cov_model=...)`, the SV `tb_top.sv` wrapper convention |

This page answers:
- What does the SV testbench top need to instantiate?
- How does `CoverageCollector` find the SV instance?
- What macros do I need defined at compile time?
- What goes wrong when wires don't match?

## Overview

**Role.** The wiring story between Python coverage spec and SV
runtime. Picks up after the spec is written and the
[architecture diagram](../explanations/architecture.md) is
understood.

**Does NOT cover:**
- Writing the spec → [`build-coverage-hierarchy.md`](build-coverage-hierarchy.md).
- Sampling cadence → [`sampling-in-cocotb.md`](sampling-in-cocotb.md).
- The exact emit layout → [`../reference/sv-emission-model.md`](../reference/sv-emission-model.md).

## Step 1 — Generate `coverage.sv`

```bash
make_coverage -f coverage_spec.py -sv coverage.sv -md coverage.md --overwrite
```

The output is gated behind `` `ifdef COCOTBEXT_FCOV `` — pass
`+define+COCOTBEXT_FCOV` at compile time. The pilots'
[`Makefile.common`](../../tests/cocotb/_lib/Makefile.common) does
this automatically.

## Step 2 — SV testbench wrapper

Instantiate **both** the DUT and the cov_model module. The
instance name of `cov_model` must match the model's Python `name=`:

```sv
`timescale 1ns/1ps

module tb_top();
  // your DUT signals + instance
  logic clk, rst;
  logic [31:0] data;
  my_dut dut(.clk(clk), .rst(rst), .data(data));

  // cov_model instance -- name == CoverageModel(name=...)
  cov_model cov_model();
endmodule
```

> Verified (sim-hit): [`tests/cocotb/register_sampling/tb_top.sv`](../../tests/cocotb/register_sampling/tb_top.sv)

## Step 3 — cocotb collector

```python
import cocotb
from cocotbext.fcov import CoverageCollector
from coverage_spec import RegfileCovModel


class RegfileCollector(CoverageCollector):
    """Thin wrapper -- inherits the connect() logic."""


@cocotb.test()
async def test_regfile(dut):
    cov_model = RegfileCovModel(name="cov_model")
    collector = RegfileCollector(dut, cov_model=cov_model)

    cg = collector.cov.cg_regfile

    # ... stimulus + sampling ...
```

The collector logs `Coverage enabled for cov_model` when it
successfully resolves the SV-side instance. If you see
`Coverage instance cov_model does not exist in dut!` — the SV
instance name doesn't match the model name; check Step 2.

> Verified (sim-hit): [`tests/cocotb/register_sampling/tb_regfile.py`](../../tests/cocotb/register_sampling/tb_regfile.py)

## Step 4 — Multi-model testbenches

When a block uses several coverage domains (e.g. protocol + perf +
SVA-style), instantiate each in the wrapper and pass a dict to the
collector:

```sv
module tb_top();
  my_dut dut(...);
  cov_protocol cov_protocol();
  cov_perf     cov_perf();
endmodule
```

```python
collector = TopCollector(
    dut,
    cov_model={
        "cov_protocol": ProtocolCovModel(),
        "cov_perf":     PerfCovModel(),
    },
)
```

Each model becomes accessible on the collector by its dict key:
`collector.cov_protocol.cg_xxx`, `collector.cov_perf.cg_yyy`.

## Step 5 — Simulator selection

| Simulator | Build | Run | Functional coverage |
|-----------|-------|-----|---------------------|
| **Verilator 5.038–5.042** | ✓ with `-Wno-COVERIGN` and the `ifndef VERILATOR` patch on the `always @(sample) cg_inst.sample();` line | ✓ | ✗ no-op (covergroup not implemented) |
| **VCS** | ✓ with `-cm assert+...` | ✓ | ✓ via `simv.vdb` → `urg` |
| **Questa** | ✓ with `+cover=bcefxs` | ✓ with `-coverage` | ✓ via `cov_*.ucdb` → `vcover` |

`tests/cocotb/_lib/Makefile.common` switches on `SIM=verilator/vcs/questa`
and applies the right flags + patches automatically.

## Common failure modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Coverage instance cov_model does not exist in dut!` | SV instance name mismatched | Make the SV instance name match `CoverageModel(name=...)` |
| `No coverpoint signal cg_xxx_cp_yyy` | A `CoverPoint` was added to the spec but `coverage.sv` not regenerated | Re-run `make_coverage` (or `make coverage.sv`) |
| `Class method 'sample' not found in class 'cg_xxx'` | Building with Verilator without the `ifndef VERILATOR` patch | Use `_lib/Makefile.common` or apply the same regex sub yourself |
| `Identifier 'AND' has not been declared` | Pass a bin-name string in `Cross.ignore_bins`/`illegal_bins` `value_spec` | Use the integer value: `int(Op.AND)` |
| `binsof(None) intersect ...` | cocotbext-fcov older than commit `769533f` | Update; the Cross cp-remap fix landed in that commit |

## See also

- [`build-coverage-hierarchy.md`](build-coverage-hierarchy.md) — design pass before wiring.
- [`sampling-in-cocotb.md`](sampling-in-cocotb.md) — the sample loop after wiring.
- [`../reference/sv-emission-model.md`](../reference/sv-emission-model.md) — exact module shape `make_coverage` emits.
- [`../reference/coverage/model.md`](../reference/coverage/model.md) — `CoverageModel` + `CoverageCollector` API.
- [`../../tests/cocotb/README.md`](../../tests/cocotb/README.md) — pilot conventions; every pilot is a worked example of this how-to.
- [`../glossary.md`](../glossary.md) — term definitions.
