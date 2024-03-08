from __future__ import annotations

import math
import numpy as np
from enum import Enum, IntEnum
from typing import Dict, Iterable

from .group import BinGroup


class BinCustom(BinGroup):
    pass


class BinSingle(BinGroup):
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
    def __init__(self, prefix: str | None = None, format: str | None = None):
        class BoolType(IntEnum):
            FALSE = False
            TRUE = True

        super().__init__(enums=BoolType, width=1, prefix=prefix, format=format)


class BinExp(BinGroup):
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
    pass


class BinMinMaxExp(BinExp, BinMinMax):
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
    def __init__(self, width: int | None = None, prefix: str = "bin", format: str | None = "x"):
        super().__init__(width=width, prefix=prefix, format=format)


class BinDefault(BinGroup):
    def __init__(self, width: int | None = None, prefix: str = "bin", format: str | None = None):
        super().__init__(bins=[None], width=width, prefix=prefix, format=format)


# for design spec.
class BinOutOfSpec(BinGroup):
    def __init__(self, prefix: str = "bin", format: str | None = None):
        super().__init__(prefix=prefix, format=format)

    @property
    def num(self):
        return 0

    def systemverilog(self, format: str | None = None):
        return ""

    def markdown(self, format: str | None = None, shorten: bool | None=False, enum=True):
        return "Out of spec"


class BinBitwise(BinGroup):
    def __init__(self, width: int | None = None, prefix: str = "bin", format: str | None = None):
        assert width is not None, "Error!! width should be specified in BinBitwise"
        super().__init__(width=width, prefix=prefix, format=format)

    def __len__(self):
        return self.width * 2

    def markdown(self, format: str | None = None, shorten: bool | None=False, enum=True):
        return "0, 1 for each bit"


class BinTransition(BinGroup):
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
