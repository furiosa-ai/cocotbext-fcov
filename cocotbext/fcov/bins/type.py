from __future__ import annotations

import math
import numpy as np
from enum import Enum, IntEnum
from typing import Dict, Iterable

from .group import BinGroup


class BinCustom(BinGroup):
    """Hand-curated bin set with no auto-naming.

    Identical surface to :class:`BinGroup`; exists as a semantic marker
    in user code: "I explicitly want a custom layout, not one of the
    predefined patterns." Markdown rendering keeps full bin text rather
    than collapsing long lists.
    """

    pass


class BinSingle(BinGroup):
    """A single coverage bin around one value or range.

    ``CoverPoint(BinSingle(7))`` → ``bins bin_7 = {7};``.
    ``CoverPoint(BinSingle(range(10)))`` → ``bins bin_0_9 = {[0:9]};``.

    Args:
        value: Int, ``range``, or any value accepted by :class:`BinItem`.
        width: Optional fixed bit width.
        name: Explicit bin label; if ``None``, auto-generated from value.
        prefix: Prefix for auto-generated names.
        format: Integer format (``"b"``/``"o"``/``"d"``/``"h"``).
    """

    def __init__(
        self,
        value,
        width: int | None = None,
        name: str | None = None,
        prefix: str = "bin",
        format: str | None = None,
    ):
        super().__init__(bins=[(name, value)], width=width, prefix=prefix, format=format)


class BinUniform(BinGroup):
    """Open-array bin spanning ``range(*args)``, split evenly via ``num``.

    Used like Python's ``range()``. ``BinUniform(10)`` covers 0--9 in one
    open array (``[]``); ``BinUniform(10, 20, num=5)`` covers 10--19
    split into 5 sub-bins.

    Args:
        *args: ``range``-style positional arguments (``stop``, or
            ``start, stop``, or ``start, stop, step``).
        width: Optional fixed bit width; required if ``*args`` empty.
        num: SV array size (``0`` = open ``[]``, ``N`` = ``[N]``).
        name: Explicit bin label.
        prefix: Default name prefix.
        format: Integer format.
    """

    def __init__(
        self,
        *args,
        width: int | None = None,
        num: int = 0,
        name: str | None = None,
        prefix: str = "bin",
        format: str | None = None,
    ):
        bins = self._get_bins(*args, width=width, num=num, name=name)
        super().__init__(bins=bins, width=width, prefix=prefix, format=format)

    def _get_bins(self, *args, width: int, num: int, name: str | None):
        if args:
            range_info = range(*args)
        else:
            range_info = range(1 << width)
        return [(name, range_info, num)]


class BinRange(BinUniform):
    """Same as :class:`BinUniform` but always open-array (no ``num``).

    ``BinRange(10)`` → ``bins bin_0_9[] = {[0:9]};``. Use when the bin
    spec is a contiguous range and per-value sub-binning is not desired.
    """

    def __init__(
        self,
        *args,
        width: int | None = None,
        name: str | None = None,
        prefix: str = "bin",
        format: str | None = None,
    ):
        super().__init__(*args, width=width, num=0, name=name, prefix=prefix, format=format)


class BinDict(BinGroup):
    """Bin set built from ``{name: value}`` mapping.

    Useful for human-readable bin labels: ``BinDict({"IDLE": 0,
    "BUSY": 1})``. Markdown rendering keeps full bin text (no ellipsis).

    Args:
        bins: ``{str: value}`` mapping; ``value`` follows
            :class:`BinItem` rules.
        width: Optional fixed bit width.
        prefix: Default name prefix (rarely used since names are explicit).
        format: Integer format.
    """

    def __init__(
        self,
        bins: Dict,
        width: int | None = None,
        prefix: str = "bin",
        format: str | None = None,
    ):
        super().__init__(bins=bins, width=width, prefix=prefix, format=format)

    def markdown(self, format: str | None = None, shorten: bool | None=False, enum=True):
        if shorten is None:
            shorten = False
        return super().markdown(format, shorten, enum)


