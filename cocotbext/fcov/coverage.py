from __future__ import annotations

import pandas as pd
from copy import deepcopy, copy
from math import prod
from typing import Any, Dict, Iterable
from itertools import chain

import cocotb
from cocotb.log import SimLog
from cocotb.triggers import Edge, Event
from cocotb.binary import BinaryValue

from .bins.group import BinGroup
from .bins.type import BinBitwise, BinOutOfSpec


def compact_index(index=None):
    if not index:
        return ""
    index = sorted(index)

    ranges = []

    def append_range(start, end):
        if start == end:
            ranges.append(str(start))
        else:
            ranges.append(f"{start}-{end}")

    start = end = index[0]
    for i in index[1:]:
        if i == end + 1:
            end += 1
        else:
            append_range(start, end)
            start = end = i
    append_range(start, end)

    ranges_str = ", ".join(ranges)
    if "-" in ranges_str or "," in ranges_str:
        return "{" + ranges_str + "}"
    else:
        return ranges_str


def traverse_type(obj, class_type, flatten):
    for var in dir(obj):
        attr = getattr(obj, var)
        if flatten:
            if isinstance(attr, class_type):
                yield var, attr, None
            elif isinstance(attr, Iterable):
                try:
                    for i, elem in enumerate(attr):
                        if isinstance(elem, class_type):
                            yield var, elem, i
                except:
                    pass
        else:
            if isinstance(attr, class_type):
                yield var, attr
            elif isinstance(attr, Iterable):
                try:
                    elem_list = [(i, elem) for i, elem in enumerate(attr) if isinstance(elem, class_type)]
                    if elem_list:
                        yield var, elem_list
                except:
                    pass


def get_markdown_list(key, value, seperator="_"):
    markdown_list = []
    if isinstance(value, list):
        while value:
            _, curr = value[0]
            if getattr(curr, "name", None):
                markdown_list.append(curr.markdown())
                value.pop(0)
            else:
                index_list = [i for i, v in value if curr == v]
                value = [(i, v) for i, v in value if curr != v]
                suffix = compact_index(index_list)
                markdown_list.append(curr.markdown(key + seperator + suffix))
    else:
        if getattr(value, "name", None):
            markdown_list.append(value.markdown())
        else:
            markdown_list.append(value.markdown(key))
    return markdown_list


