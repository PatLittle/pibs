#!/usr/bin/env python3
"""Verify graph assets against canonical inputs, including lazy evidence shards."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build_graph import build


def validate(root=ROOT):
    root = Path(root)
    actual = json.loads((root / 'site/data/graph.json').read_text())
    evidence = {}
    expected_files = actual.pop('evidence_files')
    for path, checksum in expected_files.items():
        raw = (root / 'site' / path).read_bytes()
        if hashlib.sha256(raw).hexdigest() != checksum:
            raise ValueError(f'Evidence checksum mismatch: {path}')
        evidence[path] = json.loads(raw)
    used = set()
    for edge in actual['edges']:
        path = edge.pop('evidence_url')
        count = edge.pop('evidence_count')
        edge['evidence'] = evidence[path][edge['id']]
        used.add((path, edge['id']))
        if not edge['evidence'] or len(edge['evidence']) != count:
            raise ValueError(f'Missing evidence for {edge["id"]}')
    if used != {(path, ident) for path, items in evidence.items() for ident in items}:
        raise ValueError('Orphan evidence in graph assets')
    expected = build(root)
    if expected != actual:
        raise ValueError('Graph assets are stale; run python scripts/build_graph.py')
    ids = {n['id'] for n in actual['nodes']}
    if len(ids) != len(actual['nodes']): raise ValueError('Duplicate node identifiers')
    if any(e['source'] not in ids or e['target'] not in ids for e in actual['edges']):
        raise ValueError('Dangling graph edges')
    print(f'Validated graph and {len(evidence)} evidence shards: {actual["summary"]}')


if __name__ == '__main__': validate()
