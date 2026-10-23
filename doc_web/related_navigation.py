"""Offline exact symbol binding within an explicitly declared document set.

The caller owns membership and paths. This module owns conservative source and
heading evidence checks; it never infers membership, page offsets, or editions.
"""
import re
from collections import Counter, defaultdict

from bs4 import BeautifulSoup, CData, NavigableString

from doc_web.reference_resolution import (
    BLOCKS, DOCUMENT_SOURCE, HEADINGS, NUMBER, PREFIXED_LABEL, ReferenceScope, SKIP,
    canonical_kind, forbidden, href_for, label_key, source_block_base,
    scope_occurrences, source_location, text_stream, wrap_range,
)

POLICY_ID = 'exact-related-reference-v1'
_LABEL = '(?:' + PREFIXED_LABEL + '|' + NUMBER + ')'
_TYPED = r'chapters?(?=\s)|sections?(?=\s)|§|paragraphs?(?=\s)|¶|figures?(?=\s)|fig\.|tables?(?=\s)|footnotes?(?=\s)|notes?(?=\s)|pages?(?=\s)|pp?\.'
_EXPLICIT = re.compile(r'(?<!\w)(?P<kind>' + _TYPED + r')\s*(?P<label>' + _LABEL + r')(?P<range>\s*[-–—]\s*' + _LABEL + r')?(?!\w)(?!\.\w)', re.I)
_LEADING_TYPED = re.compile(r'^\s*(?P<kind>chapter|section|paragraph|figure|fig\.|table|footnote|note)\s+(?P<label>' + _LABEL + r')(?!\w)(?!\.\w)(?=\s|[.:)\-]|$)', re.I)
_LEADING_CODE = re.compile(r'^\s*(?P<label>' + PREFIXED_LABEL + r')(?!\w)(?!\.\w)(?=\s|[.:)]|$)', re.I)
_TRAILING_CODE = re.compile(r'\((?P<label>' + PREFIXED_LABEL + r')\)\s*:?\s*$', re.I)
_CODE = re.compile(r'(?<![\w.])(?P<label>' + PREFIXED_LABEL + r')(?!\w)(?!\.\w)(?P<range>\s*[-–—]\s*' + _LABEL + r'(?!\w)(?!\.\w))?', re.I)
_NAMED_SUFFIX = re.compile(r'^\s*[)\]]?\s+(?:of|in|from)\s+' + DOCUMENT_SOURCE, re.I)
_URI = re.compile(r'(?<![\w+.-])(?:[A-Za-z][A-Za-z0-9+.-]*://[^\s<>\"\u201c\u201d\x00]+|mailto:[^\s<>\"\x00]+)|(?<![\w@])[^\s<>\"@\x00]+@[^\s<>\"@\x00]+', re.I)
_TURN = re.compile(r'(?<!\w)(?:turn|return|go|refer)\s+to\s+(?:(?P<kind>paragraph)\s+)?(?P<label>' + _LABEL + r')(?P<range>\s*[-–—]\s*' + _LABEL + r')?(?!\w)(?!\.\w)', re.I)


def _normalized(value):
    return ' '.join(str(value or '').split())


def _raw_text(tag):
    # Same text coordinates as source_location, including opaque inline text.
    return ''.join(str(node) for node in tag.descendants
                   if type(node) in {NavigableString, CData})


def _quote_views(tag, end):
    """Exact producer text conventions, with raw-to-quote coverage mapping.

    Existing emitters may concatenate inline text or separate each text leaf
    before whitespace normalization. Both are verifiable DOM representations;
    neither permits matching only a citation substring.
    """
    raw = _raw_text(tag)
    leaves, prefix_leaves, consumed = [], [], 0
    for node in tag.descendants:
        if type(node) not in {NavigableString, CData}:
            continue
        value = str(node)
        if value.strip():
            leaves.append(value.strip())
        covered = value[:max(0, min(len(value), end - consumed))]
        if covered.strip():
            prefix_leaves.append(covered.strip())
        consumed += len(value)
    return [(_normalized(raw), _normalized(raw[:end])),
            (_normalized(' '.join(leaves)), _normalized(' '.join(prefix_leaves)))]