# TODO: option
# TODO: reference to group
class CoverPoint:
    def __init__(
        self,
        bins: Iterable | None = None,
        ignore_bins: Iterable | None = None,
        illegal_bins: Iterable | None = None,
        width: int | None = None,
        name: str | None = None,
        group: str | None = None,
        ref: CoverPoint | None = None,
        prefix: str = "bin",
        format: str | None = None,
        log_level: str = "INFO",
    ) -> None:
        """
        bins:           included bins list
        ignore_bins:    ignored bins list
        illegal_bins:   illegal bins list
        width:          width of coverpoint
        name:           name of coverpoint
        group:          name of covergroup
        ref:            refered coverpoint. if set, use ref's signal and don't create own signal
        prefix:         name prefix of bins
        format:         value format (str). {b, o, d, x, h}
        log_level:      log level in cocotb simulation log
        """
        self.log = SimLog(f"cocotbext.fcov.{self.__class__.__name__}")
        self.log.setLevel(log_level)

        self.prefix = prefix
        self.format = format

        self.bins = bins if isinstance(bins, BinGroup) else BinGroup(bins, width=width, prefix=prefix, format=format)
        self.ignore_bins = (
            ignore_bins
            if isinstance(ignore_bins, BinGroup)
            else BinGroup(ignore_bins, width=width, prefix=prefix, format=format)
        )
        self.illegal_bins = (
            illegal_bins
            if isinstance(illegal_bins, BinGroup)
            else BinGroup(illegal_bins, width=width, prefix=prefix, format=format)
        )
        self._width = width

        self.name = name
        self.group = group
        self.ref = ref

        self._value = None

    def __copy__(self):
        return self.__class__(
            bins=self.bins,
            ignore_bins=self.ignore_bins,
            illegal_bins=self.illegal_bins,
            name=self.name,
            group=self.group,
            ref=self.ref,
            prefix=self.prefix,
            format=self.format,
        )

    def __deepcopy__(self, memo):
        return self.__copy__()

    def __repr__(self):
        ref_name = self.ref.name if self.ref else None
        return (
            f"CoverPoint(bins=({self.bins}), ignore_bins=({self.ignore_bins}),"
            f" illegal_bins=({self.illegal_bins}), width={self._width},"
            f" name={self.name}, group={self.group}, ref={ref_name})"
        )

    def __str__(self):
        return self.__repr__()

    def _check_attrs(self):
        return self.bins, self.ignore_bins, self.illegal_bins, self.width

    def __eq__(self, other):
        if not isinstance(other, CoverPoint):
            return False
        return self._check_attrs() == other._check_attrs()

    def __hash__(self):
        return hash(self._check_attrs())

    def __len__(self):
        return len(self.bins)

    @property
    def num(self):
        return self.__len__()

    @property
    def value(self) -> Any:
        if self.ref:
            return self.ref.value
        elif self._value is None:
            return self._handler.value
        else:
            return self._value

    @value.setter
    def value(self, value: Any):
        if self.ref:
            self.ref.value = value
            return

        if isinstance(value, str):
            value = BinaryValue(value)
        self._value = value

    def __le__(self, value):
        self.value = value

    def _drive(self, value=None):
        if self.ref:
            return self.ref._drive(value)

        if value is None:
            value = self.value
        if value is not None:
            self._handler.value = value

    @property
    def signal(self) -> str:
        if self.ref:
            return self.ref.signal

        assert self.name is not None, "Error!! coverpoint's name should not be None"
        assert self.group is not None, "Error!! coverpoint's group name should not be None"
        return self.group + "_" + self.name

    @property
    def max(self):
        if self.ref:
            return self.ref.max

        bins_max = list(
            filter(
                lambda x: x is not None,
                [self.bins.max, self.ignore_bins.max, self.illegal_bins.max],
            )
        )
        return max(bins_max) if bins_max else None

    @property
    def min(self):
        if self.ref:
            return self.ref.min

        bins_min = list(
            filter(
                lambda x: x is not None,
                [self.bins.min, self.ignore_bins.min, self.illegal_bins.min],
            )
        )
        return min(bins_min) if bins_min else None

    @property
    def width(self):
        if self.ref:
            return self.ref.width
        if self._width is not None:
            return self._width

        bins_width = list(
            filter(
                lambda x: x is not None,
                [self.bins.width, self.ignore_bins.width, self.illegal_bins.width],
            )
        )
        # assert bins_width, (
        #     f"Error!! Can't find width from bins. Need to specify width of CoverPoint. (bins: {self.bins.width}, ignore"
        #     f" bins: {self.ignore_bins.width}, illegal bins: {self.illegal_bins.width})"
        # )
        return max(bins_width) if bins_width else None

    @width.setter
    def width(self, value):
        self._width = value

    def set_name(self, name: str, group: str):
        self.name = name
        self.group = group

    def connect(self, coverage_instance):
        if self.ref:
            return

        if not hasattr(coverage_instance, self.signal):
            self.log.error(f"No coverpoint signal {self.signal}")
            assert False
        self._handler = getattr(coverage_instance, self.signal)

    @property
    def is_bitwise_bin(self):
        return isinstance(self.bins, BinBitwise)

    @property
    def is_out_of_spec(self):
        return isinstance(self.bins, BinOutOfSpec)

    def sv_wire(self) -> str:
        if self.ref:
            return None

        if not self.is_out_of_spec and self.width > 1:
            return f"wire [{self.width - 1}:0] {self.signal};"
        else:  # self.width == 1:
            return f"wire {self.signal};"

    def sv_declare(self) -> str:
        if self.is_out_of_spec:
            return None

        if self.is_bitwise_bin:
            assert self.ignore_bins.empty(), "No ignore bin is allowed for Bitwise Bins"
            assert self.illegal_bins.empty(), "No illegal bin is allowed for Bitwise Bins"
            assert self.bins.width, "Valid width value is needed"

            sv_coverpoints = f"{self.name}_0: coverpoint {self.signal}"
            sv_coverpoints += "[0];" if self.bins.width > 1 else ";"
            for i in range(1, self.bins.width):
                sv_coverpoints += f"\n{self.name}_{i}: coverpoint {self.signal}[{i}];"
            return sv_coverpoints
        else:
            sv_coverpoint = f"{self.name}: coverpoint {self.signal}"
            sv_bins = self.bins.systemverilog(format=self.format)
            if not self.ignore_bins.empty():
                sv_bins += "\n" + self.ignore_bins.systemverilog(keyword="ignore_bins", format=self.format)
            if not self.illegal_bins.empty():
                sv_bins += "\n" + self.illegal_bins.systemverilog(keyword="illegal_bins", format=self.format)
            sv_bins = " {\n" + sv_bins + "}" if sv_bins else ";"
            return sv_coverpoint + sv_bins

    def markdown(self, name: str | None = None, shorten: bool | None = None):
        if name is None:
            name = self.name

        return {
            "Coverpoint": name,
            "Width": f"[{self.width - 1}:0]" if self.width else "",
            "Bin Type": self.bins.type,
            "# of Bins": self.bins.num,
            "Bins": self.bins.markdown(format=self.format, shorten=shorten),
            "Ignore Bins": self.ignore_bins.markdown(format=self.format, shorten=shorten),
            "Illegal Bins": self.illegal_bins.markdown(format=self.format, shorten=shorten),
        }


