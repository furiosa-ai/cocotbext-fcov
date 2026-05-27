---
title: make_coverage
component_type: script_cli
layer: scripts
src_path: cocotbext/fcov/make_coverage.py
src_symbols: [main, traverse_coverage_models]
related_guides: []
---
# make_coverage

> Read a Python file containing [`CoverageModel`](../coverage/model.md) instances; emit a SystemVerilog coverage module and a Markdown spec doc.

## TL;DR

| | |
|---|---|
| **What** | CLI utility installed alongside the package: `make_coverage`. |
| **When to use** | Whenever the coverage spec changes — regenerate `.sv` + `.md` outputs from a single Python source-of-truth. |
| **Key links** | [../coverage/model.md](../coverage/model.md) · [../coverage/covergroup.md](../coverage/covergroup.md) |

## Overview

- **Role**: Imports the supplied `--file <path.py>`, walks it for `CoverageModel` subclasses (via `traverse_type`), then writes the SV module + Markdown spec doc.
- **SV output** is wrapped in ``\`ifdef COCOTBEXT_FCOV ... \`endif`` so the same file is safe to include in synthesis flows that don't define the macro.
- **Verilog formatter**: when `verible-verilog-format` is on `PATH`, the SV output is reformatted in place.

**Does NOT cover:**

- Defining the coverage model itself → [`../coverage/model.md`](../coverage/model.md).

## Quick example

```bash
make_coverage -f my_spec.py -sv coverage.sv -md coverage.md --overwrite
```

Where `my_spec.py` declares one or more `CoverageModel` subclasses at module scope.

## CLI

```
make_coverage [-h] [--file FILE] [--sv_output SV_OUTPUT] [--md_output MD_OUTPUT] [--overwrite]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--file`, `-f` | `coverage.py` | Comma-separated Python files containing `CoverageModel` instances. |
| `--sv_output`, `-sv` | `coverage.sv` | Output path for SystemVerilog module. |
| `--md_output`, `-md` | `coverage.md` | Output path for Markdown spec doc. |
| `--overwrite`, `-w` | off | Force overwrite if outputs exist. |

## See also

- [../coverage/model.md](../coverage/model.md) — model semantics consumed by this CLI.
- [../coverage/covergroup.md](../coverage/covergroup.md) — what gets emitted per covergroup.
