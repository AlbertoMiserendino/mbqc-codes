"""Export staged notebooks and include their HTML/PDF in the same commit."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile


def git(*args):
    # Keep raw bytes so generated files can be compared with their staged contents.
    return subprocess.check_output(['git', *args])


def main():
    root = Path(git('rev-parse', '--show-toplevel').decode().strip())
    # Read changes from the index (staging area), which defines the next commit.
    # NUL separators preserve filenames containing spaces or newlines.
    changed = set(git('diff', '--cached', '--name-only', '-z').decode().split('\0'))
    # Changes to dependencies, the PDF template, or the hook require fresh exports
    # for every maintained notebook, even when the notebook itself is unchanged.
    shared = {'pyproject.toml', 'uv.lock', 'requirements.txt', 'requirements-dev.txt', '.python-version',
              'scripts/export-notebooks/no-date.tex.j2', 'scripts/export-notebooks/export-notebooks.sh',
              'scripts/pre_commit.py', '.githooks/pre-commit'}
    tracked = set(git('ls-files', '-z').decode().split('\0'))
    # Discover notebook files from the index, including staged additions and moves.
    maintained = sorted(
        name for name in tracked
        if len(Path(name).parts) == 3 and Path(name).parts[0] == 'notebooks'
        and not Path(name).parts[1].startswith('.') and name.endswith('.ipynb')
    )
    # Select notebooks in the index affected by notebook or shared-file changes.
    notebooks = [p for p in maintained if p in tracked and (p in changed or changed & shared)]
    if not notebooks:
        return
    exports = [str(Path(p).with_suffix(ext)) for p in notebooks for ext in ('.html', '.pdf')]

    # Do not overwrite edits to generated files that the user has not staged.
    for name in exports:
        path = root / name
        if name in tracked:
            # ':path' reads the staged version; any local difference must be preserved.
            if not path.exists() or path.read_bytes() != git('show', ':' + name):
                raise RuntimeError(f'Stage or save aside local export changes first: {name}')
        elif path.exists():
            # An untracked export may also contain work that must not be overwritten.
            raise RuntimeError(f'Stage or save aside the existing export first: {name}')

    with tempfile.TemporaryDirectory(prefix='mbqc-pre-commit-') as temporary:
        snapshot = Path(temporary)

        # Export a temporary snapshot of the index, so unstaged notebook edits
        # cannot leak into the generated files committed by this hook.
        subprocess.run(['git', 'checkout-index', '--all', '--prefix', str(snapshot) + '/'], check=True)

        # Reuse the staged exporter and template with this hook's Python environment.
        # An empty output root writes exports next to the selected snapshot notebooks.
        subprocess.run(
            ['bash', str(snapshot / 'scripts/export-notebooks/export-notebooks.sh'), '', *notebooks],
            cwd=snapshot, env={**os.environ, 'MBQC_PYTHON': sys.executable}, check=True,
        )

        # Publish only after every conversion has succeeded.
        for name in exports:
            shutil.copy2(snapshot / name, root / name)
        # Stage the generated files so they are included in the pending commit.
        subprocess.run(['git', 'add', '--', *exports], check=True)

    print(f'Added HTML/PDF exports for {len(notebooks)} staged notebooks to the commit.')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError) as error:
        # A nonzero exit status tells the calling pre-commit hook to stop the commit.
        print(f'Notebook export failed: {error}', file=sys.stderr)
        sys.exit(1)
