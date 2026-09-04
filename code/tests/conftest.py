import pathlib
import pytest
from utils import version_to_path

def pytest_addoption(parser):
    parser.addoption(
        "--arc-version",
        action="store",
        required=True,
        help="ARC version, e.g. v1.4.1",
    )


def pytest_generate_tests(metafunc):
    if "arc_path" in metafunc.fixturenames:
        base = pathlib.Path(version_to_path(metafunc.config.getoption("--arc-version")))
        language_csvs = sorted(base.glob("*/ARCH.csv"))

        if not language_csvs:
            raise FileNotFoundError(f"No language CSVs found under {base}")

        metafunc.parametrize(
            "arc_path",
            language_csvs,
            ids=[p.parent.name for p in language_csvs],  # shows language in test name
        )