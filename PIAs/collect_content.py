#!/usr/bin/env python3
"""Collect individual bilingual PIA summaries from the artifact-derived index."""
import argparse
import concurrent.futures
import copy
import csv
import hashlib
import io
import json
import re
import subprocess
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup, Tag
from markdownify import markdownify
from build_index import generic_pia_label

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'PIAs'
CACHE = ROOT / 'work/pia_content_cache'
VERSION = 2
HEADINGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'summary']
LOCKS = {}
LOCK = threading.Lock()
FEATURE_CACHE = {}
RETRY_FAILURES = False
RETRIED = set()


def now(): return datetime.now(timezone.utc).isoformat()
def sha(data): return hashlib.sha256(data).hexdigest()
def norm(text): return unicodedata.normalize('NFKD', text.replace('’', "'")).encode('ascii', 'ignore').decode().lower()
def clean(text): return re.sub(r'\s+', ' ', text).strip()
def slug(text): return re.sub(r'[^a-z0-9]+', '-', norm(text)).strip('-')[:100] or 'assessment'
def pia(text): return bool(re.search(r'privacy impact|\bpias?\b|facteurs relatifs.{0,60}vie privee|\befr?pv?s?\b|\befr?vps?\b', norm(text)))
def tapi(text): return bool(re.search(r'technology assessment|\btapi\b|evaluation.{0,35}technolog', norm(text)))
def policy(text):
    n = norm(text)
    if re.search(r'^directive\b|directive on privacy|directive sur l.evaluation|policy on privacy|politique sur la protection|norme sur|standard on privacy|^privacy policy$|^politique de confidentialite$|^info source$|^infosource$', n): return True
    return not pia(text) and bool(re.search(r'privacy commissioner|commissariat a la protection|commissaire a la protection|^(?:request forms?|formulaires? de demande)$|^(?:privacy act|access to information act|loi sur la protection des renseignements personnels|loi sur l.acces a l.information)$', n))



class Redirects(urllib.request.HTTPRedirectHandler):
    def __init__(self): self.history = []
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.history.append({'url': req.full_url, 'http_status': code, 'location': newurl})
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url, refresh=False):
    url = urllib.parse.urldefrag(url)[0]
    key = sha(url.encode())
    with LOCK: mutex = LOCKS.setdefault(key, threading.Lock())
    with mutex:
        CACHE.mkdir(parents=True, exist_ok=True)
        meta, raw = CACHE / (key + '.json'), CACHE / (key + '.body')
        if meta.exists() and raw.exists() and not refresh:
            cached = json.loads(meta.read_text())
            if not (RETRY_FAILURES and key not in RETRIED and (cached['http_status'] != 200 or cached['error'])):
                return cached, raw.read_bytes()
        RETRIED.add(key)
        result = {'requested_url': url, 'final_url': url, 'http_status': None, 'checked_at_utc': now(), 'redirects': [], 'content_type': '', 'encoding': '', 'error': None}
        data = b''
        handler = Redirects()
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; PIBs-PIA-collection/1.0)'})
            with urllib.request.build_opener(handler).open(req, timeout=35) as response:
                result.update(final_url=response.url, http_status=response.status, content_type=response.headers.get('Content-Type', ''), encoding=response.headers.get_content_charset() or 'utf-8', last_modified=response.headers.get('Last-Modified'), etag=response.headers.get('ETag'))
                data = response.read(15_000_001)
                if len(data) > 15_000_000:
                    result['error'] = 'response_exceeds_15MB_limit'
                    data = b''
        except urllib.error.HTTPError as exc:
            data = exc.read(10000)
            result.update(http_status=exc.code, final_url=exc.url, content_type=exc.headers.get('Content-Type', ''), error=str(exc))
        except Exception as exc:
            result['error'] = type(exc).__name__ + ': ' + str(exc)
        result.update(redirects=handler.history, byte_count=len(data), sha256=sha(data))
        raw.write_bytes(data)
        meta.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        return result, data


def soup_page(data, metadata):
    soup = BeautifulSoup(data.decode(metadata.get('encoding') or 'utf-8', errors='replace'), 'html.parser')
    return soup


def main_content(soup):
    main = soup.find('main') or soup.find(attrs={'role': 'main'}) or soup.find(id='main-content') or soup.body or soup
    main = copy.copy(main)
    for node in main.select('script, style, nav, footer, header, aside[role="navigation"], .pagedetails, .page-details, .gc-subway, .wb-share, .wb-prettify, #wb-info, #wb-bc, .gc-most-requested, .gc-followus, .gc-features'):
        node.decompose()
    for heading in list(main.find_all(HEADINGS)):
        if heading.parent is not None and re.search(r'^(?:access to information and privacy menu|menu.{0,50}(?:aiprp|information))$', norm(clean(heading.get_text(' ', strip=True)))):
            menu = heading.find_parent(class_='module') or heading.find_parent(class_='pull-right') or heading.find_parent('aside')
            if menu: menu.decompose()
    for heading in list(main.find_all(HEADINGS)):
        if heading.parent is not None and re.search(r'^(?:related (?:links|resources)|liens connexes|ressources connexes|page details|details de la page|filter these results|filtrez les resultats|feature$|en vedette$|questions|contact|contactez|stay tuned|restez)', norm(clean(heading.get_text(' ', strip=True)))):
            for node in section(heading):
                if node.parent is not None: node.decompose()
    return main


