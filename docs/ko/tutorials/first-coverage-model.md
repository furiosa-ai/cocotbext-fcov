---
source: ../../tutorials/first-coverage-model.md
source_hash: bootstrap
title: 첫 번째 coverage model
---
# 첫 번째 coverage model

> `cocotbext-fcov` 처음 사용자를 위한 walk-through: Python에서 covergroup
> 하나를 정의하고, `CoverageModel`에 부착한 뒤, `make_coverage`로
> SystemVerilog `.sv` + Markdown `.md`를 emit 한다.

<!-- KO mirror of ../../tutorials/first-coverage-model.md -->

## TL;DR

| | |
|---|---|
| **목표** | `coverage_spec.py` 하나 + 생성된 `coverage.sv` 하나 + 생성된 `coverage.md` 하나, end-to-end. |
| **소요 시간** | 15분. |
| **전제 조건** | `pip install ./cocotbext-fcov` (editable install 가능), Python 3.10+. |
| **Verified backing** | [`tests/pytest/test_coverage_model.py`](../../../tests/pytest/test_coverage_model.py) |

## 환경 준비

```bash
pip install -e .
```

CLI가 `PATH`에 있는지 확인한다:

```bash
make_coverage --help
```

## Step 1 — covergroup 선언

Spec을 둘 위치에 `coverage_spec.py`를 만든다:

```python
from enum import Enum
from cocotbext.fcov import (
    CoverageModel, CoverGroup, CoverPoint, Cross,
    BinBool, BinRange, BinEnum,
)


class Opcode(Enum):
    READ  = 0
    WRITE = 1
    NOP   = 2


class TxnCoverGroup(CoverGroup):
    cp_opcode = CoverPoint(BinEnum(Opcode), format="b")
    cp_size   = CoverPoint(BinRange(8))
    cp_secure = CoverPoint(BinBool())
    cx_opcode_size = Cross([cp_opcode, cp_size])
```

확인:

```bash
python -c "import coverage_spec; print('ok')"
```

## Step 2 — `CoverageModel`로 감싼다

`coverage_spec.py`에 추가:

```python
class TxnCovModel(CoverageModel):
    cg_txn = TxnCoverGroup()


cov_model = TxnCovModel(name="cov_model")
```

마지막 instance가 `make_coverage`가 module을 walk 할 때 찾는 대상이다.

확인:

```bash
python -c "from coverage_spec import cov_model; print(cov_model.systemverilog()[:80])"
# module cov_model();
#   wire [1:0] cg_txn_cp_opcode;
#   ...
```

## Step 3 — `.sv` + `.md` emit

```bash
make_coverage -f coverage_spec.py -sv coverage.sv -md coverage.md --overwrite
```

두 새 파일이 생성된다:

```bash
head -3 coverage.sv
# `ifdef COCOTBEXT_FCOV
# module cov_model();
#   ...
head -3 coverage.md
# ## cov_model
#
# ### cg_txn
```

## 결과물

Python 한 파일이 source-of-truth가 되고, DUT include 가능한 SystemVerilog module과 사람이 리뷰할 수 있는 Markdown spec doc이 함께 생성된다. `coverage_spec.py` 수정은 `make_coverage`를 통해 두 출력에 모두 반영된다.

## 다음 단계

- **실제 cocotb 테스트에서 covergroup을 sample**: [how-to/sampling-in-cocotb.md](../how-to/sampling-in-cocotb.md).
- **더 다양한 bin 형태** (exp, min/max, transition, one-hot, ...): [reference/bins/type.md](../../reference/bins/type.md) + [how-to/bin-type-recipes.md](../how-to/bin-type-recipes.md).
- **Cross-level ignore / illegal 필터**: [how-to/cross-with-ignore-illegal.md](../how-to/cross-with-ignore-illegal.md).
- **`Bin*` 상속 지도**: [explanations/bin-type-hierarchy.md](../explanations/bin-type-hierarchy.md).

## 관련 문서

- [reference/coverage/model.md](../../reference/coverage/model.md) — `CoverageModel` API.
- [reference/scripts/make-coverage.md](../../reference/scripts/make-coverage.md) — CLI flag.
- [../../tutorials/first-coverage-model.md](../../tutorials/first-coverage-model.md) — English 원본.
