# simple_dff — first coverage pilot

Paired guide: [`docs/tutorials/first-coverage-model.md`](../../../docs/tutorials/first-coverage-model.md)

## Proves / Does NOT prove

**Proves**
- `make_coverage` emits a covergroup that both VCS and Questa elaborate.
- `cocotbext.fcov.CoverageCollector` binds the model to a cocotb-driven DUT
  (the vendored cocotb `dff.sv` D-FF).
- `BinBool` + the inline-`"=>"` transition syntax (with explicit `("name",
  pattern)` entries) flow through the emit pipeline.
- On VCS / Questa, the eight Q values sampled hit **both `BinBool` bins**
  (FALSE, TRUE) and **both `BinTransition` bins** (`up`, `down`) — 100% on
  `cg_dff`.

**Does NOT prove**
- Verilator functional hits — Verilator 5.038 ignores covergroup
  (`COVERIGN`), so the open-source run only proves emit + compile +
  `cg.sample()` call reach. Functional coverage measurement on
  Verilator requires upstream support for `cg_inst.sample()` /
  `get_inst_coverage()` (issue verilator/#7099, not in any released version).

## Run

```bash
source /root-openebs/workspace/stork-dv/stork_dv.env   # for VCS / Questa
make sim                   # SIM=verilator (default; sim-emit only)
SIM=vcs    make sim        # functional hit recording -> simv.vdb
SIM=questa make sim        # functional hit recording -> cov_*.ucdb

SIM=vcs    make report     # urg summary
SIM=questa make report     # vcover summary

make clean
```

Expected coverage output (Questa shown):

```
Coverpoint cp_q                100.00%
    bin FALSE   (5 hits)  Covered
    bin TRUE    (3 hits)  Covered
Coverpoint cp_q_trans          100.00%
    bin up      (2 hits)  Covered
    bin down    (2 hits)  Covered
TOTAL COVERGROUP COVERAGE: 100.00%
```

## What the test does

`tb_dff.py` runs the DUT through the pattern `[0, 1, 1, 0, 0, 1, 0, 1]` on
`d`, sampling `cg_dff` after each posedge clk. This pattern hits all four
target bins:

- `BinBool`: at least one FALSE (Q=0) and one TRUE (Q=1).
- `BinTransition.up` (0→1): edges at `0→1`, `0→1`, `0→1`.
- `BinTransition.down` (1→0): edges at `1→0`, `1→0`.

## Files

| File | Role |
|------|------|
| `dff.sv` | DUT, vendored verbatim from cocotb upstream (CC0; see [`NOTICE.md`](../../../NOTICE.md)) |
| `coverage_spec.py` | `DffCovModel` → `DffCoverGroup` with `cp_q` (BinBool) + `cp_q_trans` (inline transitions) |
| `tb_top.sv` | SV wrapper — instantiates `dff` and `cov_model` |
| `tb_dff.py` | cocotb test — clock + d-toggling + sample loop |
| `Makefile` | includes `_lib/Makefile.common` |
| `coverage.sv` (generated) | `module cov_model();` emitted by `make_coverage` |
| `coverage.md` (generated) | spec table |

## See also

- [`../README.md`](../README.md) — pilot conventions + marker meanings.
- [`../README.md`](../README.md) — pilot index + multi-simulator policy.
- [`../../../docs/explanations/architecture.md`](../../../docs/explanations/architecture.md) — coverage class hierarchy.
