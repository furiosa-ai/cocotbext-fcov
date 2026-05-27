"""Emit snapshot test — every public Bin* type renders SystemVerilog
identically across releases.

Each entry pairs a small constructor call with the expected
`.systemverilog()` output. This is the canonical Track A backing for
the bin-type-recipes how-to guide; the SV strings here are what the
guide claims `make_coverage` will emit.

Coverage of the 19 emit patterns the docs cycle considers:
  BinSingle, BinUniform, BinRange,
  BinDict, BinEnum, BinBool,
  BinExp, BinMinMax, BinMinMaxUniform, BinMinMaxExp,
  BinWindow, BinOneHot,
  BinDefault, BinOutOfSpec, BinBitwise,
  BinTransition,
  BinCustom,
  Cross via CoverPoint integration (sanity check covered elsewhere),
  ignore_bins / illegal_bins (covered by examples/opcode_cross at sim level).
"""

from __future__ import annotations

from enum import IntEnum

import pytest

from cocotbext.fcov import (
    BinBitwise,
    BinBool,
    BinCustom,
    BinDefault,
    BinDict,
    BinEnum,
    BinExp,
    BinGroup,
    BinMinMax,
    BinMinMaxExp,
    BinMinMaxUniform,
    BinOneHot,
    BinOutOfSpec,
    BinRange,
    BinSingle,
    BinTransition,
    BinUniform,
    BinWindow,
)


class _ExampleEnum(IntEnum):
    FALSE = 0
    TRUE = 1


# (id, instance, expected_sv) tuples.
SNAPSHOTS: list[tuple[str, BinGroup, str]] = [
    ("BinSingle_int",
     BinSingle(7),
     "bins bin_7 = {7};"),
    ("BinSingle_range",
     BinSingle(range(10)),
     "bins bin_0_9 = {[0:9]};"),

    ("BinUniform_default_num",
     BinUniform(10),
     "bins bin_0_9[] = {[0:9]};"),
    ("BinUniform_with_num",
     BinUniform(10, 20, num=5),
     "bins bin_10_19[5] = {[10:19]};"),

    ("BinRange",
     BinRange(10, 20),
     "bins bin_10_19[] = {[10:19]};"),

    ("BinDict",
     BinDict({"LOW": 0, "HIGH": 1}),
     "bins LOW = {0};\nbins HIGH = {1};"),

    ("BinEnum",
     BinEnum(_ExampleEnum),
     "bins FALSE = {0};\nbins TRUE = {1};"),

    ("BinBool",
     BinBool(),
     "bins FALSE = {0};\nbins TRUE = {1};"),

    ("BinExp",
     BinExp(100, base=10),
     "bins bin_0 = {0};\nbins bin_1_9 = {[1:9]};\nbins bin_10_99 = {[10:99]};"),

    ("BinMinMax",
     BinMinMax(min=100, max=200, num=5),
     "bins bin_100 = {100};\nbins bin_101_199[3] = {[101:199]};\nbins bin_200 = {200};"),
    ("BinMinMaxUniform_alias",
     BinMinMaxUniform(min=100, max=200, num=5),
     "bins bin_100 = {100};\nbins bin_101_199[3] = {[101:199]};\nbins bin_200 = {200};"),

    ("BinMinMaxExp",
     BinMinMaxExp(min=100, max=200, base=2),
     "bins bin_100 = {100};\nbins bin_101_127 = {[101:127]};\n"
     "bins bin_128_199 = {[128:199]};\nbins bin_200 = {200};"),

    ("BinWindow",
     BinWindow(0x6, width=6, shift=2),
     "bins bin_0x6 = {'h6};\nbins bin_0x18 = {'h18};\nbins bin_0x20 = {'h20};"),

    ("BinOneHot_w3",
     BinOneHot(width=3, format="b"),
     "bins bin_0b1 = {'b1};\nbins bin_0b10 = {'b10};\nbins bin_0b100 = {'b100};"),

    ("BinDefault",
     BinDefault(),
     "bins others = default;"),

    ("BinTransition",
     BinTransition((1, 2, 3), (4, 5, 6)),
     "bins bin_1_3 = (1 => 2 => 3);\nbins bin_4_6 = (4 => 5 => 6);"),

    ("BinCustom",
     BinCustom({"alpha": 1, "beta": 2, "gamma": 3}),
     "bins alpha = {1};\nbins beta = {2};\nbins gamma = {3};"),
]


@pytest.mark.parametrize(
    "name, instance, expected",
    SNAPSHOTS,
    ids=[s[0] for s in SNAPSHOTS],
)
def test_bin_emit_snapshot(name: str, instance: BinGroup, expected: str) -> None:
    """Each Bin* type renders to the documented SV emit verbatim."""
    actual = instance.systemverilog()
    assert actual == expected, (
        f"\n{name}: SV emit drift\n"
        f"--- expected ---\n{expected}\n"
        f"--- actual   ---\n{actual}\n"
    )


def test_BinBitwise_emit_smoke() -> None:
    """BinBitwise has per-bit coverpoint emit (handled by CoverPoint, not
    BinGroup); the bare BinGroup.systemverilog() is non-fatal but empty
    or pass-through."""
    sv = BinBitwise(width=3).systemverilog()
    assert isinstance(sv, str)


def test_BinOutOfSpec_emits_empty() -> None:
    """BinOutOfSpec is documentation-only; SV emit is the empty string."""
    assert BinOutOfSpec().systemverilog() == ""


def test_BinOutOfSpec_markdown_is_marker() -> None:
    """The Markdown emit identifies the bin as 'Out of spec'."""
    assert BinOutOfSpec().markdown() == "Out of spec"
