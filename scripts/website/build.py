"""Render README.md using Pandoc and the site's shared HTML template."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
REPO = 'https://github.com/AlbertoMiserendino/mbqc-codes'
GITHUB_ONLY_EXTENSIONS = ('.ipynb', '.qasm', '.oqasm', '.pdf')


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])


def render():
    markdown = (ROOT / 'README.md').read_text()
    markdown = re.sub(r'<!-- README-only:start -->.*?<!-- README-only:end -->',
                      '', markdown, flags=re.DOTALL)
    # Pandoc handles Markdown tables, code blocks and heading anchors.
    body = subprocess.run(
        ['pandoc', '--from=gfm', '--to=html5', '--wrap=none'],
        input=markdown, check=True, capture_output=True, text=True,
    ).stdout
    # Open Colab notebooks in a separate browser tab.
    external_icon = (
        '<svg class="external-link-icon" width="12" height="12" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" focusable="false">'
        '<path d="M14 3h7v7M21 3 10 14M10 3H3v18h18v-7"/></svg>'
    )
    body = re.sub(r'<a href="(https://colab\.research\.google\.com/[^"]*)">(.*?)</a>',
                  lambda m: f'<a href="{m[1]}" target="_blank" rel="noopener noreferrer" '
                  f'aria-label="Colab (opens in a new tab)" title="Opens in a new tab">'
                  f'{m[2]} {external_icon}</a>', body)
    # Markdown documentation is browsable on GitHub without a Markdown web server.
    body = re.sub(r'href="(docs/[^"#]+\.md)(#[^"]*)?"',
                  lambda m: f'href="{REPO}/blob/main/{m[1]}{m[2] or ""}"', body)
    # Notebook and OpenQASM sources and PDFs are viewed on GitHub.
    extensions_pattern = '|'.join(re.escape(ext) for ext in GITHUB_ONLY_EXTENSIONS)
    body = re.sub(rf'href="((?![a-zA-Z][a-zA-Z0-9+.-]*:|/)[^"#?]+(?:{extensions_pattern}))([?#][^"]*)?"',
                  lambda m: f'href="{REPO}/blob/main/{m[1]}{m[2] or ""}"', body)
    body = body.replace('href="tests/"', f'href="{REPO}/tree/main/tests"')
    for name in ('requirements.txt', 'requirements-dev.txt'):
        body = body.replace(f'href="{name}"', f'href="{REPO}/blob/main/{name}"')
    body = body.replace('<table>', '<div class="table-wrap" tabindex="0" role="region" aria-label="Scrollable reference table"><table>')
    body = body.replace('</table>', '</table></div>')
    headings = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
    nav = '<nav class="contents" aria-label="On this page">\n'
    nav += ''.join(f'<a href="#{anchor}">{label}</a>\n' for anchor, label in headings)
    nav += '</nav>\n'
    if headings:
        position = body.index('<h2')
        body = body[:position] + nav + body[position:]
    template = (ROOT / 'scripts/website/template.html').read_text()
    if template.count('{{CONTENT}}') != 1:
        raise ValueError('Template must contain exactly one {{CONTENT}} placeholder')
    result = template.replace('{{CONTENT}}', body)
    parsed = Links()
    parsed.feed(result)
    if len(parsed.ids) != len(set(parsed.ids)):
        raise ValueError('Duplicate HTML IDs')
    for link in parsed.links:
        if link.startswith('#') and link[1:] not in parsed.ids:
            raise ValueError(f'Missing anchor: {link}')
        if not link.startswith('#') and '://' not in link:
            if not (ROOT / link.split('#')[0]).exists():
                raise ValueError(f'Missing local target: {link}')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', action='store_true', help='Also assemble build/site for Pages')
    args = parser.parse_args()
    content = render()
    (ROOT / 'index.html').write_text(content)
    if args.stage:
        # Only publish maintained examples and their assets, not the whole checkout.
        destination = ROOT / 'build/site'
        if destination.exists():
            shutil.rmtree(destination)
        destination.mkdir(parents=True)
        (destination / 'index.html').write_text(content)
        shutil.copy2(ROOT / '.nojekyll', destination)
        for directory in sorted((ROOT / 'notebooks').iterdir()):
            if not directory.is_dir() or directory.name.startswith('.'):
                continue
            shutil.copytree(directory, destination / 'notebooks' / directory.name,
                            ignore=shutil.ignore_patterns('.ipynb_checkpoints', '__pycache__',
                                                         *(f'*{ext}' for ext in GITHUB_ONLY_EXTENSIONS)))
    print('Generated index.html from README.md' + (' and staged build/site' if args.stage else ''))


if __name__ == '__main__':
    main()
