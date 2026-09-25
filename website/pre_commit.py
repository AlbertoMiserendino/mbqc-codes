"""Export staged notebooks and include their HTML/PDF in the same commit."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def git(*args):
    return subprocess.check_output(['git', *args])


def main():
    root = Path(git('rev-parse', '--show-toplevel').decode().strip())
    changed = set(git('diff', '--cached', '--name-only', '-z').decode().split('\0'))
    shared = {'requirements.txt', 'requirements-dev.txt', '.python-version',
              'website/no-date.tex.j2', 'website/pre_commit.py', '.githooks/pre-commit'}
    maintained = [
        f'{folder}/{folder[3:]}-{language}.ipynb'
        for folder in ('01-mbqc-teleport', '02-mbqc-rotation', '03-mbqc-cnot')
        for language in ('en', 'it')
    ]
    tracked = set(git('ls-files', '-z').decode().split('\0'))
    notebooks = [p for p in maintained if p in tracked and (p in changed or changed & shared)]
    if not notebooks:
        return
    exports = [str(Path(p).with_suffix(ext)) for p in notebooks for ext in ('.html', '.pdf')]
    # Do not overwrite edits to generated files that the user has not staged.
    for name in exports:
        path = root / name
        if name in tracked:
            if not path.exists() or path.read_bytes() != git('show', ':' + name):
                raise RuntimeError(f'Stage or save aside local export changes first: {name}')
        elif path.exists():
            raise RuntimeError(f'Stage or save aside the existing export first: {name}')
    with tempfile.TemporaryDirectory(prefix='mbqc-pre-commit-') as temporary:
        snapshot = Path(temporary)
        # Checkout the index, including partially staged notebook versions.
        subprocess.run(['git', 'checkout-index', '--all', '--prefix', str(snapshot) + '/'], check=True)
        for name in notebooks:
            for kind in ('html', 'pdf'):
                command = [sys.executable, '-m', 'nbconvert', '--to', kind]
                if kind == 'pdf':
                    command += ['--template-file', str(snapshot / 'website/no-date.tex.j2')]
                subprocess.run(command + [name], cwd=snapshot, check=True)
        # Publish only after every conversion has succeeded.
        for name in exports:
            shutil.copy2(snapshot / name, root / name)
        subprocess.run(['git', 'add', '--', *exports], check=True)
    print(f'Added HTML/PDF exports for {len(notebooks)} staged notebooks to the commit.')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f'Notebook export failed: {error}', file=sys.stderr)
        sys.exit(1)
