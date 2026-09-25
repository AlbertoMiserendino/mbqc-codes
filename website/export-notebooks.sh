#!/usr/bin/env bash
# Export saved notebook outputs without executing cells.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
# An optional output root keeps verification exports away from tracked files.
output_root="${1:-}"
if [[ $# -gt 1 ]]; then
  echo "Usage: bash website/export-notebooks.sh [output-root]" >&2
  exit 2
fi
if [[ -x .venv/bin/python ]]; then
  python_bin="$PWD/.venv/bin/python"
else
  python_bin="python3"
fi

for dependency in pandoc xelatex; do
  if ! command -v "$dependency" >/dev/null 2>&1; then
    echo "Missing $dependency. See docs/export-pdf.md for installation instructions." >&2
    exit 1
  fi
done
if ! "$python_bin" -c 'import nbconvert' >/dev/null 2>&1; then
  echo "Install requirements-dev.txt in .venv or the active Python environment before exporting." >&2
  exit 1
fi

for directory in 01-mbqc-teleport 02-mbqc-rotation 03-mbqc-cnot; do
  output_args=()
  if [[ -n "$output_root" ]]; then
    mkdir -p "$output_root/$directory"
    output_args=(--output-dir "$(cd "$output_root/$directory" && pwd)")
  fi
  for language in en it; do
    notebook="$directory/${directory#??-}-$language.ipynb"
    "$python_bin" -m jupyter nbconvert --to html "${output_args[@]}" "$notebook"
    "$python_bin" -m jupyter nbconvert --to pdf "${output_args[@]}" --template-file "$PWD/website/no-date.tex.j2" "$notebook"
  done
done