def language_links(soup, base):
    result = {}
    for tag in soup.select('a[lang][href], a[hreflang][href], link[hreflang][href]'):
        lang = (tag.get('hreflang') or tag.get('lang', '')).split('-')[0]
        if lang in ('en', 'fr'): result[lang] = urllib.parse.urljoin(base, tag['href'])
    return result


def section(heading):
    """Select a DOM range without copying wrappers across its end boundary."""
    if heading.name == 'summary' and heading.parent and heading.parent.name == 'details':
        return [heading, *[node for node in heading.parent.children if isinstance(node, Tag) and node is not heading]]
    level = int(heading.name[1]) if re.fullmatch('h[1-6]', heading.name) else 6
    boundary = heading.find_next(lambda tag: tag.name in HEADINGS and
                                 ((tag.name == 'summary' and heading.name == 'summary') or
                                  (tag.name != 'summary' and int(tag.name[1]) <= level)))
    nodes, selected = [heading], {id(heading)}
    for nxt in heading.next_elements:
        if nxt is boundary: break
        if not isinstance(nxt, Tag): continue
        if any(id(parent) in selected for parent in nxt.parents): continue
        if boundary is not None and any(parent is nxt for parent in boundary.parents): continue
        nodes.append(nxt)
        selected.add(id(nxt))
    return nodes


def html_nodes(nodes): return '\n'.join(str(x) for x in nodes)


def heading_anchor(heading, base):
    ident = heading.get('id')
    if not ident:
        inner = heading.find(attrs={'id': True}) or heading.find('a', attrs={'name': True})
        ident = (inner.get('id') or inner.get('name')) if inner else None
    if not ident and heading.parent.name in ('section', 'details', 'article'):
        ident = heading.parent.get('id')
    if not ident:
        prev = heading.find_previous_sibling()
        if prev and prev.name == 'a': ident = prev.get('id') or prev.get('name')
    return urllib.parse.urldefrag(base)[0] + ('#' + urllib.parse.quote(ident, safe='-_.:') if ident else ''), ident


def is_year(text): return bool(re.fullmatch(r'\d{4}(?:\s*[-–/]\s*\d{2,4})?', text))


def list_scope(main):
    """PIA sections, excluding adjacent TAPI, ATI, policy and utility sections."""
    headings = main.find_all(HEADINGS)
    h1 = main.find('h1')
    dedicated = bool(h1 and pia(h1.get_text(' ', strip=True)))
    candidates = []
    for h in headings:
        title = clean(h.get_text(' ', strip=True))
        if (pia(title) or re.search(r'privacy assessment summar|sommaires d.evaluations de la protection de la vie privee',norm(title))) and not policy(title) and not tapi(title): candidates.append(h)
        elif dedicated and norm(title) in ('summaries', 'resumes', 'sommaires'): candidates.append(h)
    # Use the whole dedicated page only if it has no more focused list heading.
    candidates = [h for h in candidates if not re.search(r'what is|qu.est.ce|process|processus|guide|submit|soumettre|presenter|presentation|overview|apercu|survol|speeches|discours|directive|why |pourquoi|raison|motifs', norm(h.get_text(' ', strip=True)))]
    focused = [h for h in candidates if h.name != 'h1' and (generic_pia_label(clean(h.get_text(' ', strip=True)).replace('privées', 'privée')) or re.search(r'privacy assessment summar|sommaires d.evaluations de la protection de la vie privee',norm(h.get_text(' ',strip=True))))]
    summary_scopes = [h for h in candidates if norm(clean(h.get_text(' ', strip=True))) in ('summaries', 'resumes', 'sommaires') or (h in focused and re.search(r'summar|resum|sommair', norm(h.get_text(' ', strip=True))))]
    return summary_scopes or focused or ([h1] if dedicated else candidates)


