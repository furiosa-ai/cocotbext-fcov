"""Pytest collection for tests/cocotb/* pilots.

Each pilot subdirectory (excluding leading-underscore dirs like _lib/) with a
Makefile becomes one pytest case. The case runs `make sim` (default SIM=verilator)
and asserts a clean cocotb pass.

Opt-in via marker -- ``pytest -m cocotb_sim tests/cocotb`` -- so the default
``pytest`` invocation against ``tests/pytest/`` stays fast.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


COCOTB_DIR = Path(__file__).parent
_LIB_DIR_NAMES = {"_lib"}


def _discover_pilots() -> list[Path]:
    """Yield pilot directories: top-level subdirs of tests/cocotb/ with a Makefile,
    skipping `_lib`-style helper dirs."""
    pilots: list[Path] = []
    for child in sorted(COCOTB_DIR.iterdir()):
        if not child.is_dir():
            continue
        if child.name in _LIB_DIR_NAMES:
            continue
        if (child / "Makefile").is_file():
            pilots.append(child)
    return pilots


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "cocotb_sim: cocotb pilot (Verilator/VCS/Questa). Opt-in, slow.",
    )


@pytest.mark.cocotb_sim
@pytest.mark.parametrize("pilot", _discover_pilots(), ids=lambda p: p.name)
def test_cocotb_pilot_smoke(pilot: Path) -> None:
    """Run `make sim` in each pilot dir and assert clean PASS.

    SIM defaults to verilator (open-source, fastest). Override with
    ``SIM=vcs pytest -m cocotb_sim ...`` to exercise commercial flows.
    """
    sim = os.environ.get("SIM", "verilator")
    env = {**os.environ, "SIM": sim}
    # Match cocotb 2.0 expectations.
    env.setdefault("COCOTB_TEST_MODULES", "tb_smoke")
    result = subprocess.run(
        ["make", "clean", "sim"],
        cwd=pilot,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        pytest.fail(
            f"{pilot.name} (SIM={sim}) returned {result.returncode}\n"
            f"--- stdout (tail) ---\n{result.stdout[-2000:]}\n"
            f"--- stderr (tail) ---\n{result.stderr[-2000:]}"
        )
