# Third-party notices

This repository is distributed under the MIT License (see `LICENSE`). It also
incorporates files from the projects listed below; each retains its original
license, identified by the file's `SPDX-License-Identifier` header.

## cocotb examples (CC0-1.0 — public domain)

| File in this repo | Original location | License |
|-------------------|-------------------|---------|
| `tests/cocotb/simple_dff/dff.sv` | https://github.com/cocotb/cocotb/blob/master/examples/simple_dff/dff.sv | CC0-1.0 |
| `tests/cocotb/adder/adder.sv` | https://github.com/cocotb/cocotb/blob/master/examples/adder/hdl/adder.sv | CC0-1.0 |
| `tests/cocotb/matrix_multiplier/matrix_multiplier.sv` | https://github.com/cocotb/cocotb/blob/master/examples/matrix_multiplier/hdl/matrix_multiplier.sv | CC0-1.0 |

Public-domain dedication; reproduced verbatim. No additional notice required
by the dedication itself, but the SPDX header on the file makes provenance
explicit.

## Adding a new vendored source

1. Preserve the original `SPDX-License-Identifier` header on the file.
2. If the original lacks a header, add one matching the upstream license.
3. Append a row to the relevant license section of this file with the source
   URL and a short note on any modifications.
4. If the license requires attribution beyond an SPDX tag (e.g. BSD-3 retains
   the copyright notice + disclaimer), reproduce that text on the file itself.