class BinEnum(BinDict):
    """Bin set derived from a Python ``Enum``.

    ``BinEnum(Bool)`` reads members of the enum and creates one bin per
    member, named with the member's ``.name`` and binned on
    ``.value``. Accepts either an ``Enum`` subclass or an iterable of
    members.

    Args:
        enums: ``Enum`` subclass, or any iterable yielding enum members.
        width: Optional fixed bit width.
        prefix: When set, all bin names get ``{prefix}_`` prepended.
        format: Integer format (often ``"b"`` for enums).
    """

    def __init__(
        self,
        enums: Iterable[Enum],
        width: int | None = None,
        prefix: str | None = None,
        format: str | None = None,
    ):
        try:
            if issubclass(enums, Enum):
                bins = {k: v.value for k, v in enums.__members__.items()}
            else:
                bins = {e.name: e.value for e in enums}
        except:
            bins = {e.name: e.value for e in enums}

        if prefix is not None:
            bins = {prefix + "_" + k: v for k, v in bins.items()}
        super().__init__(bins=bins, width=width, format=format)


class BinBool(BinEnum):
    """Boolean two-bin set: ``FALSE = 0``, ``TRUE = 1``.

    Built on a private ``IntEnum``; width fixed at 1. Equivalent to
    ``BinEnum`` over a bool-shaped enum but written as a one-liner.
    """

    def __init__(self, prefix: str | None = None, format: str | None = None):
        class BoolType(IntEnum):
            FALSE = False
            TRUE = True

        super().__init__(enums=BoolType, width=1, prefix=prefix, format=format)


class BinExp(BinGroup):
    """Exponential-bucket bin set over ``range(*args)``.

    Slices the range into buckets bounded by powers of ``base``. For
    ``BinExp(100, base=10)`` this yields ``{0}, [1:9], [10:99]``.
    Useful for latency / size distributions where small values matter
    more than large.

    Args:
        *args: ``range``-style positional arguments (default starts at 0).
        width: Optional fixed bit width; required if ``*args`` empty.
        base: Bucket multiplier (``>= 2``); default 2.
        prefix: Default name prefix.
        format: Integer format.
    """

    def __init__(
        self,
        *args,
        width: int | None = None,
        base: int = 2,
        prefix: str = "bin",
        format: str | None = None,
    ):
        bins = self._get_bins(*args, base=base, width=width)
        super().__init__(bins=bins, width=width, prefix=prefix, format=format)

    def _get_bins(self, *args, base: int, width: int | None):
        range_info = range(*args) if args else None
        assert range_info is not None or width is not None, "Error!! Need range info or width info for BinExp"
        assert base >= 2, "Error!! base should be greater than or equal to 2"

        if range_info is None:
            range_info = range(1 << width)

        bins = []
        start = range_info.start
        step = range_info.step
        if start > 0:
            start = base ** math.floor(math.log(range_info.start, base))
        elif start < 0:
            start = -(base ** math.ceil(math.log(np.abs(range_info.start), base)))
        while start < range_info.stop:
            stop = start * base if start > 0 else start // base if start < -1 else start + 1

            start = max(start, range_info.start)
            stop = min(stop, range_info.stop)
            bins.append(range(start, stop, step))

            start = stop

        return bins


