import os
import sys
import importlib.util
from typing import Iterable
from argparse import ArgumentParser
from distutils.spawn import find_executable

from cocotbext.fcov import CoverageModel, compact_index


def get_coverage_models(cov_file):
    coverage_models = dict()
    if os.path.isfile(cov_file):
        sys.path.append(os.path.dirname(cov_file))
        module_name = os.path.splitext(os.path.basename(cov_file))[0]
        coverage_spec = importlib.util.spec_from_file_location(module_name, cov_file)
        coverage_module = importlib.util.module_from_spec(coverage_spec)
        coverage_spec.loader.exec_module(coverage_module)

        for attr, value in coverage_module.__dict__.items():
            if isinstance(value, CoverageModel):
                coverage_models[attr] = value
            elif isinstance(value, Iterable):
                model_list = [(i, m) for i, m in enumerate(value) if isinstance(m, CoverageModel)]
                if model_list:
                    coverage_models[attr] = model_list
    return coverage_models


def main():
    parser = ArgumentParser()
    parser.add_argument("--file", "-f", default="coverage.py", type=str)
    parser.add_argument("--sv_output", "-sv", default="coverage.sv", type=str)
    parser.add_argument("--md_output", "-md", default="coverage.md", type=str)
    parser.add_argument("--overwrite", "-w", default=False, action="store_true")
    args = parser.parse_args()

    filelist = args.file.split(",")
    if os.path.isfile(args.sv_output) and not args.overwrite:
        raise FileExistsError(f"{args.sv_output} already exists")

    sv_body = []
    md_body = []
    for f in filelist:
        cov_models = get_coverage_models(f)
        for name, model in cov_models.items():
            if isinstance(model, Iterable):
                for i, m in model:
                    m.set_name(f"{name}_{i}")
                    sv_body.append(m.systemverilog())

                while model:
                    _, cov_model = model[0]
                    index_list = [i for i, m in model if cov_model == m]
                    model = [(i, m) for i, m in model if cov_model != m]
                    md_suffix = compact_index(index_list)
                    md_body.append(m[0].markdown(f"{name}_{md_suffix}"))
            else:
                model.set_name(name)
                sv_body.append(model.systemverilog())
                md_body.append(model.markdown())

    with open(args.sv_output, "w") as f:
        sv_header = f"`ifdef COCOTBEXT_FCOV\n"
        sv_footer = "`endif\n"
        f.write(sv_header)
        f.write("\n".join(sv_body))
        f.write(sv_footer)

    with open(args.md_output, "w") as f:
        f.write("".join(md_body))

    formatter = "verible-verilog-format"
    if find_executable(formatter):
        os.system(f"{formatter} --inplace " + args.sv_output)


if __name__ == "__main__":
    main()
