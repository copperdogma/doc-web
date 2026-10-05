"""Exact document-local reference inventory and conservative DOM enrichment."""
import posixpath
import re
from collections import defaultdict
from urllib.parse import quote, urlsplit

from bs4 import BeautifulSoup, CData, NavigableString

POLICY_ID = 'exact-source-reference-v1'
NUMBER = r'(?:\d+(?:\.\d+)*[A-Za-z]?|[ivxlcdm]+)'
EXPLICIT = re.compile(r'(?<!\w)(?P<kind>pages?|pp?\.|chapters?|sections?|§|paragraphs?|¶|figures?|fig\.|tables?|footnotes?|notes?)\s*(?P<label>' + NUMBER + r')(?P<range>\s*[-–—]\s*' + NUMBER + r')?(?!\w)', re.I)
URL = re.compile(r'https?://[^\s<>"\u201c\u201d\x00]+', re.I)
TARGET = re.compile(r'^\s*(chapter|section|paragraph|figure|fig\.|table|footnote|note)\s+(' + NUMBER + r')(?=\s|[.:)\-]|$)', re.I)
TURN = re.compile(r'(?<!\w)(?:turn|return|go|refer)\s+to\s+(?:paragraph\s+)?(?P<label>\d+[A-Za-z]?)(?P<range>\s*[-–—]\s*\d+[A-Za-z]?)?(?!\w)', re.I)
SKIP = {'a', 'code', 'pre', 'script', 'style', 'nav', 'textarea', 'template', 'noscript'}
BLOCKS = {'p', 'li', 'td', 'th', 'dt', 'dd', 'figcaption', 'caption'}
HEADINGS = {f'h{level}' for level in range(1, 7)}
STRUCTURAL = BLOCKS | HEADINGS | {'ul', 'ol', 'dl', 'table', 'thead', 'tbody', 'tfoot', 'tr', 'div', 'section', 'article', 'aside', 'blockquote', 'figure', 'header', 'footer', 'main', 'address', 'form', 'fieldset', 'details', 'summary', 'hr'}


def stream_nodes(block):
    """Emit both structural boundaries, even for a container with no text."""
    pending = list(reversed(block.contents))
    while pending:
        node = pending.pop()
        yield node
        if node is not None and not isinstance(node, NavigableString):
            if node.name in STRUCTURAL:
                yield None
                pending.append(None)
            pending.extend(reversed(node.contents))


def parse_uri(value):
    """Validate literal URI syntax before urllib can normalize controls away."""
    if any(ord(c) < 32 or ord(c) == 127 for c in value):
        return None, 'invalid_url_controls'
    try:
        parsed = urlsplit(value)
        if parsed.scheme.casefold() in {'http', 'https'}:
            if not parsed.hostname or parsed.username or parsed.password:
                return None, 'invalid_http_url'
            parsed.port
        return parsed, None
    except ValueError:
        return None, 'invalid_http_url'


def canonical_kind(kind):
    k = kind.casefold().rstrip('.')
    if k in {'p', 'pp', 'page', 'pages'}:
        return 'page'
    if k == '§':
        return 'section'
    if k == '¶':
        return 'paragraph'
    if k == 'fig':
        return 'figure'
    if k.startswith('note'):
        return 'footnote'
    return k.rstrip('s')


def label_key(value):
    text = str(value).strip()
    return text.casefold() if re.fullmatch(r'[ivxlcdm]+', text, re.I) else text


def forbidden(tag):
    return any((parent.name in SKIP and not (parent.name == 'nav' and re.search(r'\b(toc|index|contents)\b', ' '.join([parent.get('epub:type', ''), parent.get('role', ''), *parent.get('class', [])])))) or parent.has_attr('data-doc-web-navigation-status') or parent.has_attr('hidden')
               or parent.get('role') == 'navigation' for parent in [tag, *tag.parents] if parent.name)


