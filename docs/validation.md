# Validate the notebooks

Complete the [setup](../README.md#setup), then run from the repository root:

```bash
source .venv/bin/activate
python -m pip check
python -m pytest -c tests/pytest.ini
```

The parametrized test in [tests/test_notebooks.py](../tests/test_notebooks.py) executes the six teaching notebooks, one pytest case per notebook, in fresh kernels using the current Python interpreter. Dependency-installation cells tagged `environment-setup` are skipped because requirements must already be installed. All remaining cells, including plots, execute; browser interaction with widgets is not tested.

For validation only, the simulator seed is fixed to `2026` and Aer uses at most two parallel threads. The notebooks retain their normal sampling behavior when opened interactively.

The checks compare simulated Pauli observables with the independent gate-model references already calculated in the notebooks. Each error must be below `6 / sqrt(shots)`, six times the worst-case standard error of a ±1 observable. Fidelity must be at least 0.97. CNOT also checks all 15 nontrivial Pauli coefficients, density-matrix normalization and positivity and trace distance below 0.05. These are regression checks for the example inputs, not a proof for all possible input states.

Executed copies and `results.json` (fidelity, maximum Pauli error, shots, elapsed time and pass/fail status) are written to `build/validation/`, which is ignored by Git. Source notebooks are not overwritten. On execution or numerical-check failure, the executed notebook is retained for diagnosis and pytest continues with the other cases. The report includes only cases executed in the current run; older notebook copies in the output directory are not removed. Errors while loading or validating the notebook format are reported by pytest before execution.

The [GitHub Actions workflow](../.github/workflows/notebooks.yml) installs the pinned requirements on Python 3.14.4, checks dependency consistency, runs this command on pushes and pull requests and uploads the executed notebooks, metrics and JUnit XML report as artifacts. It does not require Pandoc or LaTeX.

## Select tests and inspect results

```bash
# Run only the two CNOT notebooks.
python -m pytest -c tests/pytest.ini -k cnot

# List the six cases without executing notebooks.
python -m pytest -c tests/pytest.ini --collect-only

# Choose another artifact directory and produce a CI-compatible report.
python -m pytest -c tests/pytest.ini --output-dir build/checks --junitxml=build/checks/junit.xml
```

Pytest reports each notebook separately and returns a nonzero exit code if any test fails. Add `-x` to stop at the first failure. The shared fixtures in [tests/conftest.py](../tests/conftest.py) manage kernel cleanup and the metrics report. Numerical assertions still run inside each notebook kernel, using the fidelity and observables already computed by its cells; failures include the failing cell and its traceback.

In VS Code, select the environment with `requirements-dev.txt` installed, then use **Python: Configure Tests**, select **pytest** and the `tests` directory. The Testing view lets you run individual notebook cases. The previous `scripts/check_notebooks.py` entry point has been replaced by pytest.

## Run tests with VS Code tasks

Choose **Terminal → Run Task** and select the test task in [.vscode/tasks.json](../.vscode/tasks.json):

- **Tests: Run all notebooks** runs all six notebook tests.

This task runs from the repository root using `${workspaceFolder}/.venv/bin/python`. Install `requirements-dev.txt` in that environment first. The interpreter selected in VS Code does not override this explicit path. Results appear in the task terminal, with executed notebooks and metrics saved in `build/validation/`.

## Shot counts and statistical precision

`shots` is the number of circuit repetitions **per measurement setting**, not the total for the notebook. CNOT uses **20,000**, not 2,000, shots per setting.

| Example | Measured quantities | Settings | Shots per setting | Total shots per notebook |
| --- | --- | --- | --- | --- |
| Teleportation | 3 single-qubit Bloch components | X, Y, Z (3) | 10,000 | 30,000 |
| Rotation | 3 single-qubit Bloch components | X, Y, Z (3) | 10,000 | 30,000 |
| CNOT | 15 nontrivial two-qubit Pauli coefficients | All pairs in {X, Y, Z} × {X, Y, Z} (9) | 20,000 | 180,000 |

Each CNOT setting provides a two-qubit correlation and local single-qubit expectations. The notebook averages local estimates across compatible settings, so 15 separate settings are not needed.

The larger CNOT budget is a precision choice for reconstructing the two-qubit density matrix, not a requirement of the CNOT gate or MBQC. Finite-shot noise can produce negative eigenvalues in the linear reconstruction; more shots reduce that noise, but do not guarantee a positive matrix. The notebook projects the estimate onto a physical density matrix before computing fidelity.

For a Pauli observable with outcomes ±1 and expectation `mu`, the standard error from `N` independent shots is `sqrt((1 - mu**2) / N)`, at most `1 / sqrt(N)`. Doubling the shots from 10,000 to 20,000 therefore reduces the standard error by a factor of `sqrt(2)` (about 29%), from at most 0.0100 to 0.0071 for an individual setting. It does not halve the error.

Using 10,000 shots per CNOT setting is also possible: it reduces the total to 90,000 at the cost of noisier estimates. Change `shots` in the simulation cell and rerun the subsequent cells. The Pauli-error checks scale with `shots`; the fixed fidelity and trace-distance thresholds may become harder to meet at much smaller sample counts. The reference results below use the original defaults.

## Local reference run

Measured on Python 3.14.4 with the pinned packages, simulator seed 2026 and at most two Aer threads. These times include kernel startup and plotting; they are indicative, not performance guarantees.

| Example | time | Fidelity | Maximum Pauli error |
| --- | --- | --- | --- |
| Teleportation | 2.7 seconds | 0.994975 | 0.007107 |
| Rotation | 4.7 seconds | 0.999997 | 0.011242 |
| CNOT | 6.0 seconds | 0.995686 | 0.010100 |

