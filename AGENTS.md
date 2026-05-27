# AGENTS.md — repo orientation for AI agents and new contributors

This file is loaded by AI coding assistants (Claude Code, Cursor, etc.)
at session start. Human contributors should treat it as the README's
"map view" — read it before diving into a specific quadrant.

## What this repo is

**cocotbext-fcov** — a cocotb extension that lets you declare functional
coverage in Python (`CoverGroup` / `CoverPoint` / `Cross`) and emit
matching SystemVerilog `covergroup` declarations + Markdown spec tables
via the `make_coverage` CLI. Designed to plug into cocotb 2.0 testbenches.

## Repo map

```
.
├── README.md                            elevator pitch + install + docs/ pointer
├── NOTICE.md                            third-party attribution (cocotb upstream DUTs)
├── LICENSE                              MIT
├── pyproject.toml                       package metadata
│
├── cocotbext/fcov/                      the library source
│   ├── __init__.py                      public API re-exports (27 symbols)
│   ├── coverage.py                      CoverPoint / Cross / CoverGroup /
│   │                                    CoverageModel / CoverageCollector + helpers
│   ├── bins/{item,group,type}.py        BinItem + BinGroup + 17 Bin* predefined types
│   └── make_coverage.py                 CLI: walk a Python file -> emit .sv + .md
│
├── docs/                                Diátaxis-organised docs (see below)
│
└── tests/
    ├── pytest/                          pure-Python unit tests + emit snapshots (71 cases)
    └── cocotb/                          executable pilots that bind to docs/how-to/
        ├── _lib/Makefile.common         shared sim glue (Verilator + VCS + Questa)
        ├── conftest.py                  pytest harness for the pilots (opt-in marker)
        ├── README.md                    pilot index + run instructions
        └── {simple_dff, simple_counter, adder, register_sampling,
              opcode_cross, matrix_multiplier}/   6 pilots
```

## Where to start

| If you want to ... | Open |
|---|---|
| Build a coverage model end-to-end | `docs/tutorials/first-coverage-model.md` |
| Look up a class / method by name | `docs/reference/by-symbol.md` |
| Understand the chain BinItem → ... → CoverageCollector | `docs/explanations/architecture.md` |
| Sample coverage from a running cocotb test | `docs/how-to/sampling-in-cocotb.md` |
| Add `ignore_bins` / `illegal_bins` to a `Cross` | `docs/how-to/cross-with-ignore-illegal.md` |
| Pick the right `Bin*` for an intent | `docs/how-to/bin-type-recipes.md` |
| Build a multi-coverpoint hierarchy from scratch | `docs/how-to/build-coverage-hierarchy.md` |
| Wire `cov_model` into a real cocotb test | `docs/how-to/wire-into-testbench.md` |
| Understand the `coverage.sv` module layout `make_coverage` emits | `docs/reference/sv-emission-model.md` |
| Run a worked example end-to-end on Verilator / VCS / Questa | `tests/cocotb/<pilot>/README.md` |

## Diátaxis layout (`docs/`)

- `docs/reference/` — symbol-level. One page per class. Surface for AI lookups by name.
- `docs/how-to/` — task recipes. 5 pages. Each binds to one cocotb pilot.
- `docs/tutorials/` — handheld walks. 1 page (first-coverage-model).
- `docs/explanations/` — concept orientation. `architecture.md` is the canonical hierarchy diagram every reference page breadcrumbs back to.
- `docs/glossary.md` — 12 term definitions cross-linked everywhere.
- `docs/ko/` — Korean mirror (how-to + tutorial + explanations + glossary). Reference stays English by policy (`docs/ko/TRANSLATION_POLICY.md`).

## Tests

- `pytest tests/pytest/` — fast, pure-Python unit + emit snapshot tests. Run by default.
- `pytest -m cocotb_sim tests/cocotb/` — opt-in pilot suite. Spawns Verilator / VCS / Questa via cocotb 2.0. Slow.

## Common commands

```bash
# Install (editable)
pip install -e .

# Pure-Python tests
cd tests/pytest && pytest -q

# One pilot on Verilator (default)
cd tests/cocotb/simple_dff && make sim

# Same pilot on VCS / Questa (needs the EDA env sourced)
source /root-openebs/workspace/stork-dv/stork_dv.env
SIM=vcs    make sim
SIM=questa make sim

# Generate coverage.sv / coverage.md from a spec
make_coverage -f my_coverage_spec.py -sv coverage.sv -md coverage.md
```

## Known quirks (the kind that bite first-time contributors)

- **`BASH_ENV` workaround.** Some hosts set `BASH_ENV=/etc/environment`,
  which forces every non-interactive bash subshell to re-source that
  file and reset `PATH`. The cocotb recursive `$(MAKE)` then loses
  the EDA tool paths. `tests/cocotb/_lib/Makefile.common` unsets
  `BASH_ENV` to neutralise this. If you write your own Makefile,
  inherit `Makefile.common` rather than rolling your own.

- **Verilator covergroup is no-op.** Verilator 5.038–5.042 (and devel
  5.049) parse covergroup syntax but ignore it at runtime
  (`COVERIGN` warning). The `always @(<sample>) <cg_inst>.sample();`
  block also fails to elaborate. The shared Makefile wraps that line
  in `` `ifndef VERILATOR ... `endif `` on Verilator runs. Functional
  bin hit counting requires VCS or Questa.

- **Cross `value_spec` takes integer values, not bin names.** SV LRM
  19.5 — `binsof(cp) intersect {<set>}` must be a set of integer
  values. The natural-feeling `[(cp_op, "AND")]` raises
  `Identifier not declared` on VCS/Questa. Use `[(cp_op, int(Op.AND))]`.

- **`BinTransition((1, 2), (2, 1))` auto-names collide.** Both
  transitions derive `bin_1_2` from their min/max, tripping the
  duplicate-name guard. Use the explicit-name list form
  `[("up", [1, "=>", 2]), ("down", [2, "=>", 1])]` instead. The
  simple_dff and opcode_cross pilots both surface this.

## Decision rationale

The longer-form "why is the docs / pilots structured this way?"
discussions live in the maintainer's local `.claude/plan/` directory
(gitignored). Commit messages capture the load-bearing decisions
inline. If you need historical context that the commit message
doesn't carry, ask the maintainer.
