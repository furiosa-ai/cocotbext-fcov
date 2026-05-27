# register_sampling — Bin\* variety pilot

Paired guide: [`docs/how-to/wire-into-testbench.md`](../../../docs/how-to/wire-into-testbench.md)

## Proves / Does NOT prove

**Proves**
- A single `CoverGroup` can mix **six different Bin\* patterns** without
  fighting the emit: `BinDict`, `BinEnum`, an explicit-name list,
  `BinRange + BinDefault`, inline transitions, and `Cross`.
- `make_coverage` emits a syntactically-clean SV `covergroup` for each
  pattern — see [`coverage.sv`](coverage.sv).
- On VCS / Questa, 14 register transactions exercise:
  - all four addresses (`R0..R3`) — BinDict 4/4
  - all three ops (NONE / READ / WRITE) — BinEnum 3/3
  - all three sizes (1/2/4) — explicit-name list 3/3
  - low-data + high-data writes — `BinRange(64)` interior + `BinDefault`
    catch-all both seen
  - `read_after_write` (op 1→2) and `write_after_read` (op 2→1)
    transitions
  - a portion of the `cp_op × cp_addr` cross matrix

**Does NOT prove**
- 100% on `cx_op_addr` — full cross has 3 × 4 = 12 bins; the
  stimulus tape hits ~half. The paired wire-into-testbench guide
  shows how to expand the tape to close the cross.
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

Sample VCS dashboard:

```
SCORE  LINE   COND   TOGGLE FSM    BRANCH GROUP  
 90.11 100.00 100.00  68.94 --     100.00  81.60 
```

## Authoring gotchas (captured here so the guide can cite them)

### 1. `byte` / `word` are SystemVerilog reserved keywords

`BinSingle`-style explicit names like `("byte", 1)` are rejected by the
SV elaborator. The cp_size coverpoint uses `size_1` / `size_2` / `size_4`
instead. **Anything emitted as a `bins <name> = ...` clause must avoid
the SV reserved-word list.**

### 2. Duplicate bin names

`BinTransition((1, 2), (2, 1))` would auto-name both transitions
`bin_1_2` (same min/max), tripping the BinGroup duplicate-name guard.
Use the explicit-name list form instead:

```python
[("read_after_write", [2, "=>", 1]),
 ("write_after_read", [1, "=>", 2])]
```

The same pattern was needed by the [simple_dff](../simple_dff/) pilot.

## What the test does

`tb_regfile.py` reset-pulses for 15 ns, then runs a 14-step "stimulus
tape" of `(op, addr, size, wdata)` tuples. Each tuple drives the DUT
inputs at one posedge clk; after the edge, the Python side updates
`cg.cp_*` and calls `cg.sample()`.

The tape covers the matrix deliberately:

| Step | Op | Addr | Size | Data | Hits |
|------|-----|------|------|------|------|
| 1 | WRITE | R0 | 1 | 0x05 | cp_addr.R0, op.WRITE, size_1, data low |
| 2 | READ | R0 | 1 | — | op.READ, op_trans.read_after_write |
| 3–8 | (WRITE, READ) on R1, R2, R3 | | | | full BinDict + BinEnum + size 1/2/4 |
| 9–10 | WRITE high data | | | 0x100, 0xFFFFFF00 | BinDefault "others" |
| 11–12 | READ then WRITE on R2 | | | | op_trans.write_after_read |
| 13–14 | NONE pulses | | | | op.NONE |

## Files

| File | Role |
|------|------|
| `regfile.sv` | DUT (self-authored 4-entry register file) |
| `coverage_spec.py` | 6 Bin\* axes + 1 Cross |
| `coverage.sv` (committed) | `make_coverage` snapshot |
| `tb_top.sv` | SV wrapper — `regfile` + `cov_model` |
| `tb_regfile.py` | cocotb test — 14-step stimulus tape |
| `Makefile` | includes `_lib/Makefile.common` |

## See also

- [`../README.md`](../README.md) — pilot conventions + marker meanings.
- [`../adder/`](../adder/) — single-cp ref= pattern (one wire, multiple axes).
- [`../../../docs/explanations/architecture.md`](../../../docs/explanations/architecture.md) — coverage class hierarchy.
