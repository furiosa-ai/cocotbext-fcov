# opcode_cross — Cross + ignore_bins + illegal_bins pilot

Paired guide: [`docs/how-to/cross-with-ignore-illegal.md`](../../../docs/how-to/cross-with-ignore-illegal.md)

## Proves / Does NOT prove

**Proves**
- `Cross` with both `ignore_bins` and `illegal_bins` clauses emits
  syntactically-clean SystemVerilog after the upstream cp-remap fix
  (commit `769533f`).
- `BinExp` and `BinOneHot` on the same source signal (via `ref=cp_a`)
  coexist — one cp covers magnitude buckets, the other covers the
  one-hot encodings 1, 2, 4, 8.
- On VCS / Questa, the stimulus tape hits every BinExp bucket, every
  BinOneHot pattern, every BinEnum op, both result_zero polarities,
  and the cross bin matrix minus the explicitly-ignored/illegal entries.

**Does NOT prove**
- 100% on `cx_op_zero` — `<SUB, TRUE>` is the only cross bin the
  current stimulus tape leaves unhit (would need a `SUB a, b` with
  `a == b` to fire, but the tape only has SUB pairs that produce
  non-zero). The paired guide expands the tape to close this.
- Verilator functional hits — same `COVERIGN` limitation.

## Run

```bash
source /root-openebs/workspace/stork-dv/stork_dv.env   # for VCS / Questa
make sim
SIM=vcs    make sim
SIM=questa make sim

SIM=vcs    make report
SIM=questa make report
```

Sample Questa output (excerpt):

```
Coverpoint cp_op           100%   ADD(9) SUB(2) AND(3) OR(3)
Coverpoint cp_a            100%   bin_0..bin_8_15 all covered
Coverpoint cp_a_onehot     100%   1,2,4,8 all covered (via ref=cp_a)
Coverpoint cp_result_zero  100%   FALSE(11) TRUE(6)
Cross cx_op_zero
    <ADD, FALSE>(7) <SUB, FALSE>(2) <AND, FALSE>(1) <OR, FALSE>(3)
    <ADD, TRUE>(2)  <SUB, TRUE>(0 -- ZERO)
    ignore_bin ig_and_zero   Occurred 2 times
    illegal_bin il_or_zero   (never fires; would error if it did)
```

## Authoring gotcha — `binsof intersect` takes values, not names

SV LRM defines `binsof(cp) intersect {<set>}` where `<set>` is a set
of **integer values**, not bin names. The natural-feeling Python form

```python
ignore_bins=[
    {"name":  "ig_and_zero",
     "terms": [(cp_op, "AND"), (cp_result_zero, "TRUE")]},
]
```

emits `binsof(cp_op) intersect {AND}` which both VCS and Questa
reject with `Identifier 'AND' has not been declared`. Use integer
values instead — and `IntEnum.AND` makes that readable:

```python
ignore_bins=[
    {"name":  "ig_and_zero",
     "terms": [(cp_op, int(Op.AND)), (cp_result_zero, 1)]},
]
```

The paired guide expands on the full value_spec catalog from the
`Cross.ignore_bins / illegal_bins` reference.

## Upstream fix surfaced by this pilot

`fix(coverage): remap Cross ignore_bins / illegal_bins cp refs after deepcopy`
(commit `769533f`). Before that commit, the SV emit ended up with
`binsof(None) intersect ...` because the cp references inside the
ignore_bins / illegal_bins clauses pointed at the un-named class-level
templates instead of the instance-level cps. This pilot was the first
to exercise the path, so the bug surfaced + was fixed in the same
docs-boost cycle.

## What the test does

`tb_alu.py` resets the ALU, then walks a 17-step stimulus tape that
deliberately hits the matrix corners. Two samples per posedge clk
(the ALU registers its output, so we wait one extra cycle before
sampling).

## Files

| File | Role |
|------|------|
| `alu.sv` | DUT (self-authored 4-bit ALU: ADD/SUB/AND/OR) |
| `coverage_spec.py` | 5 cps + 1 cross with ignore + illegal clauses |
| `coverage.sv` (committed) | `make_coverage` snapshot |
| `tb_top.sv` | SV wrapper — `alu` + `cov_model` |
| `tb_alu.py` | cocotb test — 17-step stimulus tape |
| `Makefile` | includes `_lib/Makefile.common` |

## See also

- [`../README.md`](../README.md) — pilot conventions + marker meanings.
- [`../register_sampling/`](../register_sampling/) — earlier multi-Bin\* pilot.
- [`../adder/`](../adder/) — `ref=` pattern on a single source wire.
- [`../../../docs/explanations/architecture.md`](../../../docs/explanations/architecture.md) — coverage class hierarchy.
