# Build and publish the website

The README supplies the page content. Edit `website/template.html` for colors, layout and the GitHub button; do not edit generated `index.html` directly.

## Local generation

The generator uses Python's standard library and the Pandoc executable. On Ubuntu/WSL:

```bash
sudo apt update
sudo apt install pandoc
python3 website/build.py
```

Alternatively, use **Terminal → Run Task → Website: Build index from README** in VS Code. No Python package or active virtual environment is required. This command updates `index.html`, derives navigation from README headings and checks local links and anchors. Documentation links point to GitHub; notebook HTML links remain relative.

Preview from the repository root using Live Server or:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://localhost:8000`. The build runs when invoked, not automatically on every save. Commit the regenerated index with README or template edits to keep the local preview current.

## Export automatically before committing

Enable the versioned Git hook once per clone, from the repository root:

```bash
git config --local core.hooksPath .githooks
```

The `pre-commit` hook exports staged maintained notebooks to HTML and PDF and adds the exports to the same commit. Changes to the shared requirements, Python version, PDF template or hook regenerate all six notebooks. Commits unrelated to these files skip export; pushing does not regenerate anything locally.

The hook exports a temporary copy of the Git staging area, so unstaged notebook edits are not included. If an affected HTML/PDF has unstaged changes, the commit stops: stage those changes or save them elsewhere first. Failed conversions stop the commit before copying any exports back.

The hook uses the interpreter configured in the local Git setting `mbqc.python`, then `.venv/bin/python` when available, otherwise `python3` from `PATH`. Configure an external environment once per clone so commits from VS Code also use it without terminal activation:

```bash
git config --local mbqc.python "$HOME/venvs/qgss26venv/bin/python"
git add <changed-files>
git commit
```

Install the development requirements from the [setup guide](../README.md#setup), plus Pandoc and XeLaTeX from [PDF export](export-pdf.md). Exports use saved notebook outputs without executing cells. Run and save notebooks before staging them when results need updating.

For manual export of all six notebooks, use `bash website/export-notebooks.sh`. An optional output directory, such as `build/exports`, keeps manual exports away from tracked files. GitHub Pages publishes the exports committed to the repository.

## GitHub Pages

In the repository's **Settings → Pages → Build and deployment**, select **GitHub Actions** as the source. The `Publish website` workflow rebuilds and deploys on pushes to `main` that change the README, template/generator, maintained examples, requirements, `.python-version`, `.nojekyll` or the workflow itself. It can also be started manually from Actions.

The build uses `python3 website/build.py --stage` to recreate `build/site/` with the generated index, `.nojekyll`, requirements and the three maintained example directories. Only that directory is uploaded. The workflow publishes an artifact; it does not commit generated files back to Git. No Jekyll is used.

The workflow installs Pandoc and uses the runner's Python to generate the index, then copies the committed HTML and PDF exports into the Pages artifact without regenerating them. Run and save notebooks before committing if results need updating; the pre-commit hook includes updated exports in that commit.

The notebook regeneration steps remain in `.github/workflows/pages.yml`, disabled by `REGENERATE_NOTEBOOK_EXPORTS: 'false'`. Set this flag to `'true'` to restore Python setup, installation of the export dependencies and HTML/PDF regeneration in CI. The quantum-validation workflow remains separate; a successful website deployment does not imply that notebook tests passed.

See [GitHub's custom workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) for Pages configuration.