def discover(metadata, data, lang):
    soup = soup_page(data, metadata)
    main = main_content(soup)
    base = metadata['final_url']
    scopes = list_scope(main)
    records = []
    skipped = []
    for scope in scopes:
        nodes = section(scope)
        box = BeautifulSoup(html_nodes(nodes), 'html.parser')
        # Keep links to assessments, not nearby policies or navigation.
        for a in box.find_all('a', href=True):
            label = clean(a.get_text(' ', strip=True))
            href = urllib.parse.urljoin(base, a['href'])
            bare, fragment = urllib.parse.urldefrag(href)
            if not label or not href.startswith(('http://', 'https://')): continue
            if bare == urllib.parse.urldefrag(base)[0]: continue
            if re.search(r'^(?:guide|submit|presenter|speeches|discours)|overview|survol', norm(label)): continue
            if policy(label) or tapi(label) or re.search(r'corporate services|services generaux|statistical programs|programmes statistiques', norm(label)): continue
            if re.search(r'^(?:contact us|contactez-nous|accessibility|accessibilite|haut de la page|top of page|page details|details de la page|abonnez-vous|stay tuned|suivez-nous|follow us|twitter|facebook|linkedin|canada\.ca|sommaire des demandes|access to information and privacy|acces a l.information et protection des renseignements personnels)$', re.sub(r'\s*\([^)]*\)', '', norm(label)).strip()): continue
            if urllib.parse.urlsplit(href).netloc in ('laws-lois.justice.gc.ca', 'www.tbs-sct.canada.ca', 'www.tbs-sct.gc.ca', 'open.canada.ca', 'ouvert.canada.ca'): continue
            # Narrative links inside a complete inline assessment are supporting
            # program references, not additional assessment documents. Year
            # disclosure lists still contain independent assessment links.
            details_parent = a.find_parent('details')
            summary = details_parent.find('summary') if details_parent else None
            if summary and not is_year(clean(summary.get_text(' ', strip=True))):
                prose = sum(len(p.get_text(' ', strip=True)) for p in details_parent.find_all('p'))
                if prose >= 300: continue
            # Require either a list item, table row, or explicitly named PIA link.
            if not (a.find_parent(['li', 'td', 'p', 'h2', 'h3', 'h4']) or pia(label)): continue
            # Introductory cross-references and generic PIA landing links are not documents.
            if re.fullmatch(r'privacy impact assessments?|evaluations? des facteurs relatifs a la vie privee|summaries|sommaires|resumes|privacy|vie privee', norm(label)): continue
            records.append({'title': label, 'url': href, 'kind': 'page', 'discovered_under': clean(scope.get_text(' ', strip=True)), 'discovery_method': 'pia_section_link'})
        # Inline summaries have substantial text beneath a program heading,
        # commonly separated by h2/h3 or details/summary blocks.
        for heading in nodes:
            # nodes can include wrappers; search headings in them, then dedupe.
            hs = ([heading] if heading.name in HEADINGS else []) + heading.find_all(HEADINGS)
            for h in hs:
                title = clean(h.get_text(' ', strip=True))
                if not title or is_year(title) or policy(title) or tapi(title): continue
                if generic_pia_label(title) or re.search(r'process|processus|^title$|^titre$|^more information$|^complement|^renseignements supplementaires$', norm(title)): continue
                if h.name not in ('h2', 'h3', 'h4', 'summary'): continue
                if re.search(r'^why |^pourquoi|^raison|^motifs|^more information|^complement|^renseignements supplementaires', norm(title)): continue
                scope_level = int(scope.name[1]) if re.fullmatch('h[1-6]', scope.name) else 1
                if h.name != 'summary' and int(h.name[1]) > scope_level + 1:
                    higher = h.find_previous(lambda t: t.name in HEADINGS and t.name != 'summary' and int(t.name[1]) < int(h.name[1]))
                    if higher and not is_year(clean(higher.get_text(' ', strip=True))): continue
                if h is scope or norm(title) in ('summary', 'summaries', 'resume', 'resumes', 'sommaires', 'overview', 'apercu', 'introduction', 'background', 'context', 'contexte', 'conclusion', 'description', 'risks', 'risques'): continue
                parts = section(h)
                content = clean(BeautifulSoup(html_nodes(parts[1:]), 'html.parser').get_text(' ', strip=True))
                # An inline summary must contain paragraphs, not just link lists.
                paragraphs = BeautifulSoup(html_nodes(parts[1:]), 'html.parser').find_all('p')
                prose_length = sum(len(p.get_text(' ', strip=True)) for p in paragraphs if len(p.get_text(' ', strip=True)) > 80 and not (p.find('a') and p.get_text(' ', strip=True) == p.find('a').get_text(' ', strip=True)))
                if prose_length < 300: continue
                content_box = BeautifulSoup(html_nodes(parts[1:]), 'html.parser')
                if len(content_box.find_all('a', href=True)) > 3 and prose_length < 1500: continue
                # Program-level headings must not be subsections inside a PIA.
                if re.search(r'purpose|objectif|description|risk|risque|mitigation|attenuation|conclusion|scope|portee|introduction|background|context|contexte|overview|apercu|personal information|renseignements personnels|institution|authority|autorite|legal|juridique|privacy impact assessment process|processus', norm(title)) and not pia(title): continue
                if re.search(r'what is|qu.est.ce|related|connexes|benefits|avantages|about|a propos|responsibilities|responsabilites|contact', norm(title)): continue
                # If the heading is a link-only heading, the linked page is the document.
                if h.find('a', href=True) and len(h.get_text(' ', strip=True)) == len(h.find('a').get_text(' ', strip=True)): continue
                title_tag = next((z for z in parts if z.name in HEADINGS and norm(clean(z.get_text(' ', strip=True))) in ('title', 'titre')), None)
                if title_tag:
                    title_paragraph = title_tag.find_next('p')
                    if title_paragraph: title = clean(title_paragraph.get_text(' ', strip=True))
                url, anchor = heading_anchor(h, base)
                anchor_type = 'native_id' if anchor else 'text_fragment'
                if not anchor:
                    anchor = ':~:text=' + urllib.parse.quote(title, safe='')
                    url = urllib.parse.urldefrag(base)[0] + '#' + anchor
                    skipped.append({'title': title, 'reason': 'no_native_anchor_used_browser_text_fragment'})
                records.append({'title': title, 'url': url, 'kind': 'inline', 'anchor': anchor, 'anchor_type': anchor_type, 'source_heading': clean(h.get_text(' ', strip=True)), 'heading_level': h.name, 'discovered_under': clean(scope.get_text(' ', strip=True)), 'discovery_method': 'inline_heading', 'html': html_nodes(parts)})
    # One record per source URL/inline title; do not conflate separate anchors.
    unique = {}
    for record in records:
        key = (record['url'], record['title'] if record['kind'] == 'inline' and not record.get('anchor') else '')
        unique.setdefault(key, record)
    return list(unique.values()), {'scopes': [clean(s.get_text(' ', strip=True)) for s in scopes], 'warnings': skipped, 'language_alternates': language_links(soup, base)}