# TODO: bins by index
class Cross:
    def __init__(
        self,
        coverpoints: Iterable[CoverPoint],
        name: str | None = None,
        group: str | None = None,
    ) -> None:
        """
        coverpoints:    coverpoints list to be crossed
        name:           name of cross
        group:          name of covergroup
        """
        self.coverpoints = coverpoints
        self.name = name
        self.group = group

    def __repr__(self):
        coverpoints = ", ".join(hex(id(cp)) if cp.name is None else cp.name for cp in self.coverpoints)
        return f"Cross(coverpoints=({coverpoints}), name={self.name}, group={self.group})"

    def __str__(self):
        return self.__repr__()

    def _check_attrs(self):
        return tuple(sorted(self.coverpoints, key=hash))

    def __eq__(self, other):
        if not isinstance(other, Cross):
            return False
        return self._check_attrs() == other._check_attrs()

    def __hash__(self):
        return hash(self._check_attrs())

    def set_name(self, name: str, group: str):
        self.name = name
        self.group = group

    def sv_declare(self):
        cross = {self.name: []}
        for cp in self.coverpoints:
            if cp.is_bitwise_bin:
                cp_width = cp.width
                if len(cross) == 1:
                    cx = list(cross.values())[0]
                    cross = {f"{self.name}_{i}": cx.copy() for i in range(cp_width)}

                assert cp_width == len(cross), (
                    "Error!! bitwise bin's width does not match with current cross's"
                    f" width ({cp.name}'s width ({cp_width}) != {len(cross)})"
                )

                for cx, i in zip(cross.values(), range(cp_width)):
                    cx.append(f"{cp.name}_{i}")
            else:
                for cx in cross.values():
                    cx.append(cp.name)

        sv_cross = [f"{k}: cross {', '.join(v)};" for k, v in cross.items()]
        return "\n".join(sv_cross)

    def markdown(self, name: str | None = None):
        if name is None:
            name = self.name

        return {
            "Cross": name,
            "Coverpoints": ", ".join(cp.name for cp in self.coverpoints),
            "# of Bins": prod(cp.num for cp in self.coverpoints),
        }


class CoverGroup:
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj._copy_coverpoints()
        return obj

    def __init__(self, name: str | None = None, log_level: str = "INFO"):
        """
        name:           name of covergroup
        log_level:      log level in cocotb simulation log
        """
        self.set_name(name)

        self.log = SimLog(f"cocotbext.fcov.{self.__class__.__name__}")
        self.log.setLevel(log_level)

        self._sample_handler = None
        self._sample_thread = None
        self._sample_event = Event()
        self._sample_values = []
        self._last_drive_values = None

        self._connected_coverpoints = None

    def _copy_coverpoints(self):
        cp_map = dict()
        for k, v in self._traverse_coverpoint(flatten=False):
            if isinstance(v, list):
                new_iterable = type(v)(copy(cp) for _, cp in v)
                setattr(self, k, new_iterable)
                for (_, cp), new_cp in zip(v, new_iterable):
                    cp_map[id(cp)] = new_cp
            else:
                new_cp = copy(v)
                setattr(self, k, new_cp)
                cp_map[id(v)] = new_cp

        for _, v, _ in self._traverse_coverpoint():
            if v.ref:
                v.ref = cp_map[id(v.ref)]

        def copy_cross(cross: Cross):
            new_cross = copy(cross)
            new_cross.coverpoints = type(cross.coverpoints)(cp_map[id(cp)] for cp in cross.coverpoints)
            return new_cross

        for k, v in self._traverse_cross(flatten=False):
            if isinstance(v, list):
                new_iterable = type(v)(copy_cross(cross) for _, cross in v)
                setattr(self, k, new_iterable)
            else:
                new_cross = copy_cross(v)
                setattr(self, k, new_cross)

    def __deepcopy__(self, memo):
        obj = copy(self)
        obj._copy_coverpoints()
        return obj

    def __str__(self):
        res = f"CoverGroup(name={self.name}"
        for _, v, _ in chain(self._traverse_coverpoint(), self._traverse_cross()):
            res += f", {v.name}={str(v)}"
        res += ")"
        return res

    def _check_attrs(self):
        return tuple(sorted((v for _, v, _ in chain(self._traverse_coverpoint(), self._traverse_cross())), key=hash))

    def __eq__(self, other):
        if not isinstance(other, CoverGroup):
            return False
        return self._check_attrs() == other._check_attrs()

    def __hash__(self):
        return hash(self._check_attrs())

    def _traverse_coverpoint(self, flatten=True):
        yield from traverse_type(self, CoverPoint, flatten)

    def _traverse_cross(self, flatten=True):
        yield from traverse_type(self, Cross, flatten)

    def set_name(self, name: str | None, seperator: str = "_"):
        self.name = name
        if self.name is None:
            return

        for k, v, i in chain(self._traverse_coverpoint(), self._traverse_cross()):
            if v.name is None:
                name = k if i is None else k + seperator + str(i)
            else:
                name = v.name
            v.set_name(name, self.name)

    def connect(self, coverage_instance):
        if not hasattr(coverage_instance, self.sample_name):
            self.log.error(f"No sample signal {self.sample_name} in CoverGroup {self.name}")
            assert False

        for _, v, _ in self._traverse_coverpoint():
            v.connect(coverage_instance)
        self._connected_coverpoints = dict(self._traverse_coverpoint(flatten=False))

        if self._sample_thread:
            self._sample_thread.kill()
        self._sample_handler = getattr(coverage_instance, self.sample_name)
        self._sample_thread = cocotb.start_soon(self._sample())

    def _get_connected_coverpoints(self):
        if self._connected_coverpoints is None:
            self._connected_coverpoints = dict(self._traverse_coverpoint(flatten=False))
        return self._connected_coverpoints

    def get(self) -> Dict:
        cp_map = self._get_connected_coverpoints()

        values = dict()
        for k, v in cp_map.items():
            if isinstance(v, list):
                values[k] = [cp.value for _, cp in v]
            else:
                values[k] = v.value
        return values

    def set(self, values: Dict = dict(), **kwargs):
        cp_map = self._get_connected_coverpoints()

        values.update(kwargs)
        for k, v in values.items():
            if k not in cp_map:
                self.log.error(f"CoverPoint {k} is not found in CoverGroup ({self.name}).")
                self.log.error(f"- input values = {values}")
                assert False

            cp = cp_map.get(k)
            if isinstance(cp, list):
                assert len(cp) == len(v), f"Length of values ({len(v)}) is not same to CoverPoint {k} ({len(cp)})"
                for (_, cpi), vi in zip(cp, v):
                    cpi.value = vi
            else:
                cp.value = v

    def _drive(self, values: Dict = dict(), **kwargs):
        values.update(kwargs)
        try:
            if values == self._last_drive_values:
                return
        except ValueError:
            pass

        cp_map = self._get_connected_coverpoints()
        self._last_drive_values = values

        for k, v in cp_map.items():
            if isinstance(v, list):
                k_value = values.get(k, [None] * len(v))
                assert len(v) == len(k_value), f"Length of values ({len(v)}) is not same to CoverPoint {k} ({len(v)})"
                for (_, cpi), valuei in zip(v, k_value):
                    cpi._drive(valuei)
            else:
                v._drive(values.get(k, None))

    def __call__(self, **kwargs):
        self.set(values=dict(), **kwargs)

    async def _sample(self):
        handler_value = bool(self._sample_handler.value)

        while True:
            await self._sample_event.wait()
            while self._sample_values:
                self._drive(self._sample_values.pop(0))
                self._sample_handler.value = handler_value = not handler_value
                await Edge(self._sample_handler)
            self._sample_event.clear()

    def sample(self):
        self._sample_values.append(self.get())
        self._sample_event.set()

    @property
    def sample_name(self):
        if hasattr(self, "name"):
            return str(self.name) + "_sample"

    @property
    def instance_name(self):
        if hasattr(self, "name"):
            return str(self.name) + "_inst"

    # methods for generating systemverilog
    def sv_wire(self):
        coverpoint_wire = [v.sv_wire() for _, v, _ in self._traverse_coverpoint() if v.ref is None]
        coverpoint_wire = [i for i in coverpoint_wire if i is not None]
        sample_wire = [f"wire {self.sample_name};"]
        return "\n".join(coverpoint_wire + sample_wire)

    def sv_declare(self) -> str:
        covergroup_start = [f"covergroup {self.name};"]
        coverpoint_declare = [v.sv_declare() for _, v, _, in self._traverse_coverpoint()]
        coverpoint_declare = [i for i in coverpoint_declare if i is not None]
        cross_declare = [x.sv_declare() for _, x, _ in self._traverse_cross()]
        covergroup_end = [f"endgroup : {self.name}"]
        return "\n".join(covergroup_start + coverpoint_declare + cross_declare + covergroup_end)

    def sv_instance(self):
        return f"{self.name} {self.instance_name} = new;"

    def sv_sample_event(self):
        return f"always@ ({self.sample_name}) begin {self.instance_name}.sample(); end"

    def systemverilog(self):
        sv_wire = self.sv_wire()
        sv_declare = self.sv_declare()
        sv_instance = self.sv_instance()
        sv_sample_event = self.sv_sample_event()
        valid_sv_list = [s for s in [sv_wire, sv_declare, sv_instance, sv_sample_event] if s != ""]
        return "\n\n".join(valid_sv_list) + "\n"

    def markdown(self, name: str | None = None):
        if name is None:
            name = self.name

        if name is None:
            output = f"### Covergroup {self.__class__.__name__}"
        else:
            output = f"### Covergroup {name}"
        output += "\n\n"

        coverpoint_list = []
        for k, v in self._traverse_coverpoint(flatten=False):
            coverpoint_list += get_markdown_list(k, v)

        coverpoint_df = pd.DataFrame.from_records(coverpoint_list)
        output += coverpoint_df.to_markdown(index=False, tablefmt="github")
        output += "\n\n"

        cross_list = []
        for k, v in self._traverse_cross(flatten=False):
            cross_list += get_markdown_list(k, v)

        if cross_list:
            cross_df = pd.DataFrame.from_records(cross_list)
            output += cross_df.to_markdown(index=False, tablefmt="github")
            output += "\n\n"

        return output