def text_stream(block):
    """One edit domain: exact ordinary text nodes owned by this block.

    Specialized strings and excluded/nested block text remain opaque barriers.
    Slot coordinates include barriers so discovery and mutation share a map.
    """
    pieces, slots, offset, source_offset = [], [], 0, 0
    for node in stream_nodes(block):
        if node is None:
            pieces.append('\x00')
            slots.append((None, offset, offset + 1, False, source_offset, source_offset))
            offset += 1
            continue
        if not isinstance(node, NavigableString):
            if node.name and forbidden(node) and not any(isinstance(child, NavigableString) for child in node.descendants):
                pieces.append('\x00')
                slots.append((None, offset, offset + 1, False, source_offset, source_offset))
                offset += 1
            continue
        owner = next((p for p in node.parents if p.name in BLOCKS), None)
        editable = type(node) is NavigableString and owner is block and not forbidden(node.parent) and not any(p.name in HEADINGS for p in node.parents)
        value = str(node)
        width = len(value) if editable else max(1, len(value))
        pieces.append(value if editable else '\x00' * width)
        source_width = len(value) if type(node) in {NavigableString, CData} else 0
        slots.append((node, offset, offset + width, editable, source_offset, source_offset + source_width))
        offset += width
        source_offset += source_width
    return ''.join(pieces), slots


def source_location(slots, start, end, base=0):
    first = next(s for s in slots if s[3] and s[1] <= start < s[2])
    last = next(s for s in slots if s[3] and s[1] < end <= s[2])
    return {'start': base + first[4] + start - first[1],
            'end': base + last[4] + end - last[1]}


def source_block_base(block, source_tag):
    """Offset of an eligible nested block within its nearest ID-bearing block."""
    if block is source_tag:
        return 0
    total = 0
    for node in source_tag.descendants:
        if node is block:
            return total
        if type(node) in {NavigableString, CData}:
            total += len(str(node))
    return 0


IDENTITY_FIELDS = (
    ('page_id', ('source_page_id', 'page_id')),
    ('original_page_number', ('source_original_page_number', 'original_page_number')),
    ('spread_side', ('source_spread_side', 'spread_side')),
)


def raw_page_identity(page):
    label = page.get('printed_page_number_text')
    if label is None:
        label = page.get('printed_page_number')
    return (str(page.get('page_number', page.get('page'))),
            *(str(page.get(key)) for key, _ in IDENTITY_FIELDS),
            label_key(label) if label is not None else None,
            bool(page.get('printed_page_number_inferred')))


def identity_matches(row, raw):
    """All supplied identity evidence must agree, including print-label evidence."""
    for raw_key, row_keys in IDENTITY_FIELDS:
        values = [row[k] for k in row_keys if row.get(k) is not None]
        if values and (raw.get(raw_key) is None or any(str(value) != str(raw[raw_key]) for value in values)):
            return False
    row_labels = [row[k] for k in ('source_printed_page_label', 'source_printed_page_number') if row.get(k) is not None]
    raw_label = raw.get('printed_page_number_text')
    if raw_label is None:
        raw_label = raw.get('printed_page_number')
    if row_labels and (raw_label is None or any(label_key(value) != label_key(raw_label) for value in row_labels)):
        return False
    return True


def href_for(path, target):
    relative = '' if path == target['path'] else posixpath.relpath(target['path'], posixpath.dirname(path) or '.')
    return quote(relative, safe='/') + '#' + quote(target['id'], safe='-._~')