def navigation_label(title):
    n = norm(title)
    n = re.sub(r'^(?:opc|osfi|bsif)\s*[-–:]?\s*', '', n)
    n = re.sub(r' du commissariat$', '', n)
    return generic_pia_label(n) and bool(re.search(r'assessments|summaries|evaluations|resumes|sommaires', n))


def discover_list(metadata, data, lang, refresh=False, depth=0):
    records, details = discover(metadata, data, lang)
    pages = [(metadata, data)]
    if depth < 2:
        expanded = []
        for record in records:
            if record['kind'] == 'page' and navigation_label(record['title']):
                m, d = fetch(record['url'], refresh)
                pages.append((m, d))
                if m['http_status'] == 200 and not m['error']:
                    more, info, descendants = discover_list(m, d, lang, refresh, depth+1)
                    expanded.extend(more)
                    pages.extend(descendants[1:])
                    details.setdefault('navigation', []).append({'url': record['url'], 'http_status': m['http_status'], 'discovered_count': len(more)})
                else:
                    details.setdefault('warnings', []).append({'title': record['title'], 'reason': 'nested_list_http_failure', 'http': m})
            else: expanded.append(record)
        records = expanded
    return records, details, pages


def parallel_fetch(urls, refresh=False):
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch, u, refresh): u for u in sorted(set(urls))}
        for future in concurrent.futures.as_completed(futures):
            url = futures[future]
            results[url] = future.result()
            print(results[url][0]['http_status'], url, flush=True)
    return results


def metadata_only(metadata): return dict(metadata)


def page_features(metadata, data):
    if metadata['http_status'] != 200 or metadata['error'] or 'html' not in metadata['content_type'].lower(): return {}
    cache_key = (metadata['final_url'], metadata['sha256'])
    if cache_key in FEATURE_CACHE: return FEATURE_CACHE[cache_key]
    soup = soup_page(data, metadata)
    main = main_content(soup)
    h1 = main.find('h1')
    features = {'page_title': clean(h1.get_text(' ', strip=True)) if h1 else clean(soup.title.get_text(' ', strip=True)) if soup.title else None,
            'html_language': (soup.html.get('lang', '') if soup.html else '').split('-')[0],
            'language_alternates': language_links(soup, metadata['final_url']),
            'date_modified': next((m.get('content') for m in soup.find_all('meta') if (m.get('name') or m.get('property') or '').lower() in ('dcterms.modified', 'dc.date.modified', 'date.modified', 'article:modified_time')), None),
            'date_published': next((m.get('content') for m in soup.find_all('meta') if (m.get('name') or m.get('property') or '').lower() in ('dcterms.issued', 'dc.date.issued', 'article:published_time')), None),
            'has_pia_text': pia(main.get_text(' ', strip=True))}
    FEATURE_CACHE[cache_key] = features
    return features


