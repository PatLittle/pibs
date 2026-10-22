"""Conservative, provenance-preserving presentation names (version 2)."""
import re
import unicodedata

VERSION = 3
NAME_FIELDS = ['name_original', 'name_normalized', 'name_prefix', 'name_suffix',
               'name_normalization_method', 'name_normalization_review']
PREFIX = re.compile(r"^\s*(\(?(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Hon\.?|The Honourable|The Honorable|Honourable|Honorable|l['’]honorable|The Right Honourable|Right Honourable|Rt\.? Hon\.?|AADM|ADM|DM|retired|retraité|retraitée|Senator|Judge|Justice|Mme\.?|Lgén|Mgén|Bgén|Lieutenant[- ]général(?:e)?|Major[- ]général(?:e)?|Brigadier[- ]général(?:e)?|Général(?:e)?|Contre[- ]amiral(?:e)?|Vice[- ]amiral(?:e)?|Amiral(?:e)?|MGen|Maj[- ]?Gen|Major[- ]General|LGen|Lt[- ]?Gen|Lieutenant[- ]General|BGen|Brigadier[- ]General|General|Colonel|Col\.?|Lieutenant[- ]Colonel|Lt[- ]?Col|LCol|Lieutenant[- ]Commander|LCdr|Commander|Cdr|Captain|Capt\.?|Major|Maj\.?|Admiral|Vice[- ]Admiral|VAdm|Rear[- ]Admiral|RAdm|Commodore|Cmdre|Commissioner)\)?)(?:\s+|$)", re.I)
SUFFIX = re.compile(r'^(?:Jr\.?|Sr\.?|II|III|IV|Ph\.?D\.?|KC|QC)$', re.I)


def normalize_name(value):
    original = '' if value is None else str(value)
    clean = ' '.join(unicodedata.normalize('NFC', original).split())
    prefixes, suffixes = [], []
    if re.search(r"minister['’]s office|bureau du ministre", clean, re.I) or clean.casefold() in {'n/a', 'na', 'vacant', 'various', 'redacted', '[redacted]', '-', '~'}:
        return dict(name='', name_original=original, name_normalized='', name_prefix='', name_suffix='', name_normalization_method='non_person_placeholder', name_normalization_review='true')
    def strip_prefix(part):
        while True:
            separator = re.match(r'^([;/\\|~\-]+)\s*', part)
            if separator:
                prefixes.append(separator[1])
                part = part[separator.end():].strip()
                continue
            trailing = re.search(r'\s+(\([^()]+\))$', part)
            if trailing and PREFIX.fullmatch(trailing[1]):
                prefixes.append(trailing[1])
                part = part[:trailing.start()].strip()
                continue
            match = PREFIX.match(part)
            if not match:
                return part.strip()
            remaining = part[match.end():].strip()
            if not remaining:
                return part.strip()
            prefixes.append(match[1])
            part = remaining
    clean = strip_prefix(clean)
    chunks = [p.strip() for p in clean.split(',')]
    while len(chunks) > 1 and SUFFIX.fullmatch(chunks[-1]):
        suffixes.insert(0, chunks.pop())
    review = False
    if len(chunks) == 2 and all(chunks):
        family, given = strip_prefix(chunks[0]), strip_prefix(chunks[1])
        family_words = family.split()
        if len(family_words) > 1 and SUFFIX.fullmatch(family_words[-1]):
            suffixes.append(family_words.pop())
            family = ' '.join(family_words)
        normalized, method = given + ' ' + family, 'family_given_reordered'
    elif len(chunks) == 1:
        normalized, method = chunks[0], 'given_order_retained'
    else:
        # Multiple names/commas have no safe automatic interpretation.
        normalized, method, review = clean, 'ambiguous_retained', True
    words = normalized.split()
    if words and SUFFIX.fullmatch(words[-1]) and len(words) > 2:
        suffixes.append(words.pop())
        normalized = ' '.join(words)
    if not normalized:
        method = 'empty'
    elif len(normalized.split()) < 2:
        review = True
    return dict(name=re.sub(r"[,\.\s]", "", normalized), name_original=original, name_normalized=normalized,
                name_prefix='; '.join(prefixes), name_suffix='; '.join(suffixes),
                name_normalization_method=method, name_normalization_review='true' if review else 'false')


def normalize_record(row):
    out = dict(row)
    out.update(normalize_name(row.get('name_original', row.get('name', ''))))
    return out


def match_text(value):
    value = ''.join(c for c in unicodedata.normalize('NFD', str(value)) if not unicodedata.combining(c)).lower()
    return ' '.join(re.sub(r'[^a-z0-9 -]', ' ', value).replace('-', ' ').split())


def person_key(value):
    value = ''.join(c for c in unicodedata.normalize('NFD', str(value)) if not unicodedata.combining(c)).lower()
    tokens = re.sub(r'[^a-z0-9 -]', ' ', value).split()
    return tokens[0] + '|' + tokens[-1] if len(tokens) > 1 else (tokens[0] if tokens else '')
