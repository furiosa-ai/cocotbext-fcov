# simple_counter — multi-coverpoint + Cross pilot

Paired guide: [`docs/how-to/build-coverage-hierarchy.md`](../../../docs/how-to/build-coverage-hierarchy.md)

## Proves / Does NOT prove

**Proves**
- A `CoverGroup` with three members (`BinRange` + `BinBool` + `Cross`)
  elaborates and emits cleanly through `make_coverage`.
- Multiple Python-driven coverpoints sample together on a single
  `cg.sample()` call without races.
- On VCS / Questa, 20 free-running clock cycles of the 4-bit counter:
  - hit **every value 0..15** (cp_value 16/16 bins)
  - hit **the overflow pulse** (cp_overflow 2/2 bins)
  - hit a non-trivial subset of the **cross** matrix (cp_value × cp_overflow)

**Does NOT prove**
- Full cross coverage. The cross product is 16×2 = 32 bins; an
  overflow pulse only fires once per wrap, so the cross only reaches
  ~half. The pilot's job is to demonstrate the wiring; the paired guide
  explains how to *close* a Cross.
- Verilator functional hits — same `COVERIGN` limitation as the rest
  of the cocotb pilots.

## Run

```bash
source /root-openebs/workspace/stork-dv/stork_dv.env   # for VCS / Questa
make sim                   # SIM=verilator (default)
SIM=vcs    make sim
SIM=questa make sim

SIM=vcs    make report
SIM=questa make report
```

Sample VCS output (`urg`):

```
Group : tb_top.cov_model::cg_counter
SCORE  WEIGHT GOAL   AT LEAST AUTO BIN MAX PRINT MISSING 
 84.38 1      100    1        64           64            
```

The score is intentionally < 100% — see *Does NOT prove* above.

## What the test does

`tb_counter.py`:

1. Starts a 10 ns clock on `dut.clk`.
2. Pulses `rst=1` for 15 ns, then releases and asserts `enable=1`.
3. Runs 20 posedges, after each one:
   - reads `dut.value` + `dut.overflow`
   - drives `cg.cp_value <= ...`, `cg.cp_overflow <= ...`
   - calls `cg.sample()`

20 cycles is one full wrap (0→15→0) plus 4 extra ticks — covers every
counter value at least once + the overflow pulse at value=15→0.

## Files

| File | Role |
|------|------|
| `counter.sv` | DUT (self-authored 4-bit up-counter) |
| `coverage_spec.py` | `CounterCovModel` → `CounterCoverGroup` (BinRange + BinBool + Cross) |
| `coverage.sv` (committed) | `make_coverage` snapshot |
| `tb_top.sv` | SV wrapper — `counter` + `cov_model` |
| `tb_counter.py` | cocotb test — clock + reset + 20-cycle sample loop |
| `Makefile` | includes `_lib/Makefile.common` |

## See also

- [`../README.md`](../README.md) — pilot conventions + marker meanings.
- [`../simple_dff/`](../simple_dff/) — single-coverpoint precursor pilot.
- [`../../../docs/explanations/architecture.md`](../../../docs/explanations/architecture.md) — coverage class hierarchy.