def source_key(url):
    # HTTP fragments select independent summaries and must not be discarded.
    parts = urllib.parse.urlsplit(urllib.parse.unquote(url))
    host = parts.netloc.lower()
    if host in ('www.publicsafety.gc.ca', 'www.securitepublique.gc.ca'): host = host[4:]
    path = parts.path.rstrip('/')
    if host == 'ised-isde.canada.ca': path = path.replace('/site/isde/fr/transparence/services-laiprp/', '/site/isde/fr/services-laiprp/')
    return urllib.parse.urlunsplit((parts.scheme, host, path, parts.query, parts.fragment))


def language_variant_key(url):
    parts = urllib.parse.urlsplit(source_key(url))
    path = re.sub(r'-(?:eng|fra|en|fr)(?=\.[a-z]+(?:/|$))', '-{lang}', parts.path, flags=re.I)
    path = re.sub(r'_[ef](?=\.pdf(?:/|$))', '_{lang}', path, flags=re.I)
    query = re.sub(r'(?i)(?<=lang=)(?:eng|fra|en|fr)(?=&|$)', '{lang}', parts.query)
    if (path, query) == (parts.path, parts.query): return None
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, query, parts.fragment))


def inline_pair_key(record):
    title = norm(record.get('source_heading', ''))
    months = {'january':'01','janvier':'01','february':'02','fevrier':'02','march':'03','mars':'03','april':'04','avril':'04','may':'05','mai':'05','june':'06','juin':'06','july':'07','juillet':'07','august':'08','aout':'08','september':'09','septembre':'09','october':'10','octobre':'10','november':'11','novembre':'11','december':'12','decembre':'12'}
    match = re.fullmatch(r'(\d+)\.\s*([a-z]+)\s*(20\d{2})', title)
    if match and match[2] in months: return ('numbered_date', match[1], match[3], months[match[2]])
    if record.get('anchor_type') == 'native_id': return ('native_id', record['anchor'])
    return None


def pair_records(records, results):
    """Pair with language-switch URLs or a bilingual source section key."""
    # Deduplicate aliases that redirect to the same document in the same language.
    unique, aliases = {}, {}
    reviewed_aliases = {}
    alias_path = OUT / 'source_aliases.csv'
    if alias_path.exists():
        for row in csv.DictReader(io.StringIO(alias_path.read_text())):
            reviewed_aliases[(row['institution_id'], row['language'], source_key(row['source_url']))] = row
    for record in records:
        record.setdefault('discovery_references', []).append({k: record.get(k) for k in ('url', 'title', 'list_url', 'discovery_method')})
        m, d = results[urllib.parse.urldefrag(record['url'])[0]]
        fragment = urllib.parse.urlsplit(record['url']).fragment
        final = m['final_url'] + ('#' + fragment if fragment else '')
        review = reviewed_aliases.get((record.get('institution_id'), record['language'], source_key(record['url'])))
        identity = review['replacement_url'] if review else final
        key = (record['language'], source_key(identity))
        if key in unique:
            previous = unique[key]
            previous_meta = results[urllib.parse.urldefrag(previous['url'])[0]][0]
            if m['http_status'] == 200 and previous_meta['http_status'] != 200:
                record['aliases'] = list(dict.fromkeys([record['url'], final, *previous.get('aliases', []), previous['url']]))
                record['discovery_references'].extend(previous.get('discovery_references', []))
                unique[key] = record
            else:
                previous.setdefault('aliases', []).append(record['url'])
                previous['discovery_references'].extend(record['discovery_references'])
            continue
        unique[key] = record
        record['aliases'] = list(dict.fromkeys([record['url'], final, *record.get('aliases', [])]))
    records = list(unique.values())
    for i, record in enumerate(records):
        for url in record['aliases']: aliases[(record['language'], source_key(url))] = i
    pairs, used = [], set()
    for i, record in enumerate(records):
        if i in used: continue
        lang, other = record['language'], 'fr' if record['language'] == 'en' else 'en'
        mate, method, evidence = None, 'unpaired', None
        m, d = results[urllib.parse.urldefrag(record['url'])[0]]
        features = page_features(m, d)
        alternate = features.get('language_alternates', {}).get(other)
        if record['kind'] == 'page' and alternate:
            candidate = aliases.get((other, source_key(alternate)))
            if candidate is not None and candidate not in used:
                mate, method, evidence = candidate, 'explicit_language_link', {'from_url': record['url'], 'alternate_url': alternate}
        if mate is None and record['kind'] == 'page':
            for j, other_record in enumerate(records):
                if j in used or other_record['language'] != other or other_record['kind'] != 'page': continue
                om, od = results[urllib.parse.urldefrag(other_record['url'])[0]]
                reverse = page_features(om, od).get('language_alternates', {}).get(lang)
                if reverse and aliases.get((lang, source_key(reverse))) == i:
                    mate, method, evidence = j, 'explicit_language_link', {'from_url': other_record['url'], 'alternate_url': reverse}
                    break
        if mate is None and record['kind'] == 'page':
            variant = language_variant_key(record['url'])
            choices = [j for j, r in enumerate(records) if j not in used and r['language'] == other and r['kind'] == 'page' and variant and language_variant_key(r['url']) == variant]
            if len(choices) == 1:
                mate, method, evidence = choices[0], 'matching_language_variant_url', {'normalized_url_key': variant, 'observed_url_en': record['url'] if lang == 'en' else records[choices[0]]['url'], 'observed_url_fr': record['url'] if lang == 'fr' else records[choices[0]]['url']}
        overrides = OUT / 'pairing_overrides.csv'
        if mate is None and overrides.exists():
            for override in csv.DictReader(io.StringIO(overrides.read_text())):
                if override['institution_id'] != record.get('institution_id'): continue
                if source_key(record['url']) != source_key(override['url_' + lang]): continue
                candidate = aliases.get((other, source_key(override['url_' + other])))
                if candidate is not None and candidate not in used:
                    mate, method, evidence = candidate, 'reviewed_bilingual_list_titles', dict(override)
                    break
        if mate is None and record['kind'] == 'inline' and alternate:
            key = inline_pair_key(record)
            choices = [j for j, r in enumerate(records) if j not in used and r['language'] == other and r['kind'] == 'inline'
                       and source_key(urllib.parse.urldefrag(r['url'])[0]) == source_key(urllib.parse.urldefrag(alternate)[0]) and key and inline_pair_key(r) == key]
            if len(choices) == 1:
                mate, method, evidence = choices[0], 'bilingual_inline_section_key', {'section_key': key, 'alternate_page_url': alternate}
        group = {lang: record}
        used.add(i)
        if mate is not None:
            group[other] = records[mate]
            used.add(mate)
        pairs.append((group, method, evidence))
    return pairs


