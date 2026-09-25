# Measurement-based quantum computing

Jupyter notebooks exploring measurement-based quantum computing (MBQC) with cluster states, OpenQASM 3, Qiskit and local Aer simulations. The examples use [dynamic circuits](#dynamic-circuit-and-classical-feedforward) to implement quantum teleportation, an arbitrary single-qubit rotation and a CNOT gate on cluster states. The rotation example additionally uses [adaptive measurements](#adaptive-measurements), whose bases depend on earlier measurement outcomes.

Browse the exported notebooks on the [MBQC Codes website](https://albertomiserendino.github.io/mbqc-codes/).

## Code

### Notebooks

These notebooks simulate circuits locally with `AerSimulator`; they do not submit jobs to quantum hardware. The later Python calculations of tomography and fidelity analyze the collected results and are separate from the in-circuit feed-forward.

| Example | English | Italian | Description |
| --- | --- | --- | --- |
| Quantum teleportation | [Notebook](01-mbqc-teleport/mbqc-teleport-en.ipynb) · [HTML](01-mbqc-teleport/mbqc-teleport-en.html) · [PDF](01-mbqc-teleport/mbqc-teleport-en.pdf) · [Colab](https://colab.research.google.com/github/AlbertoMiserendino/mbqc-codes/blob/main/01-mbqc-teleport/mbqc-teleport-en.ipynb) · [OpenQASM](01-mbqc-teleport/mbqc-teleport-v1a.qasm) · [OpenQASM (2)](01-mbqc-teleport/mbqc-teleport-v1b.qasm)  | [Notebook](01-mbqc-teleport/mbqc-teleport-it.ipynb) · [HTML](01-mbqc-teleport/mbqc-teleport-it.html) · [PDF](01-mbqc-teleport/mbqc-teleport-it.pdf) · [Colab](https://colab.research.google.com/github/AlbertoMiserendino/mbqc-codes/blob/main/01-mbqc-teleport/mbqc-teleport-it.ipynb) | Transfer an arbitrary input state through a four-qubit linear cluster, then apply Pauli corrections and a final Hadamard. |
| Arbitrary rotation | [Notebook](02-mbqc-rotation/mbqc-rotation-en.ipynb) · [HTML](02-mbqc-rotation/mbqc-rotation-en.html) · [PDF](02-mbqc-rotation/mbqc-rotation-en.pdf) · [Colab](https://colab.research.google.com/github/AlbertoMiserendino/mbqc-codes/blob/main/02-mbqc-rotation/mbqc-rotation-en.ipynb) · [OpenQASM](02-mbqc-rotation/mbqc-rotation.qasm) | [Notebook](02-mbqc-rotation/mbqc-rotation-it.ipynb) · [HTML](02-mbqc-rotation/mbqc-rotation-it.html) · [PDF](02-mbqc-rotation/mbqc-rotation-it.pdf) · [Colab](https://colab.research.google.com/github/AlbertoMiserendino/mbqc-codes/blob/main/02-mbqc-rotation/mbqc-rotation-it.ipynb) | Implement `U_R = Rx(zeta) Rz(eta) Rx(xi)` on a five-qubit linear cluster using [adaptive measurement bases](#adaptive-measurements). |
| CNOT gate | [Notebook](03-mbqc-cnot/mbqc-cnot-en.ipynb) · [HTML](03-mbqc-cnot/mbqc-cnot-en.html) · [PDF](03-mbqc-cnot/mbqc-cnot-en.pdf) · [Colab](https://colab.research.google.com/github/AlbertoMiserendino/mbqc-codes/blob/main/03-mbqc-cnot/mbqc-cnot-en.ipynb) | [Notebook](03-mbqc-cnot/mbqc-cnot-it.ipynb) · [HTML](03-mbqc-cnot/mbqc-cnot-it.html) · [PDF](03-mbqc-cnot/mbqc-cnot-it.pdf) · [Colab](https://colab.research.google.com/github/AlbertoMiserendino/mbqc-codes/blob/main/03-mbqc-cnot/mbqc-cnot-it.ipynb) | Implement a `CNOT` gate on a four-qubit T-shaped cluster. |

The teleportation and rotation examples estimate the output Bloch vector from measurements in the X, Y and Z bases and compare it with a theoretical reference using fidelity. The default is 10,000 shots per basis, so numerical results vary between runs.

The rotation notebook also includes an interactive Bloch sphere comparing the input state, expected output and reconstructed output, implemented by the `BlochComparison` class.

### OpenQASM files

> OpenQASM (Open Quantum Assembly Language) is an imperative programming language designed for near-term quantum computing algorithms and applications. Quantum programs are described using the measurement-based quantum circuit model with support for classical feed-forward flow control based on measurement outcomes [[openqasm.com](https://openqasm.com/)].

- [mbqc-teleport-v1a.qasm](01-mbqc-teleport/mbqc-teleport-v1a.qasm): prepares the ancillary cluster before preparing and coupling the input state.
- [mbqc-teleport-v1b.qasm](01-mbqc-teleport/mbqc-teleport-v1b.qasm): prepares the input state first, then prepares the ancillas and creates the cluster connections. The teleportation notebook displays both variants and uses this second circuit for the subsequent simulation.
- [mbqc-rotation.qasm](02-mbqc-rotation/mbqc-rotation.qasm): prepares the five-qubit cluster, performs [adaptive measurements](#adaptive-measurements) and removes the Pauli byproduct from the output qubit.

## Setup

The reference environment is **Python 3.14.4** (also recorded in `.python-version`). Use this version to reproduce the validated setup. Other Python versions have not been verified.

Create a Python virtual environment from the repository root. On Linux or WSL:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
python -m ipykernel install --user --name mbqc --display-name "Python (MBQC)"
```

- [requirements.txt](requirements.txt) specifies Qiskit, the OpenQASM 3 importer, Aer, `ipynbname` and `ipympl`. 
- [requirements-dev.txt](requirements-dev.txt) pins the Jupyter tools used to run and export notebooks. Simulations run locally and do not require quantum hardware credentials.

## Run an example

### Run online with Google Colab

Use the **Colab** links in the table above to open either language version. Connect to a Python runtime and run the cells in order. The setup cell clones this repository's `main` branch into `/content/mbqc-codes`, selects the example directory and installs `requirements.txt`. If prompted after installation, restart the runtime and run the cells again. The rotation notebooks also enable Colab's custom widget manager for the interactive Bloch sphere, following the [ipympl instructions](https://matplotlib.org/ipympl/installing.html#google-colab).

The clone is reused within a session; start a fresh Colab session to fetch later GitHub changes. Colab links use the published files on `main`, so local edits become available after committing and pushing them. Colab's Python environment may differ from the locally validated version; execution in a hosted Colab runtime has not yet been verified.

### Run locally

Launch JupyterLab from the example directory so that the initial dependency cell can resolve `../requirements.txt`:

```bash
cd 01-mbqc-teleport
python -m jupyterlab
```

To use the Jupyter Notebook interface instead, run `python -m notebook` from the same directory.

For the rotation or CNOT example, use `02-mbqc-rotation` or `03-mbqc-cnot` instead. Open either language version, select **Python (MBQC)** and execute the cells in order. The teleportation and rotation notebooks load QASM files from their own directory; CNOT constructs its circuit in Python.

Alternatively, open a notebook in VS Code with the Python and Jupyter extensions and select the virtual environment as its kernel. If the dependency cell cannot find `../requirements.txt`, install dependencies from the repository root using the setup command above and continue with the directory setup cell.

After installing dependencies for the first time, restart the kernel before running all cells. This is especially important for `ipympl`: an already running kernel may not recognize the `widget` backend until restarted.

### Interactive Bloch sphere

Execute the rotation notebook through its final plotting cell. It uses `%matplotlib widget`: drag the sphere to rotate it and use the toolbar to zoom. A static notebook preview does not provide these controls; open the notebook with a running kernel.

## Expected results and validation

Run the notebook tests with `python -m pytest -c tests/pytest.ini` after installing the development requirements. Test code and configuration live in [`tests/`](tests/).

| Example | Default sampling | Expected result |
| --- | --- | --- |
| Teleportation | 10,000 shots in each of X, Y and Z | Recover the input Bloch vector; for the default angles, approximately `(0.7071, 0.7071, 0)`, with fidelity close to 1. |
| Arbitrary rotation | 10,000 shots in each of X, Y and Z | Match the independent gate-model reference for `Rx(zeta) Rz(eta) Rx(xi)`, with fidelity close to 1. |
| CNOT | 20,000 shots for each of nine joint Pauli settings | Match the two-qubit CNOT reference; fidelity and purity close to 1, trace distance close to 0. |

In a local validation run on Python 3.14.4, each notebook took approximately 3–7 seconds, including kernel startup and plots but excluding installation and export. Timings depend on hardware. Finite-shot results fluctuate. See [shot counts and statistical precision](docs/validation.md#shot-counts-and-statistical-precision) for why CNOT uses more shots and [validation instructions](docs/validation.md) for the automated checks, tolerances and execution-time report.

## References

- R. Raussendorf and H. J. Briegel, *A One-Way Quantum Computer*, Physical Review Letters **86**, 5188–5191 (2001). [DOI](https://doi.org/10.1103/PhysRevLett.86.5188)
- R. Raussendorf, D. E. Browne and H. J. Briegel, *Measurement-based quantum computation on cluster states*, Physical Review A **68**, 022312 (2003). [DOI](https://doi.org/10.1103/PhysRevA.68.022312)


## Glossary

### Dynamic circuit and classical feedforward

> A quantum circuit is a sequence of quantum operations — including *gates*, *measurements* and *resets* — acting on qubits.
>
> In static circuits, none of those operations depend on data produced at run time. For example, static circuits might only contain measurement operations at the end of the circuit.  
>
>**Dynamic circuits**, on the other hand, incorporate classical processing within the coherence time of the qubits. This means that dynamic circuits can make use of *mid-circuit measurements* and perform *(classical logic) feed-forward operations*, based on the outcome of those measurements to determine what gates to apply next. This process is also known as *classical feedforward*. [[IBM Quantum blog](https://www.ibm.com/quantum/blog/quantum-dynamic-circuits)][[IBM Quantum docs](https://quantum.cloud.ibm.com/docs/en/guides/execute-dynamic-circuits#execute-dynamic-circuits)]

> In these examples, outcome-dependent Pauli corrections are used.

#### Adaptive measurements

**Adaptive measurements** are measurements whose bases are chosen using earlier measurement outcomes within the same shot. 

> In the rotation example, a previously measured bit selects the sign of a rotation applied before the next measurement, thereby changing its effective measurement basis.

This is one use of [classical feed-forward](#dynamic-circuit-and-classical-feedforward): feed-forward supplies and processes the classical outcome, while the adaptive measurement is the quantum operation whose basis is selected.
