# adder — multi-axis sampling pilot

Paired guide: [`docs/how-to/sampling-in-cocotb.md`](../../docs/how-to/sampling-in-cocotb.md)

## Proves / Does NOT prove

**Proves**
- A single `CoverPoint` source signal carries **two coverage axes**
  (`cp_a` BinUniform + `cp_a_bitwise` BinBitwise via `ref=cp_a`). The
  `make_coverage` emit produces both a value coverpoint and N bit-slice
  coverpoints on the same wire.
- A diagonal sweep of 16 (A == B) values + four corner cases reaches:
  - **BinUniform(16) on A** — 16/16 bins
  - **BinUniform(16) on B** — 16/16 bins
  - **BinBitwise(4) on A** — every bit position toggled 0 and 1
  - **BinBool on carry** — both polarities seen
  - **Cross cp_a × cp_carry** — partial (the corners we explicitly add)

**Does NOT prove**
- 100% on `cx_a_carry`. Full cross has 16 × 2 = 32 bins; with 20
  vectors the cross sits around 94%. The paired guide explains how to
  hit the remaining corners.
- Verilator functional hits — same `COVERIGN` limitation.

## Run

```bash
source /root-openebs/workspace/stork-dv/stork_dv.env   # for VCS / Questa
make sim                   # SIM=verilator (default; sim-emit only)
SIM=vcs    make sim
SIM=questa make sim

SIM=vcs    make report
SIM=questa make report
```

VCS dashboard summary:

```
SCORE  LINE   COND   TOGGLE FSM    BRANCH GROUP  
 98.05 100.00 --     100.00 --     --      94.14 
```

## What the test does

`tb_adder.py`:

1. Diagonal sweep `A == B` from 0..15 — covers BinUniform on both
   inputs, all four bits of A, and produces a high carry for A >= 8.
2. Four corner pairs: `(15, 1)`, `(0, 15)`, `(8, 8)`, `(15, 0)` — adds
   coverage rows that the diagonal alone misses (especially the
   asymmetric (A, B) cross-product corners).

After each (A, B) deposit, a 2-ns delay lets the DUT settle before
`cg.sample()` triggers.

## Files

| File | Role |
|------|------|
| `adder.sv` | DUT, vendored cocotb upstream (CC0; see [`NOTICE.md`](../../NOTICE.md)) |
| `coverage_spec.py` | `AdderCovModel` → cp_a/b (BinUniform) + cp_a_bitwise (BinBitwise, ref=cp_a) + cp_carry (BinBool) + cx_a_carry (Cross) |
| `coverage.sv` (committed) | `make_coverage` snapshot |
| `tb_top.sv` | SV wrapper — `adder` + `cov_model` |
| `tb_adder.py` | cocotb test — diagonal sweep + corner pairs |
| `Makefile` | includes `_lib/Makefile.common` |

## Learning point — same wire, multiple coverpoints

`cp_a_bitwise = CoverPoint(BinBitwise(4), ref=cp_a)` reuses the
`cg_adder_cp_a` wire instead of emitting a second one. The generated
SystemVerilog ends up with five `coverpoint` blocks (the value
coverpoint plus four bit-slice coverpoints) all sampling the same
4-bit input — exactly the pattern the sampling-in-cocotb how-to
will walk through.

## See also

- [`../README.md`](../README.md) — pilot conventions + marker meanings.
- [`../simple_counter/`](../simple_counter/) — earlier pilot, single
  source signal.
- [`../../docs/explanations/architecture.md`](../../docs/explanations/architecture.md) — coverage class hierarchy.
