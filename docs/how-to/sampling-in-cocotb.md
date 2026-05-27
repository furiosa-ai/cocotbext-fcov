---
title: Sampling coverage from a cocotb test
prerequisites: [first-coverage-model]
covers_components: [coverage.covergroup, coverage.model]
---
# Sampling coverage from a cocotb test

> Drive coverpoint values from a running cocotb test and trigger the
> SystemVerilog `sample()` event so coverage gets recorded.

> 🇰🇷 [한국어 버전](../ko/how-to/sampling-in-cocotb.md) · English below.

## TL;DR

| | |
|---|---|
| **Goal** | Wire a `CoverageCollector` to a DUT, set coverpoint values per transaction, call `sample()`. |
| **When to use** | After you have a [first coverage model](../tutorials/first-coverage-model.md); now you want it filled by real stimulus. |
| **Key APIs** | `CoverageCollector`, `CoverGroup.set`, `CoverGroup.sample`, `cp.value`, `cp <= value` |

This page answers:
- How does the Python `CoverGroup` reach the SV-side covergroup instance?
- When should `.sample()` fire — clock edge, handshake, or per-transaction?
- How do I sample only when a precondition holds?

## Overview

**Role.** The collector lives on the cocotb side; the SV module emitted by [`make_coverage`](../reference/scripts/make-coverage.md) lives on the DUT side. Connecting them is a single `connect()` call. After that, every covergroup instance in the model is reachable by attribute path.

**Does NOT cover:**

- Building the model → [tutorials/first-coverage-model.md](../tutorials/first-coverage-model.md).
- Bin-spec selection → [bin-type-recipes.md](bin-type-recipes.md).

## Wire the collector

```python
import cocotb
from cocotbext.fcov import CoverageCollector
from coverage_spec import TxnCovModel


class MyCollector(CoverageCollector):
    cov_model = TxnCovModel(name="cov_model")


@cocotb.test()
async def test_basic(dut):
    collector = MyCollector(dut, cov_model=TxnCovModel(name="cov_model"))
    # ... stimulus ...
```

> Verified: [`tests/pytest/test_coverage_model.py`](../../tests/pytest/test_coverage_model.py)
>
> Verified (sim-hit): [`tests/cocotb/adder/`](../../tests/cocotb/adder/) — paired pilot exercising `BinUniform` + `BinBitwise` + `BinBool` + `Cross` on a vendored cocotb adder DUT.

## Sample per transaction

The recommended pattern is one `sample()` per transaction (or per clock when the coverpoint tracks a register).

```python
cg = collector.cov_model.cg_txn

cg.set(cp_opcode=op, cp_size=size, cp_secure=secure)
cg.sample()

# or terser via __call__:
cg(cp_opcode=op, cp_size=size, cp_secure=secure)
```

## Sample on a precondition

Skip `sample()` when the transaction isn't valid for coverage:

```python
if not valid_handshake:
    return
cg(cp_opcode=op, cp_size=size, cp_secure=secure)
```

## Use `<=` sugar for one-by-one updates

```python
cg.cp_opcode <= op
cg.cp_size   <= size
cg.sample()
```

## Read current values

```python
state = cg.get()  # {"cp_opcode": <Opcode.READ>, "cp_size": 3, "cp_secure": False}
```

## See also

- [first-coverage-model.md](../tutorials/first-coverage-model.md) — build the model this guide samples.
- [../reference/coverage/covergroup.md](../reference/coverage/covergroup.md) — `CoverGroup` API.
- [../reference/coverage/model.md](../reference/coverage/model.md) — `CoverageCollector` API.
