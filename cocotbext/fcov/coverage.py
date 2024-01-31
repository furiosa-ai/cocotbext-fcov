from __future__ import annotations

import pandas as pd
from copy import deepcopy
from math import prod
from typing import Any, Dict, Iterable
from itertools import chain

import cocotb
from cocotb.log import SimLog
from cocotb.triggers import Edge, Lock
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
        format: str = "d",
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
        ref_name = None if self.ref is None else self.ref.name
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
        if self._value is None:
            self._value = self._handler.value
        return self._value

    @value.setter
    def value(self, value: Any):
        if self.ref:
            self.ref.value = value
        else:
            if isinstance(value, str):
                value = BinaryValue(value)
            self._value = value
            self._handler.value = value

    def __le__(self, value):
        self.value = value

    @property
    def signal(self) -> str:
        if self.ref:
            return self.ref.signal
        else:
            assert self.name is not None, "Error!! coverpoint's name should be not None"
            assert self.group is not None, "Error!! coverpoint's group name should be not None"
            return self.group + "_" + self.name

    @property
    def width(self):
        if self.ref is not None:
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
        if self.ref is not None:
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

            sv_coverpoints = f"{self.name}_0: coverpoint {self.signal}[0];"
            for i in range(1, self.bins.width):
                sv_coverpoints += f"\n{self.name}_{i}: coverpoint {self.signal}[{i}];"
            return sv_coverpoints
        else:
            sv_coverpoint = f"{self.name}: coverpoint {self.signal}"
            sv_bins = self.bins.systemverilog()
            if not self.ignore_bins.empty():
                sv_bins += "\n" + self.ignore_bins.systemverilog(keyword="ignore_bins")
            if not self.illegal_bins.empty():
                sv_bins += "\n" + self.illegal_bins.systemverilog(keyword="illegal_bins")
            sv_bins = " {\n" + sv_bins + "}" if sv_bins else ";"
            return sv_coverpoint + sv_bins

    def markdown(self, name=None):
        if name is None:
            name = self.name

        return {
            "Coverpoint": name,
            "Width": f"[{self.width - 1}:0]" if self.width else "",
            "Bin Type": self.bins.type,
            "# of Bins": self.bins.num,
            "Bins": self.bins.markdown(),
            "Ignore Bins": self.ignore_bins.markdown(),
            "Illegal Bins": self.illegal_bins.markdown(),
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

    def markdown(self):
        return {
            "Cross": self.name,
            "Coverpoints": ", ".join(cp.name for cp in self.coverpoints),
            "# of Bins": prod(cp.num for cp in self.coverpoints),
        }


class CoverGroup:
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)

        # using deepcopy, make new instances of static members in class not to share the members
        attr_map = dict()
        for k in dir(cls):
            v = getattr(cls, k)
            if isinstance(v, CoverPoint):
                new_cp = deepcopy(v)
                setattr(obj, k, new_cp)
                attr_map[id(v)] = new_cp
            elif isinstance(v, Iterable):
                iterable = [e for e in v if isinstance(e, CoverPoint)]
                if iterable:
                    new_iterable = type(v)(deepcopy(iterable))
                    setattr(obj, k, new_iterable)
                    for cp, new_cp in zip(iterable, new_iterable):
                        attr_map[id(cp)] = new_cp

        def update_ref(cp: CoverPoint):
            if cp.ref:
                cp.ref = attr_map[id(cp.ref)]

        for k, v in vars(obj).items():
            if isinstance(v, CoverPoint):
                update_ref(v)
            elif isinstance(v, Iterable):
                for elem in v:
                    if isinstance(elem, CoverPoint):
                        update_ref(cp)

        def new_cross(cross: Cross):
            coverpoints = [attr_map[id(cp)] for cp in cross.coverpoints]
            return Cross(coverpoints, cross.name, cross.group)

        for k in dir(cls):
            v = getattr(cls, k)
            if isinstance(v, Cross):
                setattr(obj, k, new_cross(v))
            elif isinstance(v, Iterable):
                iterable = [e for e in v if isinstance(e, Cross)]
                if iterable:
                    new_iterable = type(v)(map(new_cross, iterable))
                    setattr(obj, k, new_iterable)

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
        self._lock = Lock()

    def __str__(self):
        res = f"CoverGroup(name={self.name}"
        for _, i, _ in chain(self._traverse_coverpoint(), self._traverse_cross()):
            res += f", {i.name}={str(i)}"
        return res

    def _check_attrs(self):
        return tuple(sorted((i for _, i, _ in chain(self._traverse_coverpoint(), self._traverse_cross())), key=hash))

    def __eq__(self, other):
        if not isinstance(other, CoverGroup):
            return False
        return self._check_attrs() == other._check_attrs()

    def __hash__(self):
        return hash(self._check_attrs())

    def _traverse_coverpoint(self, flatten=True):
        for var in dir(self):
            obj = getattr(self, var)
            if isinstance(obj, CoverPoint):
                yield var, obj, None
            elif isinstance(obj, Iterable):
                if flatten:
                    for i, elem in enumerate(obj):
                        if isinstance(elem, CoverPoint):
                            yield var, elem, i
                else:
                    cp_list = [(i, cp) for i, cp in enumerate(obj) if isinstance(cp, CoverPoint)]
                    if cp_list:
                        yield var, cp_list, None

    def _traverse_cross(self):
        for var in dir(self):
            obj = getattr(self, var)
            if isinstance(obj, Cross):
                yield var, obj, None
            elif isinstance(obj, Iterable):
                for i, elem in enumerate(obj):
                    if isinstance(elem, Cross):
                        yield var, elem, i

    def set_name(self, name: str | None, seperator: str = "_"):
        if name is None:
            return
        self.name = name

        for var, obj, i in chain(self._traverse_coverpoint(), self._traverse_cross()):
            obj_name = var if i is None else var + seperator + str(i)
            obj.set_name(obj_name, self.name)

    def connect(self, coverage_instance):
        if not hasattr(coverage_instance, self.sample_name):
            self.log.error(f"No sample signal {self.sample_name} in CoverGroup {self.name}")
            assert False
        self._sample_handler = getattr(coverage_instance, self.sample_name)
        for _, cp, _ in self._traverse_coverpoint():
            cp.connect(coverage_instance)

    def set(self, values: Dict = dict(), **kwargs):
        cp_map = {k: v for k, v, _ in self._traverse_coverpoint(flatten=False)}

        values.update(kwargs)
        for k, v in values.items():
            if k not in cp_map:
                self.log.error(f"CoverPoint {k} is not found in CoverGroup ({self.name}).")
                self.log.error(f"- input values = {values}")
                assert False

            cp = cp_map.get(k)
            if isinstance(cp, Iterable):
                assert isinstance(v, Iterable), f"Value ({v}) should be Iterable for CoverPoint {k}"
                assert len(cp) == len(v), f"Length of values ({len(v)}) is not same to CoverPoint {k} ({len(cp)})"
                for cpi, vi in zip(cp, v):
                    cpi.value = vi
            else:
                assert not isinstance(v, Iterable)
                cp.value = v

    def get(self) -> Dict:
        values = dict()
        for k, v, _ in self._traverse_coverpoint(flatten=False):
            if isinstance(v, Iterable):
                values[k] = [i.value for i in v]
            else:
                values[k] = v.value
        return values

    def __call__(self, **kwargs):
        self.set(values=dict(), **kwargs)

    async def _sample_thread(self, values):
        await self._lock.acquire()
        backup_values = self.get()

        self.set(values)
        self._sample_handler.value = not self._sample_handler.value
        await Edge(self._sample_handler)

        self.set(backup_values)
        self._lock.release()

    def sample(self):
        cocotb.start_soon(self._sample_thread(self.get()))

    @property
    def sample_name(self):
        return str(self.name) + "_sample"

    @property
    def instance_name(self):
        return str(self.name) + "_inst"

    # methods for generating systemverilog
    def sv_wire(self):
        coverpoint_wire = [cp.sv_wire() for _, cp, _ in self._traverse_coverpoint() if cp.ref is None]
        coverpoint_wire = [i for i in coverpoint_wire if i is not None]
        sample_wire = [f"wire {self.sample_name};"]
        return "\n".join(coverpoint_wire + sample_wire)

    def sv_declare(self) -> str:
        covergroup_start = [f"covergroup {self.name};"]
        coverpoint_declare = [cp.sv_declare() for _, cp, _, in self._traverse_coverpoint()]
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

    def markdown(self, name=None, seperator="_"):
        if name is None:
            name = self.name

        output = f"### Covergroup {name}"
        output += "\n\n"

        coverpoint_list = []
        for var, cp, _ in self._traverse_coverpoint(flatten=False):
            if isinstance(cp, Iterable):
                while cp:
                    _, curr_cp = cp[0]
                    index_list = [i for i, cpi in cp if curr_cp == cpi]
                    cp = [(i, cpi) for i, cpi in cp if curr_cp != cpi]
                    suffix = compact_index(index_list)
                    coverpoint_list.append(curr_cp.markdown(var + seperator + suffix))
            else:
                coverpoint_list.append(cp.markdown())

        coverpoint_df = pd.DataFrame.from_records(coverpoint_list)
        output += coverpoint_df.to_markdown(index=False, tablefmt="github")
        output += "\n\n"

        cross_list = [cx.markdown() for _, cx, _ in self._traverse_cross()]
        if cross_list:
            cross_df = pd.DataFrame.from_records(cross_list)
            output += cross_df.to_markdown(index=False, tablefmt="github")
            output += "\n\n"

        return output


