"""Deferred, source-supported manual references within one document build.

A build's entries are the document/edition boundary. Exact heading wording and
leading heading tokens are evidence; fuzzy matches and inferred numbers are not.
"""
import posixpath
import re
import time
from collections import Counter
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

from bs4 import BeautifulSoup, NavigableString

from doc_web.reference_resolution import NUMBER, PREFIXED_LABEL, parse_uri


def _text(tag):
    return ' '.join(tag.get_text(' ', strip=True).split())


def _local(href, current):
    parsed, error = parse_uri(href)
    if error:
        return current, '', error
    if parsed.scheme or parsed.netloc:
        return None
    path = unquote(parsed.path)
    target = posixpath.normpath(posixpath.join(posixpath.dirname(current), path)) if path else current
    if path.startswith('/') or target == '..' or target.startswith('../'):
        return target, unquote(parsed.fragment), 'outside_document'
    return target, unquote(parsed.fragment), None


def _tokens(heading):
    text = _text(heading)
    if not text:
        return set()
    first = text.split()[0]
    # A complete heading or explicit leading identifier is evidence; an
    # ordinary first word cannot authorize a prose reference destination.
    identifier = first.rstrip('.:)').lstrip('(')
    return {text, identifier} if re.fullmatch(f'(?:{NUMBER}|{PREFIXED_LABEL})', identifier, re.I) else {text}


def _contains(label, token):
    # Prefix and number remain one source-derived identity. Case folding is
    # confined to identifiers; ordinary heading wording remains literal.
    if re.fullmatch(PREFIXED_LABEL, token):
        return bool(re.search(r'(?<![\w.])' + re.escape(token) + r'(?!\w|\.\w)', label, re.I))
    # Full heading wording still begins with the same complete identifier.
    # Its literal title cannot turn a suffix of another dotted ID into proof.
    first = token.split()[0].rstrip('.:)').lstrip('(') if token else ''
    if re.fullmatch(PREFIXED_LABEL, first):
        return bool(re.search(r'(?<![\w.])' + re.escape(token) + r'(?!\w)', label))
    return bool(re.search(r'(?<!\w)' + re.escape(token) + r'(?!\w)', label))


def _anchor_scope_reason(anchor, context_cache=None):
    """Freeze visible block text and all occurrence offsets once per call."""
    from doc_web.reference_resolution import BLOCKS, SKIP, STRUCTURAL, ReferenceScope, stream_nodes

    block = next((parent for parent in anchor.parents if parent.name in BLOCKS | STRUCTURAL), anchor)
    cache = context_cache if context_cache is not None else {}
    cached = cache.get(id(block))
    if cached is not None:
        _, scope, offsets = cached
        occurrence = offsets.get(id(anchor))
        return scope.reason(*occurrence) if occurrence else None
    parts, width, offsets = [], 0, {}
    skipped = SKIP - {'a'}

    def excluded(tag):
        return any(parent.name in skipped or parent.has_attr('hidden')
                   or parent.get('role') == 'navigation' for parent in [tag, *tag.parents] if parent.name)

    def barrier():
        nonlocal width
        parts.append('\x00')
        width += 1

    # Reuse discovery's enter/exit structural boundaries. Skipped content is
    # opaque, including empty elements, rather than absent from the sentence.
    # Anchors remain readable so repeated occurrences retain exact coordinates.
    for node in stream_nodes(block):
        if node is None:
            barrier()
            continue
        if not isinstance(node, NavigableString):
            if node.name and excluded(node):
                barrier()
            continue
        if type(node) is not NavigableString or excluded(node.parent):
            barrier()
            continue
        value = str(node)
        for parent in node.parents:
            if parent.name == 'a':
                start = offsets.get(id(parent), (width, width))[0]
                offsets[id(parent)] = (start, width + len(value))
        parts.append(value)
        width += len(value)
    scope = ReferenceScope(''.join(parts))
    cache[id(block)] = (block, scope, offsets)
    occurrence = offsets.get(id(anchor))
    return scope.reason(*occurrence) if occurrence else None



