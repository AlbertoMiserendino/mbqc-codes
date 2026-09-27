#!/usr/bin/env bash
# Export saved notebook outputs without executing cells.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/../.."
# An optional output root keeps verification exports away from tracked files.
# Additional arguments select notebooks; omit them to export all official examples.
# Usage: export-notebooks.sh [output-root [notebook ...]]
output_root="${1:-}"
if [[ $# -gt 0 ]]; then
  shift
fi
# The pre-commit snapshot has no virtualenv, so allow its caller to supply Python.
if [[ -n "${MBQC_PYTHON:-}" ]]; then
  python_bin="$MBQC_PYTHON"
elif [[ -x .venv/bin/python ]]; then
  python_bin="$PWD/.venv/bin/python"
else
  python_bin="python3"
fi

for dependency in pandoc xelatex; do
  if ! command -v "$dependency" >/dev/null 2>&1; then
    echo "Missing $dependency. See scripts/export-notebooks/README.md for installation instructions." >&2
    exit 1
  fi
done
if ! "$python_bin" -c 'import nbconvert' >/dev/null 2>&1; then
  echo "Run uv sync --locked from the repository root before exporting." >&2
  exit 1
fi

notebooks=("$@")
if [[ ${#notebooks[@]} -eq 0 ]]; then
  shopt -s nullglob
  for directory in notebooks/*/; do
    notebooks+=("$directory"*.ipynb)
  done
  if [[ ${#notebooks[@]} -eq 0 ]]; then
    echo "No notebooks found under notebooks/." >&2
    exit 1
  fi
fi

for notebook in "${notebooks[@]}"; do
  directory="$(dirname "$notebook")"
  output_args=()
  if [[ -n "$output_root" ]]; then
    mkdir -p "$output_root/$directory"
    output_args=(--output-dir "$(cd "$output_root/$directory" && pwd)")
  fi
  "$python_bin" -m jupyter nbconvert --to html "${output_args[@]}" "$notebook"
  "$python_bin" -m jupyter nbconvert --to pdf "${output_args[@]}" --template-file "$PWD/scripts/export-notebooks/no-date.tex.j2" "$notebook"
done
