from __future__ import annotations

from functools import cached_property
from enum import Enum, IntEnum


class LanguageType(IntEnum):
    Default = 0
    SystemVerilog = 1


# TODO: sort
# TODO: auto contraction to range
# TODO: handle overlap value
class BinItem:
    def __init__(
        self,
        items=None,
        width: int | None = None,
        next: BinItem | None = None,
        name: str | None = None,
        num: int = 1,
        prefix: str = "bin",
        format: str | None = "d",
    ):
        self._width = width
        self.name = name
        self._num = num
        self.prefix = prefix
        self.format = "d" if format is None else format

        self.items = items
        self.next = next

    def __copy__(self):
        return self.__class__(
            items=self.items,
            width=self._width,
            next=self.next,
            name=self._name,
            num=self._num,
            prefix=self.prefix,
            format=self.format,
        )

    def __deepcopy__(self, memo):
        return self.__copy__()

    def copy(self):
        return self.__copy__()

    def _is_type_int(self, item):
        return isinstance(item, int)

    def _is_type_range(self, item):
        return isinstance(item, range) and item.step == 1

    def _is_type_range_with_step(self, item):
        return isinstance(item, range) and item.step > 1

    def _is_type_transition(self, item):
        return isinstance(item, BinItem) and item.next is not None

    def _is_type_wildcard(self, item):
        raise NotImplementedError

    def _is_transition_bin(self):
        return all(map(self._is_type_transition, self.items))

    def _is_range_bin(self):
        return not any(map(self._is_type_transition, self.items))

    def _as_bin_item(self, value) -> BinItem:
        if isinstance(value, BinItem):
            return value.copy()
        else:
            return BinItem(
                items=value,
                width=self._width,
                next=self.next,
                name=self._name,
                num=self._num,
                prefix=self.prefix,
                format=self.format,
            )

    def _update_items(self, items, depth=0):
        if items is None:
            return []

        def is_item_single(item):
            if self._is_type_range_with_step(item):
                return depth == 0
            return self._is_type_int(item) or self._is_type_range(item) or self._is_type_transition(item)

        if is_item_single(items):
            items = [items]
        items = list(items)

        if len(items) == 1 and is_item_single(items[0]):
            if isinstance(items[0], range) and len(items[0]) <= 1:
                return list(items[0])
            return items

        updated_items = []
        while items:
            i = items.pop(0)
            if isinstance(i, str) and (i.strip() == "=>" or i.strip() == ">>"):
                return [
                    BinItem(
                        items=updated_items,
                        width=self._width,
                        next=items,
                        format=self.format,
                    )
                ]
            updated_items += self._update_items(i, depth=depth + 1)

        return updated_items

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, value):
        self._items = self._update_items(value)
        assert (
            self._is_transition_bin() or self._is_range_bin()
        ), f"Error!! All bin items ({self._items}) should be same! (value only or transition only)"

    @cached_property
    def max(self):
        if not self.items:
            return None

        def max_item_single(item):
            if isinstance(item, Enum):
                return max_item_single(item.value)
            elif isinstance(item, BinItem):
                return item.max
            elif isinstance(item, range):
                return item.stop - 1
            else:
                return item

        values = [max_item_single(i) for i in self.items]
        if self.next is not None:
            values.append(self.next.max)
        return max(values)

    @cached_property
    def min(self):
        if not self.items:
            return None

        def min_item_single(item):
            if isinstance(item, Enum):
                return min_item_single(item.value)
            elif isinstance(item, BinItem):
                return item.min
            elif isinstance(item, range):
                return item.start
            else:
                return item

        values = [min_item_single(i) for i in self.items]
        if self.next is not None:
            values.append(self.next.min)
        return min(values)

    @property
    def width(self):
        if self._width is not None:
            return self._width

        # assert not self.items, "Error!! Need specified width value or at least one item in BinItem"
        if not self.items:
            return None

        def get_width(value: int):
            if value < -1:
                value += 1
            return value.bit_length() + (value < 0)

        return max(1, *map(get_width, [self.min, self.max]))

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def next(self) -> BinItem | None:
        if not hasattr(self, "_next"):
            self._next = None
        return self._next

    @next.setter
    def next(self, value):
        if value is None:
            self._next = None
            return

        value = self._as_bin_item(value)
        if value._is_transition_bin():
            assert len(value.items) == 1, "Error!! only single transition is allowed as next of previous transiton."
            self._next = value.items[0]
        else:
            self._next = value

    @property
    def name(self):
        if self._name is None:
            return self.suggest_name()
        else:
            return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def num(self):
        if self._num == 0:
            return self.__len__()
        else:
            return self._num

    @num.setter
    def num(self, value):
        self._num = value

    def is_default(self):
        return not self.items

    def __repr__(self):
        return (
            f"BinItem(items=({self.__str__()}), width={self._width}, next={self.next},"
            f" name={self._name}, num={self.num}, prefix={self.prefix},"
            f" format={self.format})"
        )

    def __str__(self):
        return self.as_string()

    def _check_attrs(self):
        return *sorted(self.items, key=hash), self.next, self.num, self.width

    def __eq__(self, other):
        if not isinstance(other, BinItem):
            try:
                other = self._as_bin_item(other)
            except:
                return False
        return self._check_attrs() == other._check_attrs()

    def __hash__(self):
        return hash(self._check_attrs())

    def __add__(self, value):
        rhs = self._as_bin_item(value)
        if rhs.next is not None:
            raise (
                TypeError,
                "unsupported operand type(s) for +: 'BinItem(transition)' is not allowed at right-hand side",
            )
        return self._as_bin_item(self.items + rhs.items)

    def __radd__(self, value):
        lhs = self._as_bin_item(value)
        if self.next is not None:
            raise (
                TypeError,
                "unsupported operand type(s) for +: 'BinItem(transition)' is not allowed at right-hand side",
            )
        return self._as_bin_item(lhs.items + self.items)

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        def len_item_single(item):
            if isinstance(item, Enum):
                return len_item_single(item.value)
            elif self._is_type_int(item):
                return 1
            else:
                return len(item)

        len_value = sum(len_item_single(i) for i in self.items)
        return len_value if self.next is None else len_value * len(self.next)

    def __getitem__(self, key):
        return self.items[key]

    # Transition operators: >>, <<
    def __rshift__(self, value):
        res = self.copy()
        res_next = res
        while res_next._next is not None:
            res_next = res_next._next
        res_next.next = value
        return res

    def __lshift__(self, value):
        rhs = self._as_bin_item(value)
        rhs_next = rhs
        while rhs_next._next is not None:
            rhs_next = rhs_next._next
        rhs_next.next = self
        return rhs

    def suggest_name(self, prefix: str | None = None, seperator="_", format: str | None = None):
        if prefix is None:
            prefix = self.prefix

        if len(self.items) == 0:
            return "others"
        elif len(self.items) == 1 and isinstance(self.items[0], Enum):
            return self.items[0].name

        range_list = sorted(list({self.min, self.max} - {None}))

        name = [prefix]
        name += [i.replace("-", "neg") for i in map(lambda x: self._format_int(x, format_int=format), range_list)]
        return seperator.join(name)

    def add(self, items):
        self.items += items

    def append(self, item):
        self.items += item

    def _format_int(
        self,
        value,
        lang: LanguageType = LanguageType.Default,
        format_int: str | None = None,
    ) -> str:
        if format_int is None:
            format_int = self.format

        format_bin = ["bin", "b"]
        format_oct = ["oct", "o"]
        format_dec = ["dec", "d"]
        format_hex = ["hex", "h", "x"]

        assert isinstance(value, int)
        assert (
            format_int in format_bin + format_oct + format_dec + format_hex
        ), f"Error!! Format type ({format_int}) is not allowed!"
        if format_int in format_bin:
            format_int = "b"
        elif format_int in format_oct:
            format_int = "o"
        elif format_int in format_hex:
            format_int = "x"
        else:  # format_int in format_dec
            format_int = "d"

        abs_value = format(abs(value), format_int)
        sign_prefix = "-" if value < 0 else ""
        format_prefix = ""
        if lang == LanguageType.SystemVerilog:
            if self.width > 32:
                format_prefix = (str(self.width) + "'" + format_int).replace("x", "h")
            elif format_int != "d":
                format_prefix = ("'" + format_int).replace("x", "h")
        elif format_int != "d":
            format_prefix = "0" + format_int

        return sign_prefix + format_prefix + abs_value

    def _str_item_single(self, item, lang: LanguageType = LanguageType.Default, format: str | None = None) -> str:
        if isinstance(item, Enum):
            if lang == LanguageType.SystemVerilog:
                return self._str_item_single(item.value, lang, format)
            else:
                return f"{item.name}({self._str_item_single(item.value, lang, format)})"
        elif self._is_type_int(item):
            return self._format_int(item, lang, format)
        elif isinstance(item, range):
            assert self._is_type_range(item) or lang == LanguageType.SystemVerilog
            return f"[{self._format_int(item.start, lang, format)}:{self._format_int(item.stop-1, lang, format)}]"
        elif self._is_type_transition(item):
            return f"({item.as_string(lang, format)})"
        else:
            assert False, f"Error!! Not supported type ({type(item)}) as a single item in BinItem!"

    def as_string(
        self,
        lang: LanguageType = LanguageType.Default,
        format: str | None = None,
        seperator: str = ",",
        shorten=False,
    ):
        if self.is_default():
            return "default"
        if len(self.items) == 1 and self._is_type_range_with_step(self.items[0]) and lang == LanguageType.Default:
            items = list(self.items[0])
        else:
            items = self.items

        str_item_list = [self._str_item_single(i, lang=lang, format=format) for i in items]
        if shorten and len(items) > 6:
            res = f"{seperator} ".join(str_item_list[:3] + ["..."] + str_item_list[-2:])
        else:
            res = f"{seperator} ".join(str_item_list)

        if self.next:
            res += " => " + self.next.as_string(lang=lang, format=format, seperator=seperator)
        return res

    def systemverilog(self, format: str | None = None, keyword: str = "bins"):
        assert keyword in [
            "bins",
            "ignore_bins",
            "illegal_bins",
        ], f"Error!! keyword ({keyword}) should be bins, illegal_bins or ignore_bins"

        sv_items = self.as_string(lang=LanguageType.SystemVerilog, format=format)
        if self._is_type_transition(self):
            sv_items = "(" + sv_items + ")"
        elif len(self.items) > 0 and self._is_range_bin():
            sv_items = "{" + sv_items + "}"

        if len(self.items) == 1 and self._is_type_range_with_step(self.items[0]):
            step = self.items[0].step
            offset = self.min % step
            sv_items += f" with (item % {step} == {offset})"

        if self._num == 0:
            return f"{keyword} {self.name}[] = {sv_items}"
        elif self.num == 1:
            return f"{keyword} {self.name} = {sv_items}"
        else:
            return f"{keyword} {self.name}[{self.num}] = {sv_items}"

    def markdown(self, format: str | None = None, shorten=True, enum=False):
        if len(self.items) == 1 and self._is_type_range_with_step(self.items[0]):
            is_multiple = len(self.items[0]) > 1
        else:
            is_multiple = len(self.items) > 1
        md_items = self.as_string(format=format, shorten=shorten)
        md_items = "{" + md_items + "}" if is_multiple else md_items
        divider = f"/{self.num}" if self.num > 1 else ""
        if enum:
            return self.name + "(" + md_items + divider + ")"
        else:
            return md_items + divider
