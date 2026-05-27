# examples/ — docs-backed executable pilots

Each pilot here is a small cocotb testbench paired with a `coverage_spec.py`,
exercised end-to-end against one or more simulators. The pilots double as
**Verified-bindings** for code blocks in `docs/how-to/*` and
`docs/tutorials/*` — every example a guide shows is also runnable here.

## Pilots

| Pilot | Source | Paired guide | `Bin*` patterns |
|-------|--------|--------------|-----------------|
| `simple_dff/` | cocotb upstream (CC0) | `tutorials/first-coverage-model` | `BinBool` + `BinTransition` |
| `simple_counter/` | self-authored | `how-to/build-coverage-hierarchy` | `BinRange` + `BinBool` + `Cross` |
| `adder/` | cocotb upstream (CC0) | `how-to/sampling-in-cocotb` | `BinUniform` + `BinBitwise` + `BinBool` + `Cross` |
| `register_sampling/` | self-authored | `how-to/wire-into-testbench` | `BinDict` + `BinEnum` + `BinRange` + `BinDefault` + transitions + `Cross` |
| `opcode_cross/` | self-authored | `how-to/cross-with-ignore-illegal` | `BinEnum` + `BinExp` + `BinBool` + `BinOneHot` + `Cross` + `ignore_bins` + `illegal_bins` |
| `matrix_multiplier/` | cocotb upstream (CC0, 2×2 params) | `how-to/bin-type-recipes` | `BinUniform` + `BinMinMaxExp` (combined) + `BinMinMax` + `BinBool` + `Cross` |

## Run one pilot

```bash
source /root-openebs/workspace/stork-dv/stork_dv.env   # for VCS / Questa
cd examples/<pilot>
make sim                   # SIM=verilator (open-source, default)
SIM=vcs    make sim        # functional cov via simv.vdb
SIM=questa make sim        # functional cov via cov_*.ucdb
make report                # urg / vcover summary (vcs / questa only)
make clean
```

## Run all pilots

```bash
for d in examples/*/; do (cd "$d" && make sim) || exit; done
SIM=vcs    bash -c 'for d in examples/*/; do (cd "$d" && make sim) || exit; done'
SIM=questa bash -c 'for d in examples/*/; do (cd "$d" && make sim) || exit; done'
```

Pilots live outside the pytest gate — `tests/pytest/` covers the
pure-Python regression net, and pilots are runnable demonstrations
of the docs/how-to recipes.

## Marker meanings (Verified bindings)

| `> Verified:` flavour | Sim | Guarantee |
|-----------------------|-----|-----------|
| `> Verified:` | (pytest) | Python-side API contract |
| `> Verified (sim-emit):` | Verilator | SV emit + compile + `sample()` call reaches |
| `> Verified (sim-hit):` | VCS / Questa | Actual functional bin hit count recorded |

Verilator 5.038–5.042 (devel 5.049) does **not** implement covergroup hit
counting (issue verilator/verilator#7099 open, PR pending). Pilots therefore
ship `sim-emit` guarantees on the open-source flow and `sim-hit` on commercial
flows.

## Adding a new pilot

1. Make a new directory `examples/<pilot_name>/`.
2. Add a `coverage_spec.py` (one or more `CoverageModel` subclasses with a
   module-level instance for `make_coverage` to discover).
3. Add the DUT (`<dut>.sv`) and the cocotb test (`tb_<pilot>.py`).
4. Add `tb_top.sv` that instantiates `cov_model` (and the DUT, if used).
5. Add a minimal `Makefile` that includes `_lib/Makefile.common`:

   ```makefile
   PILOT_DIR := $(dir $(realpath $(firstword $(MAKEFILE_LIST))))
   COCOTB_TOPLEVEL = tb_top
   COCOTB_TEST_MODULES = tb_<pilot>
   PILOT_DUT_SOURCES = $(PILOT_DIR)/<dut>.sv
   include $(PILOT_DIR)/../_lib/Makefile.common
   ```

6. Add a `README.md` with a **"Proves / Does NOT prove"** box at the top.

7. If the DUT was vendored from cocotb (or another BSD-3 source), add an entry
   to the repo root `NOTICE.md` and an SPDX header on the file.

8. Pair the pilot with a guide page — every code block in the guide should be
   `> Verified (sim-*)`-bound to this pilot.

## Host quirk — `BASH_ENV`

If your host sets `BASH_ENV=/etc/environment` globally, the cocotb recursive
`make` would re-source that file in every bash subshell and reset `PATH`,
dropping EDA tool paths set by `stork_dv.env`. `_lib/Makefile.common` already
unsets `BASH_ENV` to neutralise this — no extra steps needed on your side.

## See also

- `simple_dff/` — the smallest pilot; toolchain spike if you need one.
- `_lib/Makefile.common` — the shared build glue.
- `docs/explanations/architecture.md` — the BinItem→…→CoverageCollector hierarchy.