def _heading_candidates(label, headings):
    from doc_web.reference_resolution import EXPLICIT, TARGET, canonical_kind, label_key

    explicit_matches = list(EXPLICIT.finditer(label))
    explicit = explicit_matches[0] if len(explicit_matches) == 1 else None
    plurals = {'pages', 'pp.', 'chapters', 'sections', 'paragraphs', 'figures', 'tables', 'footnotes', 'notes'}
    ambiguous = len(explicit_matches) > 1 or bool(explicit and (explicit['range'] or explicit['kind'].casefold() in plurals))
    if ambiguous:
        return [], True
    if explicit:
        candidates = [h for h in headings if (match := TARGET.match(h['heading']))
                      and canonical_kind(match[1]) == canonical_kind(explicit['kind'])
                      and label_key(match[2]) == label_key(explicit['label'])]
    else:
        candidates = [h for h in headings if any(_contains(label, token) for token in h['tokens'])]
    # A bare identifier denotes its identity, even when one heading consists
    # solely of that identifier. A duplicate titled heading remains ambiguous.
    if re.fullmatch(PREFIXED_LABEL, label):
        return candidates, False
    exact = [h for h in candidates if label == h['heading']]
    return exact or candidates, False


def _toc_row(anchor):
    """A complete title cell adjacent to one authored destination cell."""
    row = anchor.find_parent('tr')
    if row is None:
        return None
    cells = row.find_all(['td', 'th'], recursive=False)
    if (len(cells) != 2 or anchor.find_parent(['td', 'th']) is not cells[1]
            or cells[0].find(['a', 'table']) or cells[1].find('table')
            or len(cells[1].find_all('a')) != 1 or _text(cells[1]) != _text(anchor)):
        return None
    title, label = _text(cells[0]), _text(anchor)
    if not title or not re.fullmatch(r'\d+|[ivxlcdm]+', label, re.I):
        return None
    return row, title, label


class _TocNavigation:
    """Source-row occurrence and heading/page joins shared by both passes.

    Capitalization equivalence applies only to full titles in this contract.
    Raw observed print labels corroborate titles; inferred labels never do.
    """
    def __init__(self, entries, soups, ids, source_pages, provenance_rows, source_soups=None):
        from doc_web.reference_resolution import identity_matches, label_key, raw_page_identity

        self.ids, self.identity_matches, self.label_key = ids, identity_matches, label_key
        self.provenance = {(r.get('html_path'), r['block_id']): r
                           for r in provenance_rows if r.get('block_id')}
        self.rows, self.final_counts, self.headings = {}, {}, []
        self.final_counts = {path: Counter((shape[1], shape[2]) for a in soup.find_all('a', href=True)
                                          if (shape := _toc_row(a))) for path, soup in soups.items()}
        if not any(self.final_counts.values()):
            return
        source_soups = {} if source_soups is None else source_soups
        raw_pages = list(source_pages) or [p for e in entries for p in e.get('prepared_pages', [])]
        self.observed = {}
        for page in {raw_page_identity(p): p for p in raw_pages}.values():
            label = page.get('printed_page_number_text')
            if label is None:
                label = page.get('printed_page_number')
            if (label is not None and not page.get('printed_page_number_inferred')
                    and re.fullmatch(r'\d+|[ivxlcdm]+', str(label).strip(), re.I)):
                self.observed.setdefault(label_key(label), []).append(page)
        for entry in entries:
            path = entry['filename']
            if path not in soups:
                continue
            sources = []
            # Identical repeated prepared-page descriptors are one source page.
            pages = {raw_page_identity(p): p for p in entry.get('prepared_pages', [])}
            for page in pages.values():
                source_html = page.get('html') or ''
                if source_html not in source_soups:
                    source_soups[source_html] = BeautifulSoup(source_html, 'html.parser')
                source = source_soups[source_html]
                sources.append((page, {_text(h) for h in source.find_all(re.compile(r'^h[1-6]$'))}))
                for anchor in source.find_all('a', href=True):
                    shape = _toc_row(anchor)
                    if shape:
                        _, title, label = shape
                        self.rows.setdefault((path, title, label), []).append((page, anchor['href']))
            for tag in soups[path].find_all(re.compile(r'^h[1-6]$'), id=True):
                if ids[path][tag['id']] != 1:
                    continue
                provenance = self.row_provenance(path, tag)
                proven = [(page, titles) for page, titles in sources
                          if provenance and str(provenance.get('source_page_number')) == str(page.get('page_number', page.get('page')))
                          and identity_matches(provenance, page) and _text(tag) in titles]
                if len(proven) == 1:
                    self.headings.append({'path': path, 'id': tag['id'], 'heading': _text(tag), 'page': proven[0][0]})

    def row_provenance(self, path, tag):
        for parent in [tag, *tag.parents]:
            if parent.get('id'):
                found = self.provenance.get((path, parent['id']), self.provenance.get((None, parent['id'])))
                if found:
                    return found
        return None

    def decision(self, path, anchor):
        from doc_web.reference_resolution import ReferenceScope, raw_page_identity

        shape = _toc_row(anchor)
        if not shape:
            return None
        row, title, label = shape
        sources = self.rows.get((path, title, label), [])
        if not sources:
            return None
        evidence = {'source_title': title, 'source_page_label': label,
                    'title_comparison': 'whole_title_case_equivalent', 'printed_page_authority': False}
        result = {'candidates': [], 'toc_evidence': evidence}

        def hold(reason, ambiguous=False):
            return {**result, 'reason': reason, 'status': 'ambiguous' if ambiguous else 'unresolved'}

        provenance = self.row_provenance(path, row)
        if not provenance:
            return hold('toc_source_row_provenance_unavailable')
        sources = [(page, href) for page, href in sources
                   if str(provenance.get('source_page_number')) == str(page.get('page_number', page.get('page')))
                   and self.identity_matches(provenance, page)]
        if len(sources) != 1 or self.final_counts[path][(title, label)] != 1:
            return hold('toc_source_row_occurrence_ambiguous', True)
        page, source_href = sources[0]
        local = _local(source_href, path)
        if local is None or local[2] or local[0] not in self.ids:
            return hold('toc_source_destination_outside_document')
        scope_text = title + ' page ' + label
        scope_reason = ReferenceScope(scope_text).reason(len(title) + 1, len(scope_text))
        if scope_reason:
            return hold(scope_reason)
        evidence.update(source_href=source_href, source_row_page_number=page.get('page_number', page.get('page')))
        candidates = [h for h in self.headings if h['heading'].casefold() == title.casefold()]
        observations = self.observed.get(self.label_key(label), [])
        evidence['page_observations'] = [{k: p.get(k) for k in ('page_number', 'original_page_number', 'spread_side', 'printed_page_number_text', 'printed_page_number')} for p in observations]
        if len(observations) > 1:
            return hold('duplicate_observed_printed_labels', True)
        if observations:
            evidence['printed_page_authority'] = True
            identity = raw_page_identity(observations[0])
            candidates = [h for h in candidates if raw_page_identity(h['page']) == identity]
            reason = 'toc_title_printed_page_conflict' if not candidates else 'unique_source_toc_title_and_page'
        else:
            reason = 'unique_source_toc_heading' if candidates else 'toc_unique_heading_unavailable'
        result['candidates'] = [{k: h[k] for k in ('path', 'id', 'heading')} for h in candidates]
        if len(candidates) != 1:
            return hold('toc_duplicate_heading_targets' if len(candidates) > 1 else reason, len(candidates) > 1)
        if not observations:
            target_page = candidates[0]['page']
            target_label = target_page.get('printed_page_number_text')
            if target_label is None:
                target_label = target_page.get('printed_page_number')
            if (target_label is not None and not target_page.get('printed_page_number_inferred')
                    and re.fullmatch(r'\d+|[ivxlcdm]+', str(target_label).strip(), re.I)
                    and self.label_key(target_label) != self.label_key(label)):
                return hold('toc_title_printed_page_conflict')
        return {**result, 'status': 'resolved', 'reason': reason}