class ReferenceIndex:
    """Build once from final IDs and observed source evidence; never infer offsets."""
    def __init__(self, entries, soups, ids, source_pages, provenance_rows, *, source_soups=None):
        # Source soups are read-only and confined to this invocation. Sharing
        # identical bytes never shares entry/page authority or mutable final DOM.
        source_soups = {} if source_soups is None else source_soups

        def source_soup(page):
            source_html = page.get('html') or ''
            if source_html not in source_soups:
                source_soups[source_html] = BeautifulSoup(source_html, 'html.parser')
            return source_soups[source_html]

        self.targets = defaultdict(list)
        self.rejected_pages = defaultdict(list)
        self.page_observations = defaultdict(list)
        self.provenance = {(r.get('html_path'), r['block_id']): r for r in provenance_rows if r.get('block_id')}
        self.unscoped_provenance = {r['block_id']: r for r in provenance_rows if r.get('block_id') and not r.get('html_path')}
        rows_by_page = defaultdict(list)
        for path, soup in soups.items():
            for tag in soup.find_all(id=True):
                row = self.provenance.get((path, tag['id']), self.unscoped_provenance.get(tag['id']))
                if row and ids[path][tag['id']] == 1:
                    rows_by_page[str(row.get('source_page_number'))].append((path, tag['id'], row))
        for entry in entries:
            path = entry['filename']
            source_texts = {' '.join(t.get_text(' ', strip=True).split()) for page in entry.get('prepared_pages', [])
                            for t in source_soup(page).find_all()}
            for tag in soups[path].find_all(id=True):
                text = ' '.join(tag.get_text(' ', strip=True).split())
                if ids[path][tag['id']] != 1 or text not in source_texts or forbidden(tag):
                    continue
                label_tag = tag.find(['figcaption', 'caption']) if tag.name in {'figure', 'table'} else tag
                match = TARGET.match(' '.join(label_tag.get_text(' ', strip=True).split())) if label_tag else None
                if match and (re.fullmatch(r'h[1-6]', tag.name) or tag.name in {'caption', 'figcaption', 'figure', 'table', 'aside'} or (tag.name in {'p', 'li', 'dt'} and ((match[1].casefold() == 'paragraph' and re.match(r'^\s*paragraph\s+' + NUMBER + r'[.:)]', text, re.I)) or tag.get('role') == 'doc-footnote' or any(c in {'footnote', 'figure-caption', 'table-caption', 'section-label', 'paragraph-label'} for c in tag.get('class', []))))):
                    self.add(canonical_kind(match[1]), match[2], path, tag['id'], {'source_text': text})
                if re.fullmatch(r'h[1-6]', tag.name):
                    leading = re.match(r'^(' + NUMBER + r')(?:[.:)]?\s+|[.:)]?$)', text, re.I)
                    if leading:
                        self.add('section', leading[1], path, tag['id'], {'source_text': text})
                        self.add('paragraph', leading[1], path, tag['id'], {'source_text': text})
        raw_pages = list(source_pages) or [p for e in entries for p in e.get('prepared_pages', [])]
        seen = set()
        identities_by_number = defaultdict(dict)
        for raw in raw_pages:
            identities_by_number[str(raw.get('page_number', raw.get('page')))][raw_page_identity(raw)] = raw
        proven_by_identity = defaultdict(list)
        for number, rows in rows_by_page.items():
            group = identities_by_number.get(number, {})
            for candidate in rows:
                matches = [identity for identity, raw in group.items() if identity_matches(candidate[2], raw)]
                if len(matches) == 1:
                    proven_by_identity[matches[0]].append(candidate)
        for page in raw_pages:
            number = page.get('page_number', page.get('page'))
            label = page.get('printed_page_number_text')
            if label is None:
                label = page.get('printed_page_number')
            if label is None:
                continue
            key = raw_page_identity(page)
            if key in seen:
                continue
            seen.add(key)
            label = str(label).strip()
            reason = None
            if page.get('printed_page_number_inferred'):
                reason = 'inferred_printed_label'
            elif not re.fullmatch(r'\d+|[ivxlcdm]+', label, re.I):
                reason = 'unsupported_printed_label_or_spread'
            if reason:
                self.rejected_pages[label_key(label)].append(reason)
                continue
            self.page_observations[label_key(label)].append({'source_page_number': number, 'printed_label': label, **{k: page[k] for k in ('original_page_number', 'spread_side', 'page_id') if k in page}})
            candidates = proven_by_identity.get(key, [])
            if not candidates:
                # Without provenance require a unique final match to this page's
                # first source block, never the first ID of the whole chapter.
                source = source_soup(page)
                first = source.find(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'table', 'figure'])
                if first and len(identities_by_number[str(number)]) == 1 and not rows_by_page.get(str(number)):
                    source_text = ' '.join(first.get_text(' ', strip=True).split())
                    matches = [(path, tag['id'], {}) for path, soup in soups.items()
                               for tag in soup.find_all(id=True)
                               if ids[path][tag['id']] == 1 and tag.name == first.name
                               and ' '.join(tag.get_text(' ', strip=True).split()) == source_text]
                    if len(matches) == 1:
                        candidates = matches
            # One page can span multiple files; the first source block is its start.
            if candidates:
                path, identifier, _ = candidates[0]
                self.add('page', label, path, identifier, {'printed_label': label, 'source_page_number': number, 'observed': True, **{k: page[k] for k in ('original_page_number', 'spread_side', 'page_id') if k in page}})

    def add(self, kind, label, path, identifier, evidence):
        target = {'path': path, 'id': identifier, 'kind': kind, 'evidence': evidence}
        bucket = self.targets[(kind, label_key(label))]
        if not any(t['path'] == path and t['id'] == identifier and (kind != 'page' or t['evidence'].get('source_page_number') == evidence.get('source_page_number')) for t in bucket):
            bucket.append(target)

    def lookup(self, kind, label):
        if kind == 'numbered_location':
            found = self.lookup('paragraph', label) + self.lookup('section', label)
            return list({(t['path'], t['id']): t for t in found}.values())
        return list(self.targets.get((kind, label_key(label)), []))