def _extra_excluded(tag):
    return any(parent.name == 'nav' or parent.get('aria-hidden') == 'true'
               or parent.has_attr('data-doc-web-generated')
               or parent.has_attr('data-generated')
               or parent.has_attr('data-doc-web-navigation')
               or re.search(r'(?:display\s*:\s*none|visibility\s*:\s*hidden)', parent.get('style', ''), re.I)
               for parent in [tag, *tag.parents] if parent.name)


def _excluded(tag):
    return forbidden(tag) or _extra_excluded(tag)


def _stream(block):
    text, slots = text_stream(block)
    pieces = list(text)
    for node, start, end, editable, *_ in slots:
        if editable and _excluded(node.parent):
            pieces[start:end] = '\x00' * (end - start)
    return ''.join(pieces), slots


def _semantic_stream(block, edit_text, slots):
    """Visible anchors supply scope evidence without granting edit permission.

    Slot widths come from the shared DOM helper, so all citation coordinates
    remain identical. Code, hidden/generated text and nested block boundaries
    remain opaque. Anchor contents are restored only in this read-only view.
    """
    pieces = list(edit_text)
    for node, start, end, editable, *_ in slots:
        if editable or type(node) not in {NavigableString, CData}:
            continue
        owner = next((p for p in node.parents if p.name in BLOCKS), None)
        parents = [p for p in node.parents if p.name]
        if (owner is not block or _extra_excluded(node.parent)
                or any(p.name in (SKIP - {'a'}) | HEADINGS
                       or p.has_attr('hidden')
                       or p.has_attr('data-doc-web-navigation-status')
                       or p.get('role') == 'navigation' for p in parents)):
            continue
        if any(p.name == 'a' for p in parents):
            pieces[start:end] = str(node)
    return ''.join(pieces)


class _SetScope(ReferenceScope):
    """Apply set citation forms through the shared attached/list scope grammar."""
    @staticmethod
    def occurrences(text):
        return scope_occurrences(text, typed_patterns=(_EXPLICIT, _TURN),
                                 prefixed_pattern=_CODE)

    def __init__(self, text):
        super().__init__(text)
        groups = []
        for ordinal, (start, end, reason) in enumerate(self.groups):
            next_start = self.groups[ordinal + 1][0] if ordinal + 1 < len(self.groups) else len(text)
            suffix = text[end:next_start].split('\x00', 1)[0]
            if reason is None and _NAMED_SUFFIX.match(suffix):
                reason = 'unestablished_document_scope'
            groups.append((start, end, reason))
        self.groups = groups


def _heading_symbols(text):
    """Only source-authored identifier positions establish target authority."""
    symbols = []
    typed = _LEADING_TYPED.search(text)
    if typed:
        symbols.append((canonical_kind(typed['kind']), typed['label']))
    for pattern in (_LEADING_CODE, _TRAILING_CODE):
        match = pattern.search(text)
        if match:
            symbol = ('numbered_location', match['label'])
            if not any(label_key(label) == label_key(symbol[1])
                       for kind, label in symbols):
                symbols.append(symbol)
    return symbols


def _discover(text, semantic_text=None):
    spans = []
    for match in _EXPLICIT.finditer(text):
        spans.append((match.start(), match.end(), canonical_kind(match['kind']), match['label'], bool(match['range'])))
    for match in _TURN.finditer(text):
        spans.append((match.start(), match.end(), 'paragraph' if match['kind'] else 'numbered_location', match['label'], bool(match['range'])))
    for match in _CODE.finditer(text):
        spans.append((match.start(), match.end(), 'numbered_location', match['label'], bool(match['range'])))
    urls = [(match.start(), match.end())
            for match in _URI.finditer(text if semantic_text is None else semantic_text)]
    selected = []
    for span in sorted(spans, key=lambda s: (-(s[1] - s[0]), s[0])):
        if not any(a < span[1] and span[0] < b for a, b in urls + [(s[0], s[1]) for s in selected]):
            selected.append(span)
    return sorted(selected)