def resolve_navigation(entries, *, bundle_root=None, resource_catalog=None,
                       resolve_references=False, source_pages=(), provenance_rows=()):
    """Mutate only link attributes/tags after final IDs, returning a full audit."""
    started = time.perf_counter()
    entries = list(entries)
    soups = {entry['filename']: BeautifulSoup(entry['body_html'], 'html.parser') for entry in entries}
    ids = {path: Counter(tag['id'] for tag in soup.find_all(id=True)) for path, soup in soups.items()}
    aliases = {entry['filename']: entry.get('_navigation_id_aliases', {}) for entry in entries}
    source_headings = {entry['filename']: set() for entry in entries}
    source_links = set()
    source_soups = {}
    for entry in entries:
        for page in entry.get('prepared_pages', []):
            source_html = page.get('html') or ''
            if source_soups is not None and source_html in source_soups:
                soup = source_soups[source_html]
            else:
                soup = BeautifulSoup(source_html, 'html.parser')
                if source_soups is not None:
                    source_soups[source_html] = soup
            source_headings[entry['filename']].update(_text(tag) for tag in soup.find_all(re.compile(r'^h[1-6]$')))
            source_links.update((entry['filename'], a.get('href'), _text(a)) for a in soup.find_all('a', href=True))
    toc = _TocNavigation(entries, soups, ids, source_pages, provenance_rows, source_soups)
    headings = []
    for path, soup in soups.items():
        for tag in soup.find_all(re.compile(r'^h[1-6]$'), id=True):
            if _text(tag) in source_headings[path]:
                headings.append({'path': path, 'id': tag['id'], 'heading': _text(tag), 'tokens': _tokens(tag)})
    base = Path(bundle_root).resolve() if bundle_root is not None else None
    catalog = set(resource_catalog) if resource_catalog is not None else None
    rows = []
    scope_contexts = {}
    entry_by_path = {entry['filename']: entry for entry in entries}
    for path, soup in soups.items():
        previous_receipts = entry_by_path[path].get('_navigation_alias_receipts', {})
        receipts = {}
        entry_by_path[path]['_navigation_alias_receipts'] = receipts
        receipt_counts = Counter(a.get('data-doc-web-alias-receipt') for a in soup.find_all('a', href=True))
        for ordinal, anchor in enumerate(soup.find_all('a'), 1):
            if not anchor.has_attr('href'):
                continue
            before, label = anchor['href'], _text(anchor)
            receipt_key = anchor.attrs.pop('data-doc-web-alias-receipt', None)
            original_alias_href = anchor.attrs.pop('data-doc-web-original-alias-href', None)
            prior = previous_receipts.get(receipt_key)
            if not (prior and receipt_counts[receipt_key] == 1 and prior.get('final_anchor_ordinal') == ordinal
                    and all(prior.get(key) == value for key, value in {'original_href': original_alias_href, 'href': before, 'label': label}.items())
                    and (path, original_alias_href, label) in source_links):
                receipt_key, original_alias_href = None, None
            lookup_href = original_alias_href or before
            local = _local(lookup_href, path)
            if local is None:
                parsed = urlsplit(before)
                if parsed.scheme.casefold() in {'http', 'https'}:
                    rows.append({'path': path, 'anchor_ordinal': ordinal, 'anchor_text': label,
                                 'original_href': before, 'block_id': next((tag.get('id') for tag in [anchor, *anchor.parents] if tag.get('id')), None),
                                 'status': 'preserved', 'reason': 'external_http_url'})
                continue
            target_path, fragment, error = local
            valid = not error and target_path in ids and (not fragment or ids[target_path][fragment] == 1)
            row = {'path': path, 'anchor_ordinal': ordinal, 'anchor_text': label, 'original_href': before,
                   'block_id': next((tag.get('id') for tag in [anchor, *anchor.parents] if tag.get('id')), None)}
            # Fragment semantics belong to the target media type, not the
            # anchor tag. Preserve included downloads/images without treating
            # their labels or fragments as chapter-heading instructions.
            resource_exists = target_path in catalog if catalog is not None else None
            if base is not None:
                resource = (base / target_path).resolve()
                resource_exists = resource.is_relative_to(base) and resource.is_file()
            is_chapter_reference = target_path in ids or not error and not urlsplit(before).path
            is_html_path = Path(target_path).suffix.casefold() in {'.html', '.htm', '.xhtml'}
            if not is_chapter_reference and (not is_html_path or resource_exists):
                row.update(status='preserved' if resource_exists is not False and not error else 'unresolved',
                           reason=error or ('included_resource' if resource_exists else 'resource_existence_unmeasured' if resource_exists is None else 'missing_resource'),
                           resource_exists=resource_exists,
                           fragment_status='unmeasured_media_fragment' if fragment and not is_html_path else 'not_applicable')
                rows.append(row)
                continue
            # A known chapter remains within this document/edition scope.
            # Unknown files cannot borrow a similarly named heading here.
            explicit_path = bool(urlsplit(lookup_href).path) if not error else True
            eligible_headings = headings if not explicit_path or target_path in ids else []
            scope_reason = _anchor_scope_reason(anchor, scope_contexts)
            # A fragment or original-ID alias cannot establish that an
            # expressly different document is this build's document.
            error = error or scope_reason
            valid = valid and not scope_reason
            supported = (path, before, label) in source_links
            alias_supported = (path, lookup_href, label) in source_links
            mapped = aliases.get(target_path, {}).get(fragment, [])
            if not explicit_path and not mapped and not valid and fragment:
                global_aliases = [(alias_path, identifier) for alias_path, alias_map in aliases.items()
                                  for identifier in alias_map.get(fragment, [])
                                  if ids.get(alias_path, {}).get(identifier, 0) == 1]
                if len(global_aliases) == 1:
                    target_path, identifier = global_aliases[0]
                    mapped = [identifier]
                elif len(global_aliases) > 1:
                    mapped = [identifier for _, identifier in global_aliases]
                    row['alias_candidates'] = [{'path': alias_path, 'id': identifier} for alias_path, identifier in global_aliases]
            original_id_authority = (not error and alias_supported and len(mapped) == 1
                                     and ids.get(target_path, {}).get(mapped[0], 0) == 1)
            # A numeric label in an ordinary table may be a quantity linked to
            # a note. Its exact authored ID remains stronger evidence than a
            # title/page interpretation of the surrounding cells.
            toc_decision = None if original_id_authority else toc.decision(path, anchor)
            if toc_decision is not None:
                row.update(toc_decision)
                if error:
                    row.update(status='unresolved', reason=error)
                if row['status'] == 'resolved':
                    chosen = row['candidates'][0]
                    relative = '' if chosen['path'] == path else posixpath.relpath(chosen['path'], posixpath.dirname(path) or '.')
                    rebound = quote(relative, safe='/') + '#' + quote(chosen['id'], safe='-._~')
                    if valid and (target_path, fragment) == (chosen['path'], chosen['id']):
                        row['status'] = 'preserved'
                    else:
                        anchor['href'] = rebound
                        row['resolved_href'] = rebound
                    row['heading'] = chosen['heading']
                else:
                    anchor.name = 'span'
                    del anchor['href']
                    anchor['data-doc-web-navigation-status'] = row['status']
                    anchor['data-doc-web-original-href'] = before
                    anchor['title'] = f"{row['status'].capitalize()} source reference: {before}"
                    anchor['class'] = list(anchor.get('class', [])) + ['unresolved-reference']
                rows.append(row)
                continue
            candidates, typed_ambiguous = _heading_candidates(label, eligible_headings) if not scope_reason else ([], False)
            semantic_candidates = candidates
            if len(candidates) > 1 and explicit_path:
                candidates = [h for h in candidates if h['path'] == target_path]
            agrees = any(h['path'] == target_path and h['id'] == fragment for h in candidates)
            if supported and len(semantic_candidates) > 1:
                row.update(semantic_status='semantic_label_ambiguity',
                           semantic_candidates=[{k: h[k] for k in ('path', 'id', 'heading')} for h in semantic_candidates])
            if original_id_authority:
                relative = '' if target_path == path else posixpath.relpath(target_path, posixpath.dirname(path) or '.')
                rebound = quote(relative, safe='/') + '#' + quote(mapped[0], safe='-._~')
                if before == rebound:
                    row.update(status='preserved', reason='original_id_authority')
                else:
                    anchor['href'] = rebound
                    row.update(status='resolved', resolved_href=rebound, reason='original_id_rebound')
                receipt_key = receipt_key or str(ordinal)
                anchor['data-doc-web-alias-receipt'] = receipt_key
                anchor['data-doc-web-original-alias-href'] = lookup_href
                receipts[receipt_key] = {'original_href': lookup_href, 'href': anchor['href'], 'label': label}
            elif valid and (not fragment or not candidates or agrees or not supported):
                row['status'] = 'preserved'
            elif not error and supported and len(candidates) == 1 and ids[candidates[0]['path']][candidates[0]['id']] == 1:
                chosen = candidates[0]
                relative = '' if chosen['path'] == path else posixpath.relpath(chosen['path'], posixpath.dirname(path) or '.')
                anchor['href'] = quote(relative, safe='/') + '#' + quote(chosen['id'], safe='-._~')
                row.update(status='resolved', resolved_href=anchor['href'], heading=chosen['heading'])
            elif not error and alias_supported and not valid and len(mapped) == 1 and ids[target_path][mapped[0]] == 1 and (
                not candidates or any(h['path'] == target_path and h['id'] == mapped[0] for h in candidates)
            ):
                relative = '' if target_path == path else posixpath.relpath(target_path, posixpath.dirname(path) or '.')
                anchor['href'] = quote(relative, safe='/') + '#' + quote(mapped[0], safe='-._~')
                row.update(status='resolved', resolved_href=anchor['href'], reason='original_id_rebound')
            else:
                status = 'ambiguous' if typed_ambiguous or len(candidates) > 1 or len(mapped) > 1 or ids.get(target_path, {}).get(fragment, 0) > 1 else 'unresolved'
                row.update(status=status, reason=error or scope_reason or ('ambiguous_typed_reference' if typed_ambiguous else 'source_reference_unavailable' if not supported else 'unique_heading_unavailable'),
                           candidates=[{k: h[k] for k in ('path', 'id', 'heading')} for h in candidates])
                anchor.name = 'span'
                del anchor['href']
                anchor['data-doc-web-navigation-status'] = status
                anchor['data-doc-web-original-href'] = before
                anchor['title'] = f'{status.capitalize()} source reference: {before}'
                anchor['class'] = list(anchor.get('class', [])) + ['unresolved-reference']
            rows.append(row)
    from doc_web.reference_resolution import POLICY_ID, enrich
    provenance = {(r.get('html_path'), r['block_id']): r for r in provenance_rows if r.get('block_id')}
    for row in rows:
        row.setdefault('reason', 'target_exists' if row['status'] == 'preserved' else 'unique_source_target')
        row['resolution_status'] = {'preserved': 'resolved', 'resolved': 'resolved', 'ambiguous': 'ambiguous'}.get(row['status'], 'missing')
        row['original_text'] = row['anchor_text']
        row['source'] = {'path': row['path'], 'block_id': row.get('block_id'), 'location': None,
                         'provenance': provenance.get((row['path'], row.get('block_id')), provenance.get((None, row.get('block_id'))))}
        row['policy'] = POLICY_ID
        row.setdefault('candidates', [])
        row['target'] = None
        if row['resolution_status'] == 'resolved':
            href = row.get('resolved_href', row['original_href'])
            local = _local(href, row['path'])
            row['target'] = {'path': local[0] if local else href, 'id': (local[1] or None) if local else None, 'href': href,
                             'kind': 'existing_link', 'evidence': {'original_href': row['original_href'], 'reason': row.get('reason', row['status'])}}
            if row.get('toc_evidence'):
                row['target']['kind'] = 'toc_heading'
                row['target']['evidence'].update(row['toc_evidence'])
    if resolve_references:
        rows.extend(enrich(entries, soups, ids, source_pages, provenance_rows, source_soups=source_soups))
    for entry in entries:
        for ordinal, anchor in enumerate(soups[entry['filename']].find_all('a'), 1):
            key = anchor.get('data-doc-web-alias-receipt')
            if key in entry['_navigation_alias_receipts']:
                entry['_navigation_alias_receipts'][key]['final_anchor_ordinal'] = ordinal
        entry['body_html'] = soups[entry['filename']].decode_contents()
    return {'schema_version': 'manual_navigation_resolution_v1', 'scope': 'single_document_build',
            'summary': dict(Counter(row['status'] for row in rows)), 'references': rows,
            'semantic_observations': [row for row in rows if row.get('semantic_status')],
            'resolution_summary': dict(Counter(row['resolution_status'] for row in rows)),
            'policy': {'id': POLICY_ID, 'printed_pages': 'observed_labels_only', 'scope': 'single_document_build',
                       'fuzzy_matching': False, 'resolve_references': bool(resolve_references)},
            'timing': {'elapsed_ms': (time.perf_counter() - started) * 1000}, 'api_calls': 0, 'cost_usd': 0}



