import os
import sys
import importlib.util
from argparse import ArgumentParser
from distutils.spawn import find_executable

from cocotbext.fcov import CoverageModel
from cocotbext.fcov import traverse_type, get_markdown_list


def traverse_coverage_models(cov_file, flatten=True):
    if os.path.isfile(cov_file):
        sys.path.append(os.path.dirname(cov_file))
        module_name = os.path.splitext(os.path.basename(cov_file))[0]
        coverage_spec = importlib.util.spec_from_file_location(module_name, cov_file)
        coverage_module = importlib.util.module_from_spec(coverage_spec)
        coverage_spec.loader.exec_module(coverage_module)

        yield from traverse_type(coverage_module, CoverageModel, flatten)


def main(append=False):
    parser = ArgumentParser()
    parser.add_argument(
        "--file", "-f", default="coverage.py", type=str, help="python files that include coverage model instances"
    )
    parser.add_argument(
        "--sv_output", "-sv", default="coverage.sv", type=str, help="output file name for systemverilog code"
    )
    parser.add_argument(
        "--md_output", "-md", default="coverage.md", type=str, help="output file name for markdown document"
    )
    parser.add_argument(
        "--overwrite", "-w", default=False, action="store_true", help="force overwrite output files if they exist"
    )
    args = parser.parse_args()

    filelist = args.file.split(",")
    if os.path.isfile(args.sv_output) and not args.overwrite:
        raise FileExistsError(f"{args.sv_output} already exists")

    sv_body = []
    md_body = []
    for f in filelist:
        for k, v, i in traverse_coverage_models(f):
            name = k if i is None else f"{k}_{i}"
            v.set_name(name)
            sv_body.append(v.systemverilog())

        for k, v in traverse_coverage_models(f, flatten=False):
            md_body += get_markdown_list(k, v)

    open_mode = "a" if append else "w"
    with open(args.sv_output, open_mode) as f:
        sv_header = f"`ifdef COCOTBEXT_FCOV\n"
        sv_footer = "`endif\n"
        f.write(sv_header)
        f.write("\n".join(sv_body))
        f.write(sv_footer)

    with open(args.md_output, open_mode) as f:
        f.write("".join(md_body))

    formatter = "verible-verilog-format"
    if find_executable(formatter):
        os.system(f"{formatter} --inplace " + args.sv_output)


if __name__ == "__main__":
    main()