def context_kind(block):
    for parent in [block, *block.parents]:
        if not parent.name:
            continue
        values = ' '.join([str(parent.get('role', '')), str(parent.get('epub:type', '')), ' '.join(parent.get('class', [])), str(parent.get('id', ''))]).casefold()
        if re.search(r'\b(toc|index|table-of-contents|contents)\b', values):
            return 'index' if 'index' in values else 'toc'
    heading = block.find_previous(re.compile(r'^h[1-6]$'))
    if heading:
        title = ' '.join(heading.get_text(' ', strip=True).split()).casefold()
        if title in {'contents', 'table of contents', 'index'}:
            return 'index' if title == 'index' else 'toc'
    return None


def discover(block):
    text, slots = text_stream(block)
    spans = []
    for match in EXPLICIT.finditer(text):
        spans.append((match.start(), match.end(), canonical_kind(match['kind']), match['label'], bool(match['range'])))
    for match in TURN.finditer(text):
        spans.append((match.start(), match.end(), 'paragraph' if re.search(r'\bparagraph\b', match[0], re.I) else 'numbered_location', match['label'], bool(match['range'])))
    for match in URL.finditer(text):
        if match.end() < len(text) and text[match.end()] == '\x00':
            spans.append((match.start(), match.end(), 'url_blocked', match[0], False))
            continue
        end = match.end()
        while end > match.start() and text[end - 1] in '.,;:!?':
            end -= 1
        for left, right in [('(', ')'), ('[', ']')]:
            while end > match.start() and text[end-1] == right and text[match.start():end].count(right) > text[match.start():end].count(left):
                end -= 1
        spans.append((match.start(), end, 'url', text[match.start():end], False))
    for segment in re.finditer(r'[^\x00]+', text):
        segment_text = segment[0]
        if not (context_kind(block) or re.search(r'\.{3,}\s*(?:\d+|[ivxlcdm]+)\s*$', segment_text, re.I)):
            continue
        # Only destination-shaped suffixes of this block's own text segment.
        match = re.search(r'(?:\.{2,}\s*|\s+|^)((?:\d+|[ivxlcdm]+)(?:\s*[-–—,]\s*(?:\d+|[ivxlcdm]+))*)\s*$', segment_text, re.I)
        if match:
            for token in re.finditer(r'(\d+|[ivxlcdm]+)(?:\s*[-–—]\s*(?:\d+|[ivxlcdm]+))?', match[1], re.I):
                start = segment.start() + match.start(1) + token.start()
                end = segment.start() + match.start(1) + token.end()
                if not any(a < end and start < b for a, b, *_ in spans):
                    spans.append((start, end, 'page', token[1], bool(re.search('[-–—]', token[0]))))
    # Literal URLs own their text; among explicit phrases retain the longest
    # occurrence. One logical interval can never be rewritten twice.
    selected = []
    for span in sorted(spans, key=lambda s: (0 if s[2].startswith('url') else 1, -(s[1] - s[0]), s[0])):
        if not any(a < span[1] and span[0] < b for a, b, *_ in selected):
            selected.append(span)
    spans = sorted(selected)
    return text, slots, spans


