from __future__ import annotations

from typing import Dict, Iterable

from .item import BinItem


class BinGroup:
    def __init__(
        self,
        bins: Iterable | None = None,
        width: int | None = None,
        prefix: str = "bin",
        format: str | None = None,
    ):
        self._width = width
        self.prefix = prefix
        self.format = format

        self.bins = bins

    def _to_bin_item(self, bin_info):
        def from_bin_info(bin_info):
            if (
                isinstance(bin_info, Iterable)
                and (bin_info[0] is None or isinstance(bin_info[0], str))
                and len(bin_info) == 2
            ):
                num = bin_info[1].num if isinstance(bin_info[1], BinItem) else 1
                return *bin_info, num
            elif (
                isinstance(bin_info, Iterable)
                and (bin_info[0] is None or isinstance(bin_info[0], str))
                and len(bin_info) == 3
            ):
                if isinstance(bin_info[1], BinItem):
                    num = bin_info[2]
                    assert bin_info[1].num == num
                return bin_info
            else:
                num = bin_info.num if isinstance(bin_info, BinItem) else 1
                return None, bin_info, num

        name, items, num = from_bin_info(bin_info)
        return BinItem(
            items=items,
            width=self._width,
            name=name,
            num=num,
            prefix=self.prefix,
            format=self.format,
        )

    def _update_bins(self, bins):
        if bins is None:
            return dict()
        if isinstance(bins, BinGroup):
            return bins.bins
        # special case: range, not recommanded
        if isinstance(bins, range) and bins.step == 1:
            bins = [(None, bins, 0)]
        if isinstance(bins, dict):
            bins = list(bins.items())

        named_bins = list(self._to_bin_item(i) for i in bins)
        bins = dict((i.name, i) for i in named_bins)
        # TODO: print duplicated keys
        assert len(named_bins) == len(bins), f"There are some duplicated bin names in BinGroup"

        return bins

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(bins=({self.__str__()}), width={self._width},"
            f" prefix={self.prefix}, format={self.format})"
        )

    def __str__(self):
        str_list = [v.as_string(shorten=True) for v in self.bins.values()]
        str_list = ["(" + s + ")" if ", " in s else s for s in str_list]
        return ", ".join(str_list)

    def _check_attrs(self):
        return self.type, self.width, *sorted(self.bins.values(), key=hash)

    def __eq__(self, other):
        if not isinstance(other, BinGroup):
            try:
                other = BinGroup(self._update_bins(other))
            except:
                return False
        return self._check_attrs() == other._check_attrs()

    def __hash__(self):
        return hash(self._check_attrs())

    def __add__(self, value):
        bins = self.bins
        bins.update(self._update_bins(value))
        return BinGroup(bins, self._width, self.prefix, self.format)

    def __radd__(self, value):
        bins = self._update_bins(value)
        bins.update(self.bins)
        return BinGroup(bins, self._width, self.prefix, self.format)

    def __iter__(self):
        return self._bins.__iter__()

    def __len__(self):
        return sum(i.num for i in self._bins.values())

    def __getitem__(self, key):
        return self._bins[key]

    def __setitem__(self, key, value):
        self._bins[key] = self._to_bin_item((key, value))

    @property
    def type(self):
        return self.__class__.__name__.replace("Bin", "").replace("Group", "Custom")

    @property
    def bins(self) -> Dict[str, BinItem]:
        return self._bins

    @bins.setter
    def bins(self, value):
        self._bins = self._update_bins(value)

    @property
    def max(self):
        max_list = [i.max for i in self.bins.values() if i.max is not None]
        return max(max_list) if max_list else None

    @property
    def min(self):
        min_list = [i.min for i in self.bins.values() if i.min is not None]
        return min(min_list) if min_list else None

    @property
    def width(self):
        if self._width is not None:
            return self._width

        width_list = [i.width for i in self.bins.values() if i.width is not None]
        return max(width_list) if width_list else None

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def num(self):
        return self.__len__()

    def empty(self):
        return self.num == 0

    def keys(self):
        return self.bins.keys()

    def values(self):
        return self.bins.values()

    def items(self):
        return self.bins.items()

    def update(self, bins):
        self.bins.update(self._update_bins(bins))

    def add(self, bins):
        self.update(bins)

    def append(self, bin):
        self.update([bin])

    def systemverilog(self, format: str | None = None, keyword: str = "bins"):
        if format is None:
            format = self.format

        bin_sv_list = [
            v.systemverilog(format=format, keyword=keyword) + ";" for v in self.bins.values() if not v.is_default()
        ]
        bin_sv_list += [
            v.systemverilog(format=format, keyword=keyword) + ";" for v in self.bins.values() if v.is_default()
        ]
        return "\n".join(bin_sv_list)

    def markdown(self, format: str | None = None, shorten=True, enum=False):
        if format is None:
            format = self.format

        bin_md_list = [
            v.markdown(format=format, shorten=shorten, enum=enum) for v in self.bins.values() if not v.is_default()
        ]
        bin_md_list += [
            v.markdown(format=format, shorten=shorten, enum=enum) for v in self.bins.values() if v.is_default()
        ]
        if shorten and len(bin_md_list) > 6:
            return ", ".join(bin_md_list[:3] + ["..."] + bin_md_list[-2:])
        else:
            return ", ".join(bin_md_list)
