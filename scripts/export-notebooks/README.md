# Export notebooks to HTML and PDF

Export uses `nbconvert`, included in [requirements-dev.txt](../../requirements-dev.txt). Complete the [project setup](../../README.md#run-locally) before exporting.

Exports use saved notebook outputs without executing cells. Run and save the notebook first to include updated results. Generated files are saved alongside the source notebook and overwrite existing exports with the same name.

## Export to HTML

From the repository root:

```bash
source .venv/bin/activate
cd notebooks/01-mbqc-teleport
python -m jupyter nbconvert --to html mbqc-teleport-en.ipynb
```

Open the generated HTML file in a browser. Interactive plots that require a running Python kernel are not available in the exported page.

## Export to PDF

PDF export also requires Pandoc and XeLaTeX. On Ubuntu/Debian (including WSL Ubuntu), install these system dependencies outside the Python virtual environment:

```bash
sudo apt update
sudo apt install pandoc texlive-xetex texlive-fonts-recommended texlive-plain-generic
```

Verify that the tools are available:

```bash
pandoc --version
xelatex --version
```

From the repository root:

```bash
source .venv/bin/activate
cd notebooks/01-mbqc-teleport
python -m jupyter nbconvert --to pdf --template-file ../../scripts/export-notebooks/no-date.tex.j2 mbqc-teleport-en.ipynb
```

The shared [no-date.tex.j2](no-date.tex.j2) template removes the date from the PDF title. The pre-commit hook, optional GitHub Pages export step and VS Code PDF tasks use this template too.

## Export with the shared script

To export all six maintained notebooks to both formats, install the PDF dependencies above and run from the repository root:

```bash
bash scripts/export-notebooks/export-notebooks.sh
```

An optional output directory keeps exports away from tracked files. Additional arguments select specific notebooks:

```bash
bash scripts/export-notebooks/export-notebooks.sh build/exports
bash scripts/export-notebooks/export-notebooks.sh build/exports notebooks/01-mbqc-teleport/mbqc-teleport-en.ipynb
```

Use `""` as the output directory to export selected notebooks alongside their sources. The pre-commit hook uses this script inside a temporary staging snapshot, supplying its Python interpreter through `MBQC_PYTHON`.

## Use the VS Code tasks

The export tasks are defined in [.vscode/tasks.json](../../.vscode/tasks.json). Open the repository root as the VS Code workspace and complete the setup above. The tasks use `${workspaceFolder}/.venv/bin/jupyter` directly, so activating the environment in a terminal or selecting a different notebook kernel does not change the interpreter used for export. If your environment is elsewhere, update the executable path in the corresponding task commands.

### Export the current notebook

1. Open the `.ipynb` file you want to export and keep it as the active editor tab.
2. Run and save the notebook to include the latest outputs.
3. Choose **Terminal → Run Task**, then **Jupyter: Export current notebook to HTML** or **Jupyter: Export current notebook to PDF**.
4. Check the task terminal for the result. The `.html` or `.pdf` file is written next to the notebook with the same base name.

The task uses the active file's name (`${fileBasename}`) and directory (`${fileDirname}`). Keep the notebook selected when starting it; selecting an exported HTML file or a Markdown guide would pass that file to `nbconvert` instead.

### Export all notebooks

Choose **Terminal → Run Task → Jupyter: Export ALL notebooks to HTML** or **Jupyter: Export ALL notebooks to PDF**. This task searches `notebooks/` recursively for `.ipynb` files and saves each export alongside its source notebook. Check the task terminal for conversion errors for each notebook.

All export tasks export saved outputs without executing notebook cells and overwrite existing exports with the same name. The tasks are configured for Linux or WSL; the batch task uses `find` and `sh`.

For PDF export, Pandoc and XeLaTeX must also be available on the `PATH` used by VS Code. If the task reports that either command is missing after installation, restart VS Code and retry.