def wrap_range(soup, slots, start, end, href=None, status=None):
    """Wrap a contiguous DOM range without cloning tags or provenance IDs.

    Whole inline elements move intact. Partial elements use same-target text
    leaf wrappers, preserving the parent tree and avoiding duplicated IDs.
    """
    selected = []
    for node, node_start, node_end, editable, _, _ in slots:
        if not editable:
            continue
        value = str(node)
        lo, hi = max(start - node_start, 0), min(end - node_start, node_end - node_start)
        if lo >= hi:
            continue
        replacement = NavigableString(value[lo:hi])
        pieces = ([NavigableString(value[:lo])] if lo else []) + [replacement] + ([NavigableString(value[hi:])] if hi < len(value) else [])
        node.replace_with(*pieces)
        selected.append(replacement)
    if not selected:
        return False
    parents = list(selected[0].parents)
    common = next((p for p in parents if all(any(p is ancestor for ancestor in n.parents) for n in selected)), None)
    if common is None:
        return False
    units = []
    partial = False
    selected_ids = {id(n) for n in selected}
    for node in selected:
        unit = node
        while unit.parent is not common:
            unit = unit.parent
        if unit.name and any(id(n) not in selected_ids for n in unit.descendants if isinstance(n, NavigableString)):
            partial = True
        if not any(unit is existing for existing in units):
            units.append(unit)
    if units:
        siblings = list(common.contents)
        first_index = next(i for i, sibling in enumerate(siblings) if sibling is units[0])
        last_index = next(i for i, sibling in enumerate(siblings) if sibling is units[-1])
        if any(not any(sibling is unit for unit in units) for sibling in siblings[first_index:last_index + 1]):
            partial = True
    if partial:
        for node in selected:
            wrapper = soup.new_tag('a' if href else 'span')
            if href:
                wrapper['href'] = href
                wrapper['data-doc-web-reference'] = 'resolved'
            else:
                wrapper['data-doc-web-navigation-status'] = status
                wrapper['class'] = ['unresolved-reference']
            node.wrap(wrapper)
        return True
    wrapper = soup.new_tag('a' if href else 'span')
    if href:
        wrapper['href'] = href
        wrapper['data-doc-web-reference'] = 'resolved'
    else:
        wrapper['data-doc-web-navigation-status'] = status
        wrapper['class'] = ['unresolved-reference']
    units[0].insert_before(wrapper)
    for unit in units:
        wrapper.append(unit.extract())
    return True


def enrich(entries, soups, ids, source_pages, provenance_rows, *, source_soups=None):
    index = ReferenceIndex(entries, soups, ids, source_pages, provenance_rows, source_soups=source_soups)
    rows = []
    for path, soup in soups.items():
        blocks = [b for b in soup.find_all(BLOCKS) if not forbidden(b)]
        for block in blocks:
            text, nodes, spans = discover(block)
            # Recompute node map after each reverse mutation; offsets stay stable.
            for start, end, kind, label, is_range in reversed(spans):
                original = text[start:end]
                if start == 0 and any(t['path'] == path and t['id'] in {parent.get('id') for parent in [block, *block.parents] if parent.name} for t in index.lookup(kind, label)):
                    continue
                candidates = [] if kind == 'url' else index.lookup(kind, label)
                status, reason, target = 'missing', 'exact_target_unavailable', None
                href = None
                if is_range:
                    status, reason = 'ambiguous', 'unsupported_range'
                elif kind == 'url_blocked':
                    reason = 'excluded_inline_url_boundary'
                elif kind == 'url':
                    parsed, uri_error = parse_uri(label)
                    valid_url = parsed is not None and parsed.scheme.casefold() in {'http', 'https'}
                    if valid_url:
                        status, reason, href = 'resolved', 'literal_http_url', label
                        target = {'path': label, 'id': None, 'href': label, 'kind': 'url', 'evidence': {'literal_url': label}}
                    else:
                        reason = 'invalid_http_url'
                elif kind == 'page' and len(index.page_observations.get(label_key(label), [])) > 1:
                    status, reason = 'ambiguous', 'duplicate_observed_printed_labels'
                elif len(candidates) > 1:
                    status, reason = 'ambiguous', 'duplicate_exact_targets'
                elif len(candidates) == 1:
                    status, reason, target = 'resolved', 'unique_exact_source_target', dict(candidates[0])
                    href = href_for(path, target)
                    target['href'] = href
                elif kind == 'page' and index.rejected_pages.get(label_key(label)):
                    reason = index.rejected_pages[label_key(label)][0]
                source_tag = next((t for t in [block, *block.parents] if t.name and t.get('id')), block)
                block_id = source_tag.get('id')
                location = source_location(nodes, start, end, source_block_base(block, source_tag))
                row = {'path': path, 'block_id': block_id, 'anchor_text': original, 'original_text': original,
                       'status': status if status != 'missing' else 'unresolved', 'resolution_status': status,
                       'kind': kind, 'reason': reason, 'candidates': candidates, 'target': target, 'policy': POLICY_ID,
                       'source': {'path': path, 'block_id': block_id, 'location': location,
                                  'provenance': index.provenance.get((path, block_id), index.unscoped_provenance.get(block_id))}}
                if kind == 'page':
                    row['page_observations'] = index.page_observations.get(label_key(label), [])
                if href:
                    row['resolved_href'] = href
                rows.append(row)
                _, nodes = text_stream(block)
                if not wrap_range(soup, nodes, start, end, href, status):
                    row.update(status='unresolved', resolution_status='missing', reason='unsupported_inline_range', target=None)
                    row.pop('resolved_href', None)
    return rows
