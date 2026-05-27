# cocotbext-fcov

A cocotb extension that allows defining functional coverage in Python and
automatically generates industry-standard SystemVerilog covergroups.

## Installation

```bash
git clone https://github.com/furiosa-ai/cocotbext-fcov
pip install ./cocotbext-fcov
```

## Documentation

Full documentation lives under [`docs/`](docs/) — Diátaxis-organised:

| Where | Open |
|---|---|
| First walk-through | [docs/tutorials/first-coverage-model.md](docs/tutorials/first-coverage-model.md) |
| Task-oriented recipes | [docs/how-to/](docs/how-to/) |
| Symbol-level reference | [docs/reference/](docs/reference/) ([by-symbol](docs/reference/by-symbol.md)) |
| Conceptual orientation | [docs/explanations/](docs/explanations/) |
| Executable pilots (Verilator + VCS + Questa) | [examples/](examples/) |
| Third-party attribution | [NOTICE.md](NOTICE.md) |
| 한국어 | [docs/ko/](docs/ko/) |

## Quick taste

```python
from cocotbext.fcov import CoverGroup, CoverPoint, Cross, BinBool, BinRange

class CustomCoverGroup(CoverGroup):
    cp_bool = CoverPoint(BinBool())
    cp_range = CoverPoint(BinRange(10))
    cx_bool_range = Cross([cp_bool, cp_range])

cg = CustomCoverGroup(name="cg_custom")
print(cg.systemverilog())
# covergroup cg_custom;
#   cp_bool:  coverpoint cg_custom_cp_bool  { ... }
#   cp_range: coverpoint cg_custom_cp_range { bins bin_0_9 = {[0:9]}; }
#   cx_bool_range: cross cp_bool, cp_range;
# endgroup
```

Full emit + walk-through: [docs/tutorials/first-coverage-model.md](docs/tutorials/first-coverage-model.md).

## License

See [LICENSE](LICENSE).