class BinMinMax(BinUniform):
    """Uniform bin set with explicit boundary bins on ``min`` and ``max``.

    Splits ``[min+1, max-1]`` into ``num-2`` interior buckets, sandwiching
    them between two single-value boundary bins. Used to enforce coverage
    on the endpoints of a numeric range.

    Args:
        min: Lower boundary value (default ``0``).
        max: Upper boundary value (default ``(1<<width)-1``); at least
            one of ``max`` / ``width`` must be supplied.
        width: Optional fixed bit width.
        num: Total bin count including the two boundary bins (default 3).
        name: Base label for auto-generated boundary names.
        prefix: Default name prefix.
        format: Integer format.
    """

    def __init__(
        self,
        min: int | None = None,
        max: int | None = None,
        width: int | None = None,
        num: int = 3,
        name: str | None = None,
        prefix: str = "bin",
        format: str | None = None,
    ):
        bins = self._get_bins(min, max, width, num, name)
        BinGroup.__init__(self, bins=bins, width=width, prefix=prefix, format=format)

    def _check_min_max(self, min_value, max_value, width):
        assert (
            max_value is not None or width is not None
        ), f"Error!! one of max value ({max_value}) and width ({width}) should be assgined in BinMinMax!"

        min_value = 0 if min_value is None else min_value
        max_value = (1 << width) - 1 if max_value is None else max_value
        assert (
            min_value <= max_value
        ), f"Error!! max value ({max_value}) should be greater than or equal to min value ({min_value})"

        return min_value, max_value

    def _get_bins(self, min_value, max_value, width, num, name):
        min_value, max_value = self._check_min_max(min_value, max_value, width)
        min_name = None if name is None else name + "_min"
        max_name = None if name is None else name + "_max"
        num = max_value - min_value + 1 if num == 0 else min(max_value - min_value + 1, num)

        bins = []
        if num >= 2:
            bins.append((min_name, min_value, 1))
        if num >= 3:
            bins += super()._get_bins(min_value + 1, max_value, width=width, num=num - 2, name=name)
        bins.append((max_name, max_value, 1))
        return bins


class BinMinMaxUniform(BinMinMax):
    """Alias for :class:`BinMinMax`. Same behaviour; clearer name when
    pairing with :class:`BinMinMaxExp` in a code review.
    """

    pass


class BinMinMaxExp(BinExp, BinMinMax):
    """Exponential bin set with explicit boundary bins on ``min`` and ``max``.

    Combines :class:`BinMinMax` boundary bins with :class:`BinExp`
    bucketing for the interior. Use for ranges where boundary coverage
    must be guaranteed while interior values follow an exponential
    distribution.

    Args:
        min: Lower boundary value.
        max: Upper boundary value (or supply ``width``).
        width: Optional fixed bit width.
        base: Exponential bucket multiplier (``>= 2``); default 2.
        prefix: Default name prefix.
        format: Integer format.
    """

    def __init__(
        self,
        min: int | None = None,
        max: int | None = None,
        width: int | None = None,
        base: int = 2,
        prefix: str = "bin",
        format: str | None = None,
    ):
        bins = self._get_bins(min, max, width, base)
        BinGroup.__init__(self, bins=bins, width=width, prefix=prefix, format=format)

    def _get_bins(self, min_value, max_value, width, base):
        min_value, max_value = self._check_min_max(min_value, max_value, width)

        bins = []
        bins.append((None, min_value, 1))
        bins += super()._get_bins(min_value + 1, max_value, base=base, width=width)
        bins.append((None, max_value, 1))
        return bins


class BinWindow(BinGroup):
    """Sliding-window bin set: ``window`` shifted left by ``shift`` bits
    repeatedly within ``width``.

    Each shifted value becomes one bin. ``BinWindow(0x6, width=6,
    shift=2)`` yields ``{0x6, 0x18, 0x20}``. Useful for protocols where
    coverage on a "marker" value sliding across positions is required.

    Args:
        window: Seed bit pattern (default ``1``).
        width: Required total bit width.
        shift: Per-step left shift (default ``window.bit_length()``).
        prefix: Default name prefix.
        format: Integer format (default ``"x"``).
    """

    def __init__(
        self,
        window: int = 1,
        width: int | None = None,
        shift: int | None = None,
        prefix: str = "bin",
        format: str | None = "x",
    ):
        bins = self._get_bins(window, width, shift)
        super().__init__(bins=bins, width=width, prefix=prefix, format=format)

    def _get_bins(self, window: int, width: int | None, shift: int | None):
        if shift is None:
            shift = window.bit_length()
        assert width is not None, "Error!! Need specified width value for BinWindow"

        mask = (1 << width) - 1
        bits = window & mask

        bins = []
        while bits > 0:
            bins.append([None, bits, 1])
            bits = (bits << shift) & mask
        return bins