def persist_raw(folder, metadata, data):
    suffix = '.pdf' if data.startswith(b'%PDF') else '.html' if 'html' in metadata['content_type'].lower() else '.bin'
    relative = Path('raw') / (sha(metadata['requested_url'].encode())[:20] + suffix)
    if metadata['http_status'] == 200 and data and not metadata['error']:
        path = folder / relative
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(data)
        return str(relative)
    return None


def export_source(folder, pia_id, record, lang, results):
    metadata, data = results[urllib.parse.urldefrag(record['url'])[0]]
    features = page_features(metadata, data)
    source = {'url': record['url'], 'title_from_list': record.get('title'), 'kind': record['kind'],
              'discovery_method': record['discovery_method'], 'list_url': record.get('list_url'),
              'discovered_under': record.get('discovered_under'), 'discovery_references': record.get('discovery_references', []), 'aliases': record.get('aliases', []),
              'alternative_http_observations': [metadata_only(results[urllib.parse.urldefrag(u)[0]][0]) for u in record.get('aliases', []) if urllib.parse.urldefrag(u)[0] in results and urllib.parse.urldefrag(u)[0] != metadata['requested_url']],
              'http': metadata_only(metadata), 'raw_path': persist_raw(folder, metadata, data),
              'markdown_path': None, 'markdown_sha256': None, 'status': 'pending', **features}
    if record['kind'] == 'inline':
        source.update(anchor=record['anchor'], anchor_type=record['anchor_type'], source_heading=record.get('source_heading'))
    if metadata['http_status'] != 200 or metadata['error']:
        source['status'] = 'http_error' if metadata['http_status'] else 'request_error'
        return source
    if features.get('html_language') in ('en', 'fr') and features['html_language'] != lang:
        source['status'] = 'language_mismatch'
        return source
    title = record.get('title') if record['kind'] == 'inline' else features.get('page_title') or record.get('title')
    source['title'] = title
    if re.search(r'(?:^|\b)(?:not found|errors? / erreur|page (?:not found|introuvable))|access denied|acces refuse|error 404|erreur 404|we couldn.t find', norm(title or '')):
        source['status'] = 'soft_error_page'
        return source
    if features and not features['has_pia_text'] and 'fightspam-combattrelepourriel.ised-isde.canada.ca' in metadata['final_url']:
        source.update(status='not_pia_content', review_note='The list links to a general anti-spam program homepage, not a PIA summary.')
        return source
    try:
        if data.startswith(b'%PDF'):
            cache_path = CACHE / (sha(metadata['requested_url'].encode()) + '.body')
            converted = subprocess.run(['pdftotext', '-layout', str(cache_path), '-'], capture_output=True, check=True)
            body = converted.stdout.decode('utf-8', errors='replace')
            source['conversion'] = 'pdftotext -layout'
        elif 'html' in metadata['content_type'].lower():
            soup = soup_page(data, metadata)
            main = BeautifulSoup(record['html'], 'html.parser') if record['kind'] == 'inline' else main_content(soup)
            for a in main.find_all('a', href=True): a['href'] = urllib.parse.urljoin(metadata['final_url'], a['href'])
            for img in main.find_all('img', src=True): img['src'] = urllib.parse.urljoin(metadata['final_url'], img['src'])
            body = markdownify(str(main), heading_style='ATX', bullets='-', strip=['script', 'style'])
            source['conversion'] = 'markdownify'
        elif 'text/plain' in metadata['content_type'].lower():
            body = data.decode(metadata.get('encoding') or 'utf-8', errors='replace')
            source['conversion'] = 'plain_text'
        else:
            source['status'] = 'unsupported_content_type'
            return source
        body = re.sub(r'\n{3,}', '\n\n', body).strip()
        if len(body) < 180:
            source['status'] = 'insufficient_content'
            return source
        relative = f'{pia_id}_{lang}.md'
        header = {'title': title, 'institution_id': folder.name, 'language': lang, 'source_url': record['url'],
                  'retrieved_at_utc': metadata['checked_at_utc'], 'http_status': metadata['http_status'], 'source_sha256': metadata['sha256'], 'content_kind': record['kind']}
        frontmatter = '---\n' + ''.join(f'{k}: {json.dumps(v, ensure_ascii=False)}\n' for k, v in header.items()) + '---\n\n'
        if record['kind'] == 'inline' or not body.lstrip().startswith('# '): body = '# ' + (title or 'PIA summary') + '\n\n' + body
        content = (frontmatter + body + '\n').encode()
        (folder / relative).write_bytes(content)
        source.update(markdown_path=relative, markdown_sha256=sha(content), text_sha256=sha(body.encode()), word_count=len(body.split()), status='exported')
    except Exception as exc:
        source.update(status='conversion_error', conversion_error=type(exc).__name__ + ': ' + str(exc))
    return source


def collect(rows, discovery, results, refresh=False):
    by_org = {}
    for entry in discovery:
        by_org.setdefault(entry['institution_id'], []).append(entry)
    all_records = []
    for entry in discovery:
        for record in entry['records']:
            record.update(language=entry['language'], institution_id=entry['institution_id'], list_url=entry['url'])
            all_records.append(record)
    document_urls = {urllib.parse.urldefrag(r['url'])[0] for r in all_records}
    results.update(parallel_fetch(document_urls - results.keys(), refresh))
    # Explicit language links can recover a translation omitted from a list.
    existing = {(r['institution_id'], r['language'], source_key(r['url'])) for r in all_records}
    additions = []
    for record in all_records:
        if record['kind'] != 'page': continue
        m, d = results[urllib.parse.urldefrag(record['url'])[0]]
        other = 'fr' if record['language'] == 'en' else 'en'
        alternate = page_features(m, d).get('language_alternates', {}).get(other)
        if not alternate or source_key(alternate) == source_key(record['url']): continue
        if re.search(r'/(?:scripts/language\.asp|errors/404\.html|en|fr)(?:\.html)?/?$', urllib.parse.urlsplit(alternate).path): continue
        key = (record['institution_id'], other, source_key(alternate))
        if key in existing: continue
        existing.add(key)
        additions.append({'title': None, 'url': alternate, 'kind': 'page', 'discovery_method': 'document_language_link', 'language': other, 'institution_id': record['institution_id'], 'list_url': record['list_url'], 'discovered_under': None})
    results.update(parallel_fetch({urllib.parse.urldefrag(r['url'])[0] for r in additions} - results.keys(), refresh))
    for record in additions:
        m, d = results[urllib.parse.urldefrag(record['url'])[0]]
        features = page_features(m, d)
        if m['http_status'] == 200 and not features.get('has_pia_text') and not d.startswith(b'%PDF'):
            continue  # A default language landing page is not a translation.
        record['title'] = features.get('page_title')
        all_records.append(record)
    totals, organization_counts = Counter(), {}
    for row in rows:
        org_id = row['institution_id']
        folder = OUT / org_id
        folder.mkdir(exist_ok=True)
        entries = by_org.get(org_id, [])
        payload = {'schema_version': 1, 'collector_version': VERSION, 'collected_at_utc': now(),
                   'institution_id': org_id, 'gc_orgID': row['gc_orgID'], 'open_canada_org_id': row['open_canada_org_id'],
                   'open_canada_org_slug': row['open_canada_org_slug'], 'name_en': row['legal_name_en'], 'name_fr': row['legal_name_fr'],
                   'registry_membership': row['registry_membership'], 'source_index_sha256': sha((OUT / 'index.csv').read_bytes()), 'list_pages': {}, 'pias': []}
        for lang in ('en', 'fr'):
            entry = next((e for e in entries if e['language'] == lang), None)
            page = {'indexed_url': row['pia_list_url_' + lang] or None, 'index_resolution': row['resolution_' + lang],
                    'pia_link_in_infosource': row['pia_link_in_infosource_' + lang], 'review_note': row['review_note_' + lang] or None,
                    'status': 'no_indexed_url', 'captures': [], 'discovered_count': 0}
            if entry:
                urls = list(dict.fromkeys([entry['url'], *[n['url'] for n in entry.get('navigation', [])]]))
                for url in urls:
                    m, d = results.get(url) or fetch(url)
                    results[url] = (m, d)
                    page['captures'].append({**m, 'raw_path': persist_raw(folder, m, d)})
                page.update(discovered_count=len(entry['records']), scopes=entry.get('scopes', []), warnings=entry.get('warnings', []))
                page['status'] = 'attribution_blocked' if entry['attribution_block'] else 'discovered' if entry['records'] else 'http_error' if entry['http']['http_status'] != 200 else 'no_summaries_discovered'
            payload['list_pages'][lang] = page
        records = [r for r in all_records if r['institution_id'] == org_id]
        for group, method, evidence in pair_records(records, results):
            seed = group.get('en') or group['fr']
            pia_id = 'pia-' + sha(seed['url'].encode())[:12]
            document = {'pia_id': pia_id, 'title_en': None, 'title_fr': None, 'url_en': None, 'url_fr': None,
                        'pairing_status': 'paired' if len(group) == 2 else 'missing_counterpart', 'pairing_method': method,
                        'pairing_evidence': evidence, 'sources': {}}
            for lang, record in group.items():
                source = export_source(folder, pia_id, record, lang, results)
                document['sources'][lang] = source
                document['title_' + lang] = source.get('title') or record.get('title')
                document['url_' + lang] = record['url']
                totals[source['status']] += 1
            payload['pias'].append(document)
        payload['summary'] = {'pia_count': len(payload['pias']), 'paired_count': sum(p['pairing_status'] == 'paired' for p in payload['pias']),
                              'source_status_counts': dict(Counter(s['status'] for p in payload['pias'] for s in p['sources'].values()))}
        organization_counts[org_id] = payload['summary']
        # Remove only exports generated by this collector that are no longer referenced.
        referenced = {s['markdown_path'] for p in payload['pias'] for s in p['sources'].values() if s['markdown_path']}
        for old in folder.glob('pia-*_??.md'):
            if old.name not in referenced: old.unlink()
        (folder / 'collection.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    manifest = {'schema_version': 1, 'collector_version': VERSION, 'generated_at_utc': now(), 'source_index_sha256': sha((OUT / 'index.csv').read_bytes()),
                'collector_sha256': sha(Path(__file__).read_bytes()), 'organization_count': len(rows), 'organizations_with_pias': sum(v['pia_count'] > 0 for v in organization_counts.values()),
                'pia_count': sum(v['pia_count'] for v in organization_counts.values()), 'paired_count': sum(v['paired_count'] for v in organization_counts.values()),
                'source_status_counts': dict(totals), 'organizations': organization_counts}
    (OUT / 'collection_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    from reference_extraction import enrich_collections
    enrich_collections()
    print('Collection complete:', {k:v for k,v in manifest.items() if k != 'organizations'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument('--discover-only', action='store_true')
    parser.add_argument('--retry-failures', action='store_true', help='Recheck failed cached HTTP requests once this run')
    args = parser.parse_args()
    global RETRY_FAILURES
    RETRY_FAILURES = args.retry_failures
    rows = list(csv.DictReader((OUT / 'index.csv').open()))
    urls = [r['pia_list_url_' + lang] for r in rows for lang in ('en', 'fr') if r['pia_list_url_' + lang]]
    results = parallel_fetch(urls, args.refresh)
    discovery = []
    for row in rows:
        for lang in ('en', 'fr'):
            url = row['pia_list_url_' + lang]
            if not url: continue
            metadata, data = results[url]
            records, details = ([], {})
            attribution_block = bool(row['review_note_' + lang] and ('IRCC' in row['review_note_' + lang] or 'request search' in row['review_note_' + lang]))
            if metadata['http_status'] == 200 and not metadata['error'] and not attribution_block:
                records, details, _ = discover_list(metadata, data, lang, args.refresh)
            discovery.append({'institution_id': row['institution_id'], 'language': lang, 'url': url, 'http': metadata, 'attribution_block': attribution_block, 'records': records, **details})
    (ROOT / 'work/pia_discovery.json').write_text(json.dumps(discovery, ensure_ascii=False, indent=2) + '\n')
    print('Discovery:', Counter((x['language'],len(x['records'])) for x in discovery))
    if args.discover_only: return
    collect(rows, discovery, results, args.refresh)


if __name__ == '__main__': main()
