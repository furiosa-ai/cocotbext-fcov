# matrix_multiplier — magnitude / range Bin\* showcase

Paired guide: [`docs/how-to/bin-type-recipes.md`](../../../docs/how-to/bin-type-recipes.md)

## Proves / Does NOT prove

**Proves**
- Two complementary ways to combine `Bin*` patterns on one value:
  - **`BinGroup.__add__`** (this pilot's headline) — combine
    `BinUniform(4, num=4)` (fine-grained low region: 0,1,2,3 as
    four sub-bins) with `BinMinMaxExp(min=4, max=15, base=2)`
    (boundary + exp interior: 4, [5:7], [8:14], 15) into **one**
    coverpoint via Python's `+` operator. The emit is one
    `coverpoint` block with 8 named bins (`bin_0_3[4]`, `bin_4`,
    `bin_5_7`, `bin_8_14`, `bin_15`).
  - **`ref=`** — sample the same SV wire with two different
    coverpoints (used on `cp_c0` / `cp_c0_mmexp` to compare a
    `BinMinMax` boundary split with a `BinMinMaxExp` interior).
- The pilot uses cocotb upstream `matrix_multiplier.sv` (CC0)
  parameterised down to a 2×2 × 2×2 multiplication with 4-bit
  elements so the coverage matrix is tractable (C result fits in 9
  bits, max 450).
- On VCS / Questa, the 8-vector stimulus tape hits 5/8 bins on
  `cp_a0`, 6/8 on `cp_b0`, both boundary corners on `cp_c0`
  (0 and 450), and ~10% of the 8×8 cross.

**Does NOT prove**
- 100% on `cx_a0_b0` — full cross is 8×8 = 64 bins; 8 vectors hit
  ~7 of them. The paired guide expands the stimulus to close it.
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

## Coverage spec — combined `Bin*` via `+`

```python
def _hybrid_4bit():
    # 0,1,2,3 each as singletons (uniform low) + 4, [5:7], [8:14], 15
    # (boundary + exp high)  -- one CoverPoint, 8 bins.
    return BinUniform(4, num=4) + BinMinMaxExp(min=4, max=15, base=2)


class MatmulCoverGroup(CoverGroup):
    cp_a0       = CoverPoint(_hybrid_4bit(), name="cp_a0")
    cp_b0       = CoverPoint(_hybrid_4bit(), name="cp_b0")
    cp_c0       = CoverPoint(BinMinMax(min=0, max=450, num=5))
    cp_c0_mmexp = CoverPoint(BinMinMaxExp(min=0, max=450, base=2), ref=cp_c0)
    cp_valid_o  = CoverPoint(BinBool())
    cx_a0_b0    = Cross([cp_a0, cp_b0], name="cx_a0_b0")
```

Generated SV (excerpt):

```sv
cp_a0: coverpoint cg_matmul_cp_a0 {
  bins bin_0_3[4] = {[0:3]};     // 4 sub-bins (one per value 0,1,2,3)
  bins bin_4 = {4};               // boundary low
  bins bin_5_7 = {[5:7]};         // exp interior
  bins bin_8_14 = {[8:14]};       // exp interior
  bins bin_15 = {15};             // boundary high
}
```

`BinGroup` overloads `+` to merge bin dicts — duplicate names
raise `AssertionError`, so the two halves of the combine must
produce disjoint ranges (which `(0..3, num=4)` + `(min=4, max=15)`
naturally does).

## What the test does

`tb_mm.py` resets the DUT then drives 8 (A_matrix, B_matrix) pairs:

| Step | Notes |
|------|-------|
| 1 | All-zero — C[0]=0, hits `cp_c0.bin_0` (boundary low) |
| 2 | Diagonal 1s — `cp_a0.bin_0_3[1]`, `cp_b0.bin_0_3[1]` |
| 3 | Mid magnitudes — `cp_a0.bin_5_7` / `cp_b0.bin_4` |
| 4 | A[0]=B[0]=15, off-diagonal zero — C[0]=225, `cp_a0.bin_15` |
| 5 | A and B max diagonal — C[0]=450, hits `cp_c0.bin_450` (boundary high) |
| 6–8 | Variety to fill more cross corners |

`valid_i` is pulsed one cycle per multiplication; the DUT registers
`valid_o` and `c_o` one cycle later.

## Files

| File | Role |
|------|------|
| `matrix_multiplier.sv` | DUT, vendored cocotb upstream (CC0; see [`NOTICE.md`](../../../NOTICE.md)) |
| `coverage_spec.py` | 5 cps + 1 cross — hybrid `_hybrid_4bit()` on cp_a0/cp_b0, `BinMinMax`/`BinMinMaxExp` on cp_c0 via ref= |
| `coverage.sv` (committed) | `make_coverage` snapshot |
| `tb_top.sv` | SV wrapper, instantiates matrix_multiplier with reduced params (2×2 × 2×2, 4-bit elements) |
| `tb_mm.py` | cocotb test — 8-vector stimulus tape |
| `Makefile` | includes `_lib/Makefile.common` |

## Learning point — `BinGroup.__add__` vs `ref=`

Two ways to put **multiple bin shapes on the same source signal**.
Both are useful; the pilot demonstrates each so the recipes guide
can recommend by intent:

| Pattern | When to use |
|---------|-------------|
| `cp = CoverPoint(BinX() + BinY())` | One coverpoint, one logical "view" of the signal — but the view's bin set is naturally split into two disjoint regions (e.g. fine-grained low + coarse high). The simulator reports them as one coverpoint's bins. |
| `cp_a = CoverPoint(BinX()); cp_b = CoverPoint(BinY(), ref=cp_a)` | Two coverpoints with separate hit counts on the same wire — useful when each "view" should be closed independently (e.g. an exponential bucket view and a uniform bucket view both treated as first-class). |

`cp_a0` uses the first pattern. `cp_c0` / `cp_c0_mmexp` uses the
second.

## See also

- [`../README.md`](../README.md) — pilot conventions + marker meanings.
- [`../adder/`](../adder/) — earlier `ref=` example (BinUniform + BinBitwise).
- [`../opcode_cross/`](../opcode_cross/) — Cross + ignore/illegal pilot.
- [`../../../docs/explanations/architecture.md`](../../../docs/explanations/architecture.md) — coverage class hierarchy.
- [`../../../docs/glossary.md`](../../../docs/glossary.md) — term definitions.
