"""Shared pytest configuration, artifacts and kernel lifecycle."""
import json
from pathlib import Path
import sys

from jupyter_client import KernelManager
import pytest

ROOT = Path(__file__).resolve().parents[1]


def pytest_addoption(parser):
    parser.addoption(
        '--output-dir', default=str(ROOT / 'build' / 'validation'),
        help='Directory for executed notebook copies and results.json.',
    )


@pytest.fixture(scope='session')
def validation_output(pytestconfig):
    """Create the artifact directory once per test session."""
    destination = Path(pytestconfig.getoption('--output-dir')).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    return destination


@pytest.fixture(scope='session')
def validation_report(validation_output):
    """Save metrics for this run, including completed failures and selected tests."""
    report = []
    # Reset the report so a previous successful run cannot look like this run.
    target = validation_output / 'results.json'
    target.write_text('[]\n')
    yield report
    target.write_text(json.dumps(report, indent=2) + '\n')


@pytest.fixture
def notebook_kernel():
    """Give each test a fresh kernel and always shut it down afterwards."""
    manager = KernelManager(kernel_name='python3')
    # Use pytest's interpreter, not the notebook's saved kernel selection.
    manager.kernel_spec.argv = [
        sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}',
    ]
    try:
        yield manager
    finally:
        if manager.has_kernel:
            manager.shutdown_kernel(now=True)