class CoverageModel:
    def __init__(self, name: str | None = None, log_level: str = "INFO"):
        """
        name:           name of coverage model
        log_level:      log level in cocotb simulation log
        """
        self.set_name(name)

        self.log = SimLog(f"cocotbext.fcov.{self.__class__.__name__}")
        self.log.setLevel(log_level)

    def __str__(self):
        res = f"CoverageModel(name={self.name}"
        for _, i, _ in self._traverse_covergroup():
            res += f", {i.name}={str(i)}"
        return res

    def _check_attrs(self):
        return tuple(sorted((i for _, i, _ in self._traverse_covergroup()), key=hash))

    def __eq__(self, other):
        if not isinstance(other, CoverageModel):
            return False
        return self._check_attrs() == other._check_attrs()

    def __hash__(self):
        return hash(self._check_attrs())

    def _traverse_covergroup(self, flatten=True):
        for var in dir(self):
            obj = getattr(self, var)
            if isinstance(obj, CoverGroup):
                yield var, obj, None
            elif isinstance(obj, Iterable):
                if flatten:
                    for i, elem in enumerate(obj):
                        if isinstance(elem, CoverGroup):
                            yield var, elem, i
                else:
                    cg_list = [(i, cg) for i, cg in enumerate(obj) if isinstance(cg, CoverGroup)]
                    if cg_list:
                        yield var, cg_list, None

    def set_name(self, name=None, seperator="_"):
        if name is not None:
            self.name = name

        for var, obj, i in self._traverse_covergroup():
            obj_name = var if i is None else var + seperator + str(i)
            obj.set_name(obj_name, seperator=seperator)

    def connect(self, dut):
        if hasattr(dut, self.name):
            self.log.info("Coverage enabled for %s", self.name)
            cov_inst = getattr(dut, self.name)
            for _, cg, _ in self._traverse_covergroup():
                cg.connect(cov_inst)
        else:
            self.log.warning("Coverage instance %s does not exist in dut!", self.name)

    def systemverilog(self, name=None):
        if name is None:
            name = self.name
        header = f"module {name} ();\n"
        body = "\n".join([cg.systemverilog() for _, cg, _ in self._traverse_covergroup()])
        footer = "endmodule\n"
        return header + body + footer

    def markdown(self, name=None, seperator="_"):
        if name is None:
            name = self.name

        header = f"## {name} ({self.__class__.__name__})\n\n"
        covergroup_list = []
        for var, cg, _ in self._traverse_covergroup(flatten=False):
            if isinstance(cg, Iterable):
                while cg:
                    _, curr_cg = cg[0]
                    index_list = [i for i, cgi in cg if curr_cg == cgi]
                    cg = [(i, cgi) for i, cgi in cg if curr_cg != cgi]
                    suffix = compact_index(index_list)
                    covergroup_list.append(curr_cg.markdown(var + seperator + suffix))
            else:
                covergroup_list.append(cg.markdown())
        body = "".join(covergroup_list)

        return header + body


class CoverageCollector:
    def __init__(self, dut, cov_model, log_level: str = "INFO") -> None:
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