class CoverageModel:
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj._copy_covergroups()
        return obj

    def __init__(self, name: str | None = None, log_level: str = "INFO"):
        """
        name:           name of coverage model
        log_level:      log level in cocotb simulation log
        """
        self.set_name(name)

        self.log = SimLog(f"cocotbext.fcov.{self.__class__.__name__}")
        self.log.setLevel(log_level)

    def _copy_covergroups(self):
        cg_map = dict()
        for k, v in self._traverse_covergroup(flatten=False):
            if isinstance(v, list):
                new_iterable = type(v)(deepcopy(cg) for _, cg in v)
                setattr(self, k, new_iterable)
                for (_, cg), new_cg in zip(v, new_iterable):
                    cg_map[id(cg)] = new_cg
            else:
                new_cg = deepcopy(v)
                setattr(self, k, new_cg)
                cg_map[id(v)] = new_cg

    def __deepcopy__(self, memo):
        obj = copy(self)
        obj._copy_covergroups()
        return obj

    def __str__(self):
        res = f"CoverageModel(name={self.name}"
        for _, v, _ in self._traverse_covergroup():
            res += f", {v.name}={str(v)}"
        res += ")"
        return res

    def _check_attrs(self):
        return tuple(sorted((v for _, v, _ in self._traverse_covergroup()), key=hash))

    def __eq__(self, other):
        if not isinstance(other, CoverageModel):
            return False
        return self._check_attrs() == other._check_attrs()

    def __hash__(self):
        return hash(self._check_attrs())

    def _traverse_covergroup(self, flatten=True):
        yield from traverse_type(self, CoverGroup, flatten)

    def set_name(self, name=None, seperator="_"):
        self.name = name

        for k, v, i in self._traverse_covergroup():
            if v.name is None:
                name = k if i is None else k + seperator + str(i)
            else:
                name = v.name
            v.set_name(name, seperator=seperator)

    def connect(self, dut):
        if hasattr(dut, self.name):
            self.log.info("Coverage enabled for %s", self.name)
            cov_inst = getattr(dut, self.name)
            for _, v, _ in self._traverse_covergroup():
                v.connect(cov_inst)
        else:
            self.log.warning("Coverage instance %s does not exist in dut!", self.name)

    def systemverilog(self, name=None):
        if name is None:
            name = self.name
        header = f"module {name} ();\n"
        body = "\n".join([v.systemverilog() for _, v, _ in self._traverse_covergroup()])
        footer = "endmodule\n"
        return header + body + footer

    def markdown(self, name: str | None = None):
        if name is None:
            name = self.name

        if name is None:
            header = f"## {self.__class__.__name__}\n\n"
        else:
            header = f"## {name} ({self.__class__.__name__})\n\n"
        covergroup_list = []
        for k, v in self._traverse_covergroup(flatten=False):
            covergroup_list += get_markdown_list(k, v)
        body = "".join(covergroup_list)

        return header + body


class CoverageCollector:
    def __init__(self, dut, cov_model, log_level: str = "INFO", **kwargs) -> None:
        """
        dut:            cocotb entity for dut
        cov_model:      instances of coverage model
        log_level:      log level in cocotb simulation log
        """
        self.dut = dut

        self.log = SimLog(f"cocotbext.fcov.{self.__class__.__name__}")
        self.log.setLevel(log_level)

        self.connect_coverage(dut, cov_model)

    def connect_coverage(self, dut, cov_model):
        if isinstance(cov_model, CoverageModel):
            cov_model = [cov_model]
        if isinstance(cov_model, dict):
            for k, v in cov_model.items():
                v.set_name(k)
            cov_model = list(cov_model.values())

        for m in cov_model:
            m.connect(dut)
            setattr(self, m.name, m)
        self.cov = cov_model[0]
