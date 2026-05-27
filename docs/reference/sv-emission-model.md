---
title: SystemVerilog emission model
component_type: emission_model
layer: reference
src_path: cocotbext/fcov/coverage.py
src_symbols: [CoverageModel.systemverilog, CoverGroup.systemverilog]
related_guides: [bin-type-recipes, wire-into-testbench]
---
# SystemVerilog emission model

> The exact shape `make_coverage` writes out — what's a public
> contract, what's an implementation detail, and where the macros
> hook.

## TL;DR

| | |
|---|---|
| **What** | The structure of the `coverage.sv` file emitted by `make_coverage`. |
| **When to use** | When wiring `coverage.sv` into a testbench, or when chasing why a particular pattern compiles on commercial sims but not Verilator. |
| **Key links** | [`scripts/make-coverage.md`](scripts/make-coverage.md) · [`coverage/model.md`](coverage/model.md) · [`coverage/covergroup.md`](coverage/covergroup.md) · [`../explanations/architecture.md`](../explanations/architecture.md) |

## Module structure

For a `CoverageModel` named `cov_model` with two covergroups
`cg_a` and `cg_b`:

```sv
`ifdef FUNC_COV
`endif                          // legacy SV LRM macro -- reserved, currently empty

`ifdef COCOTBEXT_FCOV           // gate so non-coverage builds see no SV
module cov_model ();
  // ---- wires (one per CoverPoint signal; ref= cps share wires) ----
  wire [W-1:0] cg_a_cp_x;
  wire         cg_a_cp_y;
  wire         cg_a_sample;     // sample event wire for cg_a
  wire [W-1:0] cg_b_cp_z;
  wire         cg_b_sample;

  // ---- covergroups (one per CoverGroup) ----
  covergroup cg_a;
    cp_x: coverpoint cg_a_cp_x { bins ... }
    cp_y: coverpoint cg_a_cp_y { bins ... }
    cx_xy: cross cp_x, cp_y { ignore_bins ... }
  endgroup : cg_a
  cg_a cg_a_inst = new;
  always @(cg_a_sample) begin cg_a_inst.sample(); end

  covergroup cg_b;
    cp_z: coverpoint cg_b_cp_z { bins ... }
  endgroup : cg_b
  cg_b cg_b_inst = new;
  always @(cg_b_sample) begin cg_b_inst.sample(); end
endmodule
`endif
```

## Naming derivation

Every public identifier is composed mechanically — there is no
hand-naming in the emit pipeline.

| Identifier in SV | Python source |
|------------------|---------------|
| `<model_name>` (module name) | `CoverageModel(name="...")` arg or the class-attribute name in the parent collector |
| `<cg_name>` (covergroup type + instance prefix) | `CoverGroup` class-attribute name on the `CoverageModel` |
| `<cg_name>_inst` (covergroup instance) | hard-coded suffix `_inst` |
| `<cg_name>_<cp_name>` (wire) | `cp_*` class-attribute name on `CoverGroup`, joined with the cg's name |
| `<cg_name>_sample` (sample event wire) | hard-coded suffix `_sample` |
| `<bin_name>` inside `bins ...` | name given to `BinItem` (via `BinDict` / `BinEnum` / explicit name) or auto-derived from min/max |

## Public contract vs. implementation detail

**Public contract** (will not change without a deprecation cycle):

- The module name comes from `CoverageModel(name=...)`.
- Wires named `<cg>_<cp>` and `<cg>_sample` exist for every
  coverpoint and covergroup.
- The whole file is wrapped in `` `ifdef COCOTBEXT_FCOV ... `endif ``.

**Implementation detail** (may change in patch releases):

- Whitespace + newlines inside the `covergroup` body.
- The order in which coverpoints / crosses appear within a
  covergroup (currently follows Python class-attribute order).
- The `<cg>_inst` instance-name suffix (could become
  `<cg>_instance` etc.).
- The `` `ifdef FUNC_COV `endif`` shell at the top — currently empty,
  reserved for legacy SV LRM coverage gating.

## Macros

| Macro | Defined where | Effect |
|-------|---------------|--------|
| **`COCOTBEXT_FCOV`** | Pilot Makefiles via `+define+COCOTBEXT_FCOV` | Unwraps the `cov_model` module body. Synthesis flows that don't define it see an empty file — safe to include. |
| **`VERILATOR`** | Auto-defined by Verilator | The `_lib/Makefile.common` post-emit step wraps the `always @(<sample>) <cg_inst>.sample();` driver in `` `ifndef VERILATOR ... `endif `` because Verilator 5.038–5.042 doesn't implement `.sample()`. Commercial sims keep the driver. |
| **`FUNC_COV`** | (currently unused) | Reserved. The empty `` `ifdef FUNC_COV `endif `` shell at the top of `coverage.sv` is a hook for legacy gating; do not rely on it for new code. |

## Wiring into a DUT

The wires inside `cov_model` are read-only from outside SV — they
are driven from Python via cocotb's VPI handles. Typical wrapper:

```sv
module tb_top();
  // your DUT
  my_dut dut(...);

  // cov_model instance -- name must match `dut.cov_model` lookup
  cov_model cov_model();
endmodule
```

The cocotb side does the rest:

```python
collector = MyCollector(dut, cov_model=MyCovModel(name="cov_model"))
# Coverage enabled for cov_model -- collector binds every cg_*_sample wire.

cg.cp_value <= int(dut.some_signal.value)
cg.sample()
```

See [`coverage/model.md`](coverage/model.md) and the pilot READMEs
([`simple_dff`](../../examples/simple_dff/),
[`adder`](../../examples/adder/),
[`opcode_cross`](../../examples/opcode_cross/)) for end-to-end
worked examples.

## Verilator-specific patch

`examples/_lib/Makefile.common` ships a regex post-emit step that
turns

```sv
always @(<cg>_sample) begin <cg>_inst.sample(); end
```

into

```sv
`ifndef VERILATOR
always @(<cg>_sample) begin <cg>_inst.sample(); end
`endif
```

for `SIM=verilator` runs only. VCS / Questa run the unmodified
emit. Upstream cocotbext-fcov could absorb this guard at emit time
(see `CoverGroup.sv_sample_event`); the pilot-level patch is the
minimal-impact workaround until that lands.

## See also

- [`scripts/make-coverage.md`](scripts/make-coverage.md) — CLI that produces this file.
- [`coverage/model.md`](coverage/model.md) — Python source of the module body.
- [`../explanations/architecture.md`](../explanations/architecture.md) — full Python → SV → simulator data flow.
- [`../../examples/simple_dff/`](../../examples/simple_dff/) — smallest pilot; the simplest emit + run worth keeping.