class BinOneHot(BinWindow):
    """One-hot bin set: one bin per single-bit pattern across ``width`` bits.

    Specialisation of :class:`BinWindow` with ``window=1`` and
    ``shift=1``. ``BinOneHot(width=3)`` yields ``{0b1, 0b10, 0b100}``.
    """

    def __init__(self, width: int | None = None, prefix: str = "bin", format: str | None = "x"):
        super().__init__(width=width, prefix=prefix, format=format)


class BinDefault(BinGroup):
    """Single default catch-all bin.

    Emits ``bins others = default;`` in SystemVerilog. Add to a
    :class:`~cocotbext.fcov.CoverPoint` to assert that no out-of-spec
    values land.
    """

    def __init__(self, width: int | None = None, prefix: str = "bin", format: str | None = None):
        super().__init__(bins=[None], width=width, prefix=prefix, format=format)


# for design spec.
class BinOutOfSpec(BinGroup):
    """Documentation-only marker for "out of spec" coverage rows.

    Renders as nothing in SystemVerilog and as the literal string
    ``"Out of spec"`` in Markdown. Use to annotate a coverpoint in the
    spec table without emitting an actual bin.
    """

    def __init__(self, prefix: str = "bin", format: str | None = None):
        super().__init__(prefix=prefix, format=format)

    @property
    def num(self):
        return 0

    def systemverilog(self, format: str | None = None):
        return ""

    def markdown(self, format: str | None = None, shorten: bool | None=False, enum=True):
        return "Out of spec"


# TODO: lsb, msb options
class BinBitwise(BinGroup):
    """Per-bit ``0``/``1`` coverage spec for a ``width``-bit signal.

    Emits ``2 * width`` bins (one ``0`` and one ``1`` per bit position).
    Used to ensure every bit gets exercised both polarities. Renders
    in Markdown as the short literal ``"0, 1 for each bit"``.

    Args:
        width: Required signal bit width.
        prefix: Default name prefix.
        format: Integer format.
    """

    def __init__(self, width: int | None = None, prefix: str = "bin", format: str | None = None):
        assert width is not None, "Error!! width should be specified in BinBitwise"
        super().__init__(width=width, prefix=prefix, format=format)

    def __len__(self):
        return self.width * 2

    def markdown(self, format: str | None = None, shorten: bool | None=False, enum=True):
        return "0, 1 for each bit"


class BinTransition(BinGroup):
    """Multi-bin transition coverage spec.

    Each positional ``trans_bin`` is a sequence of values / ranges; the
    sequence is rendered as a SystemVerilog ``a => b => c`` transition.
    ``BinTransition((1, 2, 3), (range(10), range(20, 30)))`` emits two
    transition bins.

    Args:
        *trans_bins: One iterable per transition bin. Each entry is an
            iterable of ints / ranges / iterables (per :class:`BinItem`
            rules).
        width: Optional fixed bit width.
        prefix: Default name prefix.
        format: Integer format.
    """

    def __init__(
        self,
        *trans_bins,
        width: int | None = None,
        prefix: str = "bin",
        format: str | None = None,
    ):
        bins = self._get_bins(*trans_bins)
        super().__init__(bins, width, prefix, format)

    def _get_bins(self, *trans_bins):
        def add_arrow(trans):
            assert isinstance(trans, Iterable), "Error!! transition should be described as Iterable."
            if not trans:
                return []
            new_trans = [j for i in trans[:-1] for j in [i, "=>"]]
            new_trans.append(trans[-1])
            return new_trans

        bins = [add_arrow(trans) for trans in trans_bins]
        return bins