def _source_evidence(source_tag, rows, ids, location):
    """A 400-character quote authorizes only its own occurrence positions."""
    if not source_tag.get('id'):
        return None, 'missing_source_block_id'
    if ids[source_tag['id']] != 1:
        return None, 'duplicate_source_dom_id'
    if len(rows) != 1:
        return None, 'duplicate_source_provenance' if rows else 'missing_source_provenance'
    row = rows[0]
    if not row.get('source_element_ids'):
        return row, 'missing_source_element_ids'
    quote = row.get('text_quote')
    normalized_quote = _normalized(quote)
    if not normalized_quote:
        return row, 'source_quote_mismatch'
    views = _quote_views(source_tag, location['end'])
    if any(normalized_quote == full for full, _ in views):
        return row, None
    # Producers store collapse_text(block.text)[:400]. Do not accept arbitrary
    # short prefixes or a quote that matches only the individual citation.
    matching_prefixes = [covered for full, covered in views
                         if len(str(quote)) == 400 and str(quote) == full[:400]]
    if not matching_prefixes:
        return row, 'source_quote_mismatch'
    if not any(len(covered) <= len(normalized_quote) for covered in matching_prefixes):
        return row, 'insufficient_source_evidence'
    return row, None


def resolve_related_entries(members: list[dict]) -> dict:
    """Mutate only eligible entry HTML; return a complete, JSON-safe inventory.

    All filenames are set-relative. Existing anchors, including previous set
    links, stay opaque. Repeated calls therefore make no further DOM changes.
    Rejected heading candidates remain lookup evidence and block guessing.
    """
    contexts, inventory = [], []
    target_index = defaultdict(list)
    editions = {_normalized(m.get('edition')).casefold() for m in members
                if _normalized(m.get('edition'))}
    edition_conflict = len(editions) > 1
    for member in members:
        provenance = defaultdict(list)
        for row in member.get('provenance_rows', []):
            provenance[(row.get('entry_id'), row.get('block_id'))].append(row)
        for entry in member.get('entries', []):
            soup = BeautifulSoup(entry['body_html'], 'html.parser')
            # The local resolver annotates abstentions with generated spans.
            # Reconsider those texts under the new, caller-declared set scope.
            # Leave IDs and inline structure intact while removing only its
            # known status annotation; existing anchors stay opaque.
            for span in soup.find_all('span', attrs={'data-doc-web-navigation-status': True}):
                if ('unresolved-reference' in span.get('class', [])
                        and span['data-doc-web-navigation-status'] in {'missing', 'ambiguous', 'unresolved'}):
                    del span['data-doc-web-navigation-status']
                    classes = [c for c in span.get('class', []) if c != 'unresolved-reference']
                    if classes:
                        span['class'] = classes
                    else:
                        span.attrs.pop('class', None)
            ids = Counter(str(tag['id']) for tag in soup.find_all(id=True))
            contexts.append((member, entry, soup, ids, provenance))
            for heading in soup.find_all(HEADINGS):
                raw_heading = _normalized(_raw_text(heading))
                text = _normalized(heading.get_text(' ', strip=True))
                for kind, label in _heading_symbols(raw_heading):
                    rows = provenance.get((entry.get('entry_id'), heading.get('id')), [])
                    reason = None
                    if _excluded(heading):
                        reason = 'excluded_heading'
                    elif not heading.get('id'):
                        reason = 'missing_heading_dom_id'
                    elif ids[heading['id']] != 1:
                        reason = 'duplicate_heading_dom_id'
                    elif len(rows) != 1:
                        reason = 'duplicate_heading_provenance' if rows else 'missing_heading_provenance'
                    elif rows[0].get('block_kind') != 'heading':
                        reason = 'non_heading_provenance'
                    elif not rows[0].get('source_element_ids'):
                        reason = 'missing_heading_element_ids'
                    elif _normalized(rows[0].get('text_quote')) not in {raw_heading, text}:
                        reason = 'heading_quote_mismatch'
                    target = {'member_id': member['member_id'], 'document_id': member['document_id'],
                              'path': entry['filename'], 'id': heading.get('id'),
                              'heading': text, 'label': label, 'kind': kind,
                              'eligible': reason is None, 'rejection_reason': reason,
                              'evidence': {'heading_text': text, 'provenance': rows[0] if len(rows) == 1 else None,
                                           'provenance_rows': list(rows), 'dom_id_count': ids[heading.get('id')]}}
                    inventory.append(target)
                    target_index[label_key(label)].append(target)
    references = []
    for member, entry, soup, ids, provenance in contexts:
        changed = False
        for block in soup.find_all(BLOCKS):
            if _excluded(block):
                continue
            text, slots = _stream(block)
            semantic_text = _semantic_stream(block, text, slots)
            scope = _SetScope(semantic_text)
            for start, end, kind, label, is_range in reversed(_discover(text, semantic_text)):
                label_candidates = target_index.get(label_key(label), [])
                candidates = [t for t in label_candidates
                              if t['kind'] == kind or kind == 'numbered_location'
                              or (t['kind'] == 'numbered_location' and kind in {'section', 'paragraph'})]
                source_tag = next((t for t in [block, *block.parents] if t.name and t.get('id')), block)
                location = source_location(slots, start, end, source_block_base(block, source_tag))
                source_rows = provenance.get((entry.get('entry_id'), source_tag.get('id')), [])
                source_row, source_reason = _source_evidence(source_tag, source_rows, ids, location)
                status, reason, target = 'missing', 'exact_target_unavailable', None
                scope_reason = scope.reason(start, end)
                if scope_reason:
                    reason = scope_reason
                elif re.search(r'\beditions?\b', semantic_text, re.I):
                    reason = 'textual_edition_scope'
                elif is_range:
                    status, reason = 'ambiguous', 'unsupported_range'
                elif kind == 'page':
                    reason = 'unsupported_page_scope'
                elif source_reason:
                    reason = source_reason
                elif len(candidates) > 1:
                    status, reason = 'ambiguous', 'duplicate_exact_targets'
                elif len(candidates) == 1:
                    candidate = candidates[0]
                    if not candidate['eligible']:
                        reason = candidate['rejection_reason']
                    elif edition_conflict and candidate['member_id'] != member['member_id']:
                        reason = 'edition_conflict'
                    else:
                        status, reason = 'resolved', 'unique_exact_source_target'
                        target = dict(candidate, href=href_for(entry['filename'], candidate))
                elif label_candidates:
                    reason = 'target_kind_mismatch'
                row = {'original_text': text[start:end], 'label': label, 'kind': kind,
                       'status': status, 'reason': reason,
                       'source': {'member_id': member['member_id'], 'path': entry['filename'],
                                  'block_id': source_tag.get('id'), 'location': location,
                                  'provenance': source_row, 'provenance_rows': list(source_rows)},
                       'candidates': candidates, 'target': target}
                if target:
                    _, current_slots = _stream(block)
                    if wrap_range(soup, current_slots, start, end, target['href']):
                        changed = True
                    else:
                        row.update(status='missing', reason='unsupported_inline_range', target=None)
                references.append(row)
        if changed:
            entry['body_html'] = str(soup)
    references.sort(key=lambda r: (r['source']['path'], r['source']['block_id'] or '', r['source']['location']['start']))
    return {'policy': {'id': POLICY_ID, 'edition_conflict': edition_conflict,
                       'source_quote_limit': 400, 'unsupported_pages': True,
                       'edition_mentions': 'visible_block_level_hold',
                       'scope_context': 'visible_anchors_read_only',
                       'named_postfix_document_scope': 'hold',
                       'uri_text': 'opaque',
                       'untyped_heading_aliases': ['section', 'paragraph']},
            'scope': 'declared_related_document_set',
            'references': references, 'targets': inventory,
            'summary': dict(Counter(r['status'] for r in references)),
            'api_calls': 0, 'cost_usd': 0}
