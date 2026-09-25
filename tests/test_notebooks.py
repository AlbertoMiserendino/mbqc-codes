"""Execute each notebook and check its existing quantum results."""
import json
from pathlib import Path
import time

import nbformat
from nbclient import NotebookClient
import pytest

ROOT = Path(__file__).resolve().parents[1]

# Explicit paths ensure missing notebooks fail instead of disappearing from collection.
NOTEBOOKS = [
    ROOT / folder / f"{stem}-{language}.ipynb"
    for folder, stem in (
        ("01-mbqc-teleport", "mbqc-teleport"),
        ("02-mbqc-rotation", "mbqc-rotation"),
        ("03-mbqc-cnot", "mbqc-cnot"),
    )
    for language in ("en", "it")
]


# These cells are injected only into the executed copy, not the source notebook.
SEED_CELL = """from qiskit_aer import AerSimulator
_original_init = AerSimulator.__init__
def _seeded_init(self, *args, **kwargs):
    kwargs.setdefault("seed_simulator", 2026)
    kwargs.setdefault("max_parallel_threads", 2)
    _original_init(self, *args, **kwargs)
AerSimulator.__init__ = _seeded_init
"""

# 0.97 is a regression threshold for the example inputs, not a physical law.
# A small margin above 1 accommodates numerical rounding.
FIDELITY_CHECK = """import json
assert np.isfinite(fidelity) and 0.97 <= fidelity <= 1.000001, fidelity
"""

# Validate all 15 nontrivial two-qubit Pauli coefficients and a physical state:
# unit trace, nonnegative eigenvalues (within rounding) and small trace distance.
CNOT_CHECK = """errors = [error for _, _, _, error in rows]
assert len(errors) == 15
assert np.allclose(np.trace(rho_measured), 1)
assert np.linalg.eigvalsh(rho_measured).min() >= -1e-10
assert trace_distance < 0.05, trace_distance
"""

# Single-qubit examples compare their three Bloch components against theory.
SINGLE_QUBIT_CHECK = """errors = np.abs(np.array([x_meas, y_meas, z_meas]) - r_theory)
"""

# For +/-1 observables the standard error is at most 1/sqrt(shots).
# Six times that bound provides a tolerance that scales with the sample count.
PAULI_CHECK = """assert max(errors) < 6 / np.sqrt(shots), errors
print(json.dumps({"fidelity": float(fidelity), "max_pauli_error": float(max(errors)), "shots": shots}))
"""


@pytest.mark.parametrize("path", NOTEBOOKS, ids=[p.stem for p in NOTEBOOKS])
def test_notebook(path, notebook_kernel, validation_output, validation_report):
    """Run one notebook in isolation without changing its source file."""
    # Load an in-memory copy; never overwrite the original notebook.
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    # Requirements are installed before testing, so skip package installation.
    notebook.cells = [cell for cell in notebook.cells
                      if 'environment-setup' not in cell.metadata.get('tags', [])]

    # Configure reproducible sampling in this kernel, with bounded CPU usage.
    # Explicit simulator options in a notebook still take precedence.
    notebook.cells.insert(0, nbformat.v4.new_code_cell(SEED_CELL))

    # Reuse fidelity and observables already calculated by the notebook.
    # These assertions run inside its kernel, where those variables exist.
    check = FIDELITY_CHECK
    check += CNOT_CHECK if 'cnot' in path.name else SINGLE_QUBIT_CHECK
    check += PAULI_CHECK
    notebook.cells.append(nbformat.v4.new_code_cell(check))

    # Execute in the notebook directory so relative QASM paths resolve.
    # The fixture supplies a fresh kernel using pytest's Python interpreter.
    client = NotebookClient(notebook, km=notebook_kernel, timeout=300,
                            resources={'metadata': {'path': str(path.parent)}})
    start = time.perf_counter()
    record = {"notebook": str(path.relative_to(ROOT)), "status": "failed"}
    try:
        client.execute()
        # The final cell prints JSON for the report; no source outputs are changed.
        metrics = json.loads(''.join(
            output.get('text', '') for output in notebook.cells[-1].outputs
        ).strip())
        record.update(metrics, status="passed")
    except Exception as error:
        record['error'] = str(error)
        # Let pytest report this failure and continue with the other cases.
        raise
    finally:
        # Preserve partial execution on failure. The fixture always closes the kernel.
        record['seconds'] = round(time.perf_counter() - start, 2)
        validation_report.append(record)
        nbformat.write(notebook, validation_output / path.name)