def inspect_navigation(html_files, *, source_pages=(), source_entries=(), provenance_rows=(), resource_observations=None, semantic_observations=None):
    """Validate actual exported local anchors and collect visible abstentions."""
    files = [Path(path) for path in html_files]
    roots = {path.parent.resolve() for path in files}
    for root in list(roots):
        index = root / 'index.html'
        if index.exists() and index not in files:
            files.append(index)
    soups = {path.resolve(): BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser') for path in files if path.exists()}
    ids = {path: Counter(tag['id'] for tag in soup.find_all(id=True)) for path, soup in soups.items()}
    source_entries = list(source_entries)
    toc_soups = {name: soup for path, soup in soups.items() for name in [next((e['filename'] for e in source_entries
                 if any((root / e['filename']).resolve() == path for root in roots)), None)] if name is not None}
    toc_ids = {name: Counter(tag['id'] for tag in soup.find_all(id=True)) for name, soup in toc_soups.items()}
    toc = _TocNavigation(source_entries, toc_soups, toc_ids, source_pages, provenance_rows)
    source_headings, source_labels = set(), set()
    for page in source_pages:
        source = BeautifulSoup(page.get('html') or '', 'html.parser')
        source_headings.update(_text(tag) for tag in source.find_all(re.compile(r'^h[1-6]$')))
        source_labels.update(_text(tag) for tag in source.find_all('a', href=True))
    contexts = {}
    aliases = {}
    for entry in source_entries:
        name = entry['filename']
        context = contexts.setdefault(name, {'headings': set(), 'links': set(), 'receipts': entry.get('_navigation_alias_receipts', {}),
                                             'selector': entry.get('_navigation_content_selector'),
                                             'exclude_prefix': entry.get('_navigation_generated_prefix_selector')})
        aliases[name] = entry.get('_navigation_id_aliases', {})
        for page in entry.get('prepared_pages', []):
            source = BeautifulSoup(page.get('html') or '', 'html.parser')
            context['headings'].update(_text(tag) for tag in source.find_all(re.compile(r'^h[1-6]$')))
            context['links'].update((tag['href'], _text(tag)) for tag in source.find_all('a', href=True))
    scoped_contexts = {path: [context for name, context in contexts.items()
                              if any((root / name).resolve() == path for root in roots)] for path in soups}

    def source_heading(path, text):
        owned = scoped_contexts[path]
        return any(text in context['headings'] for context in owned) if owned else text in source_headings

    headings = [{'path': path, 'id': tag['id'], 'heading': _text(tag), 'tokens': _tokens(tag)}
                for path, soup in soups.items()
                for tag in soup.find_all(re.compile(r'^h[1-6]$'), id=True) if source_heading(path, _text(tag))]
    issues, annotations = [], []
    scope_contexts = {}
    positioned_receipts = set()
    failed_receipt_anchors = set()
    for name, context in contexts.items():
        if context['receipts'] and not any((root / name).resolve() in soups for root in roots):
            issues.append({'path': name, 'reason': 'alias_receipt_file_missing'})
    for path, owned in scoped_contexts.items():
        for context in owned:
            if not context['receipts']:
                continue
            roots_selected = soups[path].select(context['selector']) if context['selector'] else [soups[path]]
            prefix = soups[path].select(context['exclude_prefix']) if context['exclude_prefix'] else []
            if len(roots_selected) != 1 or (context['exclude_prefix'] and len(prefix) != 1):
                issues.append({'path': path.name, 'reason': 'alias_receipt_content_boundary_missing'})
                continue
            anchors = [anchor for anchor in roots_selected[0].find_all('a')
                       if not any(parent is prefix_tag for prefix_tag in prefix for parent in [anchor, *anchor.parents])]
            counts = Counter(anchor.get('data-doc-web-alias-receipt') for anchor in anchors)
            for key, receipt in context['receipts'].items():
                ordinal = receipt.get('final_anchor_ordinal')
                anchor = anchors[ordinal - 1] if isinstance(ordinal, int) and 0 < ordinal <= len(anchors) else None
                valid = anchor is not None and counts[key] == 1 and anchor.get('data-doc-web-alias-receipt') == key
                valid = valid and anchor.get('data-doc-web-original-alias-href') == receipt['original_href'] and anchor.get('href') == receipt['href'] and _text(anchor) == receipt['label']
                if valid:
                    positioned_receipts.add((path, id(anchor)))
                else:
                    issues.append({'path': path.name, 'reason': 'alias_receipt_missing_or_changed', 'receipt_key': key,
                                   'expected_anchor_ordinal': ordinal, 'href': receipt['href']})
                    if anchor is not None:
                        failed_receipt_anchors.add((path, id(anchor)))

    def alias_authority(path, target, fragment, label, anchor):
        # Independent source evidence plus the original stamping map proves
        # authority. Neither the final label nor a DOM marker supplies it.
        if (path, id(anchor)) not in positioned_receipts:
            return False
        current_names = [name for name in contexts if any((root / name).resolve() == path for root in roots)]
        proven_targets = set()
        for current in current_names:
            receipt_key = anchor.get('data-doc-web-alias-receipt')
            href = anchor.get('data-doc-web-original-alias-href')
            receipt = contexts[current]['receipts'].get(receipt_key)
            if not receipt or any(receipt.get(key) != value for key, value in {'original_href': href, 'href': anchor['href'], 'label': label}.items()):
                continue
            if len(soups[path].find_all('a', attrs={'data-doc-web-alias-receipt': receipt_key})) != 1:
                continue
            for source_href, source_label in contexts[current]['links']:
                if source_href != href:
                    continue
                if source_label != label:
                    continue
                local = _local(href, current)
                if not local or local[2] or not local[1]:
                    continue
                source_path, old_id, _ = local
                mapped = [(source_path, identifier) for identifier in aliases.get(source_path, {}).get(old_id, [])]
                if mapped and len(mapped) != 1:
                    return False
                if not urlsplit(href).path and not mapped:
                    mapped = [(name, identifier) for name, mapping in aliases.items()
                              for identifier in mapping.get(old_id, [])]
                final = {(candidate.resolve(), identifier) for name, identifier in mapped for root in roots
                         if (candidate := root / name).resolve() in ids
                         and ids[candidate.resolve()][identifier] == 1}
                proven_targets.update(final)
        return proven_targets == {(target, fragment)}

    for path, soup in soups.items():
        for anchor in soup.find_all('a', href=True):
            parsed, uri_error = parse_uri(anchor['href'])
            if anchor.find_parent('a'):
                issues.append({'path': path.name, 'href': anchor['href'], 'anchor_text': _text(anchor), 'reason': 'nested_anchor'})
            if uri_error:
                issues.append({'path': path.name, 'href': anchor['href'], 'anchor_text': _text(anchor), 'reason': uri_error})
                continue
            if parsed.scheme or parsed.netloc:
                continue
            target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            fragment = unquote(parsed.fragment)
            reason = None
            if not any(target.is_relative_to(root) for root in roots):
                reason = 'outside_document'
            elif not target.is_file():
                reason = 'missing_file'
            elif fragment and (target in soups or target.suffix.casefold() in {'.html', '.htm', '.xhtml'}):
                if target not in ids:
                    try:
                        ids[target] = Counter(tag['id'] for tag in BeautifulSoup(target.read_text(encoding='utf-8'), 'html.parser').find_all(id=True))
                    except (UnicodeError, OSError):
                        reason = 'unreadable_html_target'
                if not reason:
                    count = ids[target][fragment]
                    if count != 1:
                        reason = 'missing_fragment' if count == 0 else 'duplicate_fragment'
            if not reason and fragment and target not in ids and resource_observations is not None:
                resource_observations.append({'path': path.name, 'href': anchor['href'],
                                              'status': 'resource_exists_fragment_unmeasured'})
            label = _text(anchor)
            authority = alias_authority(path, target, fragment, label, anchor)
            toc_name = next((name for name, toc_soup in toc_soups.items() if toc_soup is soup), None)
            toc_decision = toc.decision(toc_name, anchor) if toc_name and not authority else None
            if not reason and toc_decision is not None:
                if toc_decision['status'] != 'resolved':
                    reason = toc_decision['reason']
                else:
                    chosen = toc_decision['candidates'][0]
                    if (target, fragment) != ((path.parent / chosen['path']).resolve(), chosen['id']):
                        reason = 'source_toc_target_mismatch'
                if reason:
                    issues.append({'path': path.name, 'href': anchor['href'], 'anchor_text': label, 'reason': reason})
                continue
            # Independently inspect final destinations. Assert label semantics
            # only for a source-authored reference and a unique exact heading.
            owned = scoped_contexts[path]
            source_authored = any(label == source_label for context in owned for _, source_label in context['links']) if owned else label in source_labels
            if not reason and target in ids and source_authored:
                reason = _anchor_scope_reason(anchor, scope_contexts)
            if not reason and (path, id(anchor)) in positioned_receipts and not authority:
                reason = 'alias_receipt_authority_unproven'
            if not reason and (path, id(anchor)) in failed_receipt_anchors:
                continue
            if not reason and fragment and target in ids and source_authored and not authority:
                candidates, _ = _heading_candidates(label, headings) if not _anchor_scope_reason(anchor, scope_contexts) else ([], False)
                if len(candidates) > 1 and semantic_observations is not None:
                    semantic_observations.append({'path': path.name, 'href': anchor['href'], 'anchor_text': label,
                                                  'status': 'semantic_label_ambiguity',
                                                  'candidates': [{'path': candidate['path'].name, 'id': candidate['id'], 'heading': candidate['heading']}
                                                                 for candidate in candidates]})
                if len(candidates) == 1 and (target, fragment) != (candidates[0]['path'], candidates[0]['id']):
                    reason = 'source_heading_target_mismatch'
            if reason:
                issues.append({'path': path.name, 'href': anchor['href'], 'anchor_text': _text(anchor), 'reason': reason})
        annotations.extend({'path': path.name, 'status': tag['data-doc-web-navigation-status'],
                            'original_href': tag.get('data-doc-web-original-href'), 'anchor_text': _text(tag)}
                           for tag in soup.find_all(attrs={'data-doc-web-navigation-status': True}))
    return issues, annotations


def verify_final_navigation(html_files, *, source_pages=(), source_entries=(), provenance_rows=()):
    """Inspect serialized exported destinations before bundle hashes are sealed."""
    resources, semantics = [], []
    issues, annotations = inspect_navigation(html_files, source_pages=source_pages, source_entries=source_entries,
                                            provenance_rows=provenance_rows,
                                            resource_observations=resources,
                                            semantic_observations=semantics)
    return {'status': 'failed' if issues else 'passed', 'issues': issues,
            'annotations': annotations, 'resource_observations': resources,
            'semantic_observations': semantics}
