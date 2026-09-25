# Export to HTML

HTML export uses `nbconvert`, included in [requirements-dev.txt](../requirements-dev.txt). Complete the [project setup](../README.md#setup), then run these commands from the repository root:

```bash
source .venv/bin/activate
cd 01-mbqc-teleport
python -m jupyter nbconvert --to html mbqc-teleport-en.ipynb
```

The HTML file is saved alongside the notebook and can be opened in a browser. Export uses the notebook's saved outputs; run and save the notebook first to include updated results. Interactive plots that require a running Python kernel are not available in the exported page.

## Use the VS Code tasks

The export tasks are defined in [.vscode/tasks.json](../.vscode/tasks.json). Open the repository root as the VS Code workspace and complete the setup above. The tasks use `${workspaceFolder}/.venv/bin/jupyter` directly, so activating the environment in a terminal or selecting a different notebook kernel does not change the interpreter used for export. If your environment is elsewhere, update the executable path in the corresponding task commands.

### Export the current notebook

1. Open the `.ipynb` file you want to export and keep it as the active editor tab.
2. Run and save the notebook to include the latest outputs.
3. Choose **Terminal → Run Task**, then **Jupyter: Export current notebook to HTML**.
4. Check the task terminal for the result. The `html` file is written next to the notebook with the same base name.

The task uses the active file's name (`${fileBasename}`) and directory (`${fileDirname}`). Keep the notebook selected when starting it; selecting an exported HTML file or a Markdown guide would pass that file to `nbconvert` instead.

### Export all notebooks

Choose **Terminal → Run Task → Jupyter: Export ALL notebooks to HTML**. This task searches the entire workspace recursively for `.ipynb` files and saves each export alongside its source notebook. The task attempts every matching notebook and returns a failure status if any conversion fails.

Both tasks export saved outputs without executing notebook cells and overwrite existing exports with the same name. The tasks are configured for Linux or WSL; the batch task uses `find` and `sh`.
