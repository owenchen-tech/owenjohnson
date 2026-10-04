"""Check generated page structure and every local link using the standard library."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parent

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.ids = set()
        self.links = []
        self.headings = []
        self.title = False
        self.description = False
        self.main = 0
        self.errors = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                self.errors.append(f'duplicate id: {attrs["id"]}')
            self.ids.add(attrs['id'])
        if tag in ('a', 'link') and attrs.get('href'):
            self.links.append(attrs['href'])
        if tag in ('img', 'script') and attrs.get('src'):
            self.links.append(attrs['src'])
        if tag == 'img' and not attrs.get('alt'):
            self.errors.append('image missing meaningful alt text')
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self.headings.append(int(tag[1]))
        if tag == 'title':
            self.title = True
        if tag == 'main':
            self.main += 1
        if tag == 'meta' and attrs.get('name') == 'description' and attrs.get('content'):
            self.description = True

pages = {}
for path in ROOT.rglob('*.html'):
    if 'dist' in path.relative_to(ROOT).parts:
        continue
    parser = Page(path)
    parser.feed(path.read_text())
    pages[path.resolve()] = parser
errors = []
links = 0
for path, parser in pages.items():
    label = str(path.relative_to(ROOT))
    errors.extend(f'{label}: {err}' for err in parser.errors)
    if parser.headings.count(1) != 1 or parser.main != 1 or not parser.title or not parser.description:
        errors.append(f'{label}: missing page metadata, single H1, or main landmark')
    for a, b in zip(parser.headings, parser.headings[1:]):
        if b > a + 1:
            errors.append(f'{label}: skipped heading level {a} → {b}')
    for link in parser.links:
        parsed = urlparse(link)
        if parsed.scheme or parsed.netloc:
            continue
        links += 1
        target = (ROOT / unquote(parsed.path).lstrip('/')) if parsed.path.startswith('/') else path.parent / unquote(parsed.path)
        if not parsed.path:
            target = path
        if target.is_dir():
            target /= 'index.html'
        target = target.resolve()
        if not target.is_file():
            errors.append(f'{label}: broken link {link}')
        elif parsed.fragment and (target not in pages or unquote(parsed.fragment) not in pages[target].ids):
            errors.append(f'{label}: missing fragment {link}')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'PASS: {len(pages)} pages, {links} local links, metadata, heading order, image alt text, and unique IDs.')
