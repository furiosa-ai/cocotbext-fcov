# cocotbext-fcov

Cocotb Extension for Functional Coverage Closure


## Installation

```
$ git clone https://github.com/furiosa-ai/cocotbext-fcov
$ pip install cocotbext-fcov
```

## Documentation



### CoverPoint

The `CoverPoint` class defines specific ranges to be covered during verification using bins, corresponding to the `coverpoint` in SystemVerilog.

`CoverPoint` requires a collection of bins, and the following types are supported as bins:

#### integer
``` python
CoverPoint([1, 5])
# bins bin_1 = {1};
# bins bin_5 = {5};

```

#### range
``` python
CoverPoint([range(10), range(10, 20)])
# bins bin_0_9 = {[0:9]};
# bins bin_10_19 = {[10:19]};
```

#### list (Iterable)
``` python
CoverPoint([[1, 2], (3, 5, 7)])
# bins bin_1_2 = {1, 2};
# bins bin_3_7 = {3, 5, 7};
CoverPoint([[1, 2], (3, 5, 7)])
# bins bin_1_2 = {1, 2};
# bins bin_3_7 = {3, 5, 7};
```

#### transition
``` python
CoverPoint([[1, "=>",  2], [range(10, 20), "=>", range(20, 30)]])
# bins bin_1_2 = {1 => 2};
# bins bin_10_29 = {[10:19] => [20:29]};
```

### Predefined Bin Types

For convenience, some predefined bin types are provided:

#### BinSingle
``` python
CoverPoint(BinSingle(1))
# bins bin_1 = {1};
CoverPoint(BinSingle(range(10)))
# bins bin_0_9 = {[0:9]};
```

#### BinUniform
Use like python `range()`
``` python
CoverPoint(BinUniform(10))
# bins bin_0_9[] = {[0:9]};
CoverPoint(BinUniform(10, 20), num=5)
# bins bin_10_19[5] = {[10:19]};
```

#### BinRange
Same as `BinUniform`, but not support `num` argument
``` python
CoverPoint(BinRange(10))
# bins bin_0_9[] = {[0:9]};
CoverPoint(BinRange(10, 20))
# bins bin_10_19[] = {[10:19]};
```

#### BinDict
``` python
CoverPoint(BinDict({"FALSE": 0, "TRUE": 1}), format="b")
# bins FALSE = {'b0};
# bins TRUE = {'b1};
```

#### BinEnum
``` python
class Bool(Enum):
    FALSE = 0
    TRUE = 1
CoverPoint(BinEnum(Bool), format="b")
# bins FALSE = {'b0};
# bins TRUE = {'b1};
```

#### BinBool
``` python
CoverPoint(BinBool())
# bins FALSE = {'b0};
# bins TRUE = {'b1};
```

#### BinExp
Use like python `range()`
``` python
CoverPoint(BinExp(100, base=10))
# bins bin_0 = {0}
# bins bin_1_9 = {[1:9]}
# bins bin_10_99 = {[10:99]}
```

#### BinMinMax, BinMinMaxUniform
``` python
CoverPoint(BinMinMax(min=100, max=200, num=5))
# bins bin_100 = {100};
# bins bin_101_199[3] = {[101:199]};
# bins bin_200 = {200};
```

#### BinMinMaxExp
``` python
CoverPoint(BinMinMaxExp(min=100, max=200, base=2, num=5))
# bins bin_100 = {100};
# bins bin_101_127 = {[101:127]};
# bins bin_128_199 = {[128:199]};
# bins bin_200 = {200};
```

#### BinWindow
``` python
CoverPoint(BinWindow(0x6, width=6, shift=2))
# bins bin_0x6 = {'h6};
# bins bin_0x18 = {'h18};
# bins bin_0x20 = {'h20};
```

#### BinOneHot
``` python
CoverPoint(BinOneHot(width=3, format="b"))
# bins bin_0b1 = {'b1};
# bins bin_0b10 = {'b10};
# bins bin_0b100 = {'b100};
```

#### BinDefault
``` python
CoverPoint(BinDefault())
# bins others = default;
```

#### BinBitwise
``` python
CoverPoint(BinBitwise(3), name="cp_bitwise", group="cg_predefined")
# cp_bitwise_0: coverpoint cg_predefined_cp_bitwise[0];
# cp_bitwise_1: coverpoint cg_predefined_cp_bitwise[1];
# cp_bitwise_2: coverpoint cg_predefined_cp_bitwise[2];
```

#### BinTransition
``` python
CoverPoint(BinTransition([1, 2, 3], (4, 5, 6), [[7, 8, 9], range(10, 20)]))
# bins bin_1_3 = (1 => 2 => 3);
# bins bin_4_6 = (4 => 5 => 6);
# bins bin_7_19 = (7, 8, 9 => [10:19]);
```


### Cross

The `Cross` class supports the examination of various combinations of values of coverpoints, corresponding to the `cross` in SystemVerilog.

``` python
Cross([cp1, cp2], name="cx")
# cx: cross cp1, cp2;
```

### CoverGroup

The `CoverGroup` class is a container that groups together multiple coverpoints and samples covered values, corresponding to the `covergroup` in SystemVerilog.

``` python
class CustomCoverGroup(CoverGroup):
    cp_bool = CoverPoint(BinBool())
    cp_range = CoverPoint(BinRange(10))
    cx_bool_range = Cross([cp_bool, cp_range])
cg_custom = CustomCoverGroup(name="cg_custom")
# covergroup cg_custom;
#   cp_bool: coverpoint cg_custom_cp_bool {
#     bins FALSE = {0};
#     bins TRUE = {1};
#   }
#   cp_range: coverpoint cg_custom_cp_range {
#     bins bin_0_9 = {[0:9]};
#   }
#   cx_bool_range: cross cp_bool, cp_range;
```
### CoverageModel

A `CoverageModel` is a collection of specifications used to measure the coverage of a design during simulation, typically represented by a set of CoverGroups and coverted to a single module in SystemVerilog.

``` python
class CustomCovModel(CoverageModel):
    cg_custom_1 = CustomCoverGroup1()
    cg_custom_2 = CustomCoverGroup2()
cov_model = CustomCovModel()
# module cov_model();
#   wire ...
#   covergroup cg_custom_1 ...
#   wire ...
#   covergroup cg_custom_2 ...
# endmodule
```

#### make_coverage

A tool that generates SystemVerilog code and Markdown documentation from Python code, including model instances.

Usage:
```
make_coverage [-h] [--file FILE] [--sv_output SV_OUTPUT] [--md_output MD_OUTPUT] [--overwrite]
```

Optional arguments:
```
  -h, --help            show this help message and exit
  --file FILE, -f FILE  python files that include coverage model instances
  --sv_output SV_OUTPUT, -sv SV_OUTPUT
                        output file name for systemverilog code
  --md_output MD_OUTPUT, -md MD_OUTPUT
                        output file name for markdown document
  --overwrite, -w       force overwrite output files if they exist
```

### CoverageCollector

A base class designed to gather and sample coverage values using coverage models.
