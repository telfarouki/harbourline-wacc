#!/usr/bin/env python3
"""Load weekly reference-data files into the Supabase table market_snapshots (runs in GitHub Actions).
Env: SUPABASE_URL, SUPABASE_SERVICE_KEY.  Args: one or more weekly JSON files (research/SCHEMA.md format).
A file for a week that is already stored replaces that week's row."""
import json, os, sys, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate import check, iso3_list

URL = os.environ['SUPABASE_URL'].rstrip('/')
KEY = os.environ['SUPABASE_SERVICE_KEY']
codes = iso3_list(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
failed = False
for path in sys.argv[1:]:
    with open(path, encoding='utf-8') as f: doc = json.load(f)
    errs = check(doc, codes)
    if errs:
        failed = True
        print(f'{path}: NOT imported, {len(errs)} problem(s)'); [print('  -', x) for x in errs[:40]]
        continue
    row = {'week': doc['week'], 'as_of': doc['as_of'], 'global': doc['global'], 'countries': doc['countries'],
           'changes': doc.get('changes') or [], 'source_file': path}
    r = urllib.request.Request(URL + '/rest/v1/market_snapshots?on_conflict=week', data=json.dumps([row]).encode(), method='POST',
        headers={'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json',
                 'Prefer': 'resolution=merge-duplicates,return=minimal'})
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            print(f'{path}: week {doc["week"]} stored ({len(doc["countries"])} countries, {len(row["changes"])} changes) — HTTP {resp.status}')
    except urllib.error.HTTPError as e:
        failed = True
        print(f'{path}: Supabase refused the import: {e.code} {e.read().decode()[:400]}')
sys.exit(1 if failed else 0)
