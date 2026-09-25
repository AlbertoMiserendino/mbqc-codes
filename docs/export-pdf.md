# Export to PDF

PDF export with `nbconvert` requires Pandoc and XeLaTeX in addition to the Python packages in [requirements-dev.txt](../requirements-dev.txt). On Ubuntu/Debian (including WSL Ubuntu), install these system dependencies:

```bash
sudo apt update
sudo apt install pandoc
sudo apt install texlive-xetex texlive-fonts-recommended texlive-plain-generic
```

These packages are installed at the system level, outside the Python virtual environment. Verify that the tools are available:

```bash
pandoc --version
xelatex --version
```

After completing the [project setup](../README.md#setup), from the repository root, activate the virtual environment and export a notebook:

```bash
source .venv/bin/activate
cd 01-mbqc-teleport
python -m jupyter nbconvert --to pdf --template-file ../website/no-date.tex.j2 mbqc-teleport-en.ipynb
```

The PDF is saved alongside the notebook. Export uses the notebook's saved outputs; run and save the notebook first to include updated results.

The shared `website/no-date.tex.j2` template removes the date from the PDF title. The pre-commit hook, GitHub Pages workflow and VS Code PDF tasks use this template too.

## Use the VS Code tasks

The export tasks are defined in [.vscode/tasks.json](../.vscode/tasks.json). Open the repository root as the VS Code workspace and complete the setup above. The tasks use `${workspaceFolder}/.venv/bin/jupyter` directly, so activating the environment in a terminal or selecting a different notebook kernel does not change the interpreter used for export. If your environment is elsewhere, update the executable path in the corresponding task commands.

### Export the current notebook

1. Open the `.ipynb` file you want to export and keep it as the active editor tab.
2. Run and save the notebook to include the latest outputs.
3. Choose **Terminal → Run Task**, then **Jupyter: Export current notebook to PDF**.
4. Check the task terminal for the result. The `pdf` file is written next to the notebook with the same base name.

The task uses the active file's name (`${fileBasename}`) and directory (`${fileDirname}`). Keep the notebook selected when starting it; selecting an exported HTML file or a Markdown guide would pass that file to `nbconvert` instead.

### Export all notebooks

Choose **Terminal → Run Task → Jupyter: Export ALL notebooks to PDF**. This task searches the entire workspace recursively for `.ipynb` files and saves each export alongside its source notebook. The task attempts every matching notebook and returns a failure status if any conversion fails.

Both tasks export saved outputs without executing notebook cells and overwrite existing exports with the same name. The tasks are configured for Linux or WSL; the batch task uses `find` and `sh`.

Pandoc and XeLaTeX must also be available on the `PATH` used by VS Code. If the task reports that either command is missing after installation, restart VS Code and retry.
