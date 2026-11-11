#!/usr/bin/env python3
"""Check a weekly reference-data file against research/SCHEMA.md.  Usage: validate.py weekly/2026-W46.json
Prints the problems and exits 1, or prints OK and exits 0."""
import json, os, re, sys

DATE = re.compile(r'\d{4}-\d{2}-\d{2}$')
OUTLOOKS = {'positive', 'stable', 'negative', 'watch', None}

def iso3_list(root):
    with open(os.path.join(root, 'countries.js'), encoding='utf-8') as f:
        return sorted(set(re.findall(r'\["([A-Z]{3})"', f.read())))

def num(v, lo, hi):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and lo <= v <= hi

def url(v):
    return isinstance(v, str) and v.startswith('https://')

def check(doc, codes):
    e = []
    if not re.fullmatch(r'\d{4}-W\d{2}', str(doc.get('week', ''))): e.append('week must look like 2026-W46')
    if not DATE.match(str(doc.get('as_of', ''))): e.append('as_of must be YYYY-MM-DD')
    g = doc.get('global') or {}
    if not num(g.get('us10y_pct'), 0, 20): e.append('global.us10y_pct missing or out of range')
    if not DATE.match(str(g.get('us10y_date', ''))): e.append('global.us10y_date must be YYYY-MM-DD')
    if not url(g.get('us10y_source_url')): e.append('global.us10y_source_url missing')
    if g.get('mature_erp_pct') is not None and not num(g['mature_erp_pct'], 1, 15): e.append('global.mature_erp_pct out of range')
    cs = doc.get('countries')
    if not isinstance(cs, dict): return e + ['countries must be an object keyed by ISO3']
    for c in codes:
        if c not in cs: e.append(f'{c}: missing')
    for c, v in cs.items():
        if c not in codes: e.append(f'{c}: not a code of countries.js'); continue
        if not isinstance(v, dict): e.append(f'{c}: entry must be an object'); continue
        r = v.get('ratings')
        if not isinstance(r, dict): e.append(f'{c}: ratings missing'); r = {}
        for a in ('moodys', 'sp', 'fitch'):
            x = r.get(a)
            if x is None: continue
            if not isinstance(x, dict) or not x.get('rating'): e.append(f'{c}.{a}: rating missing'); continue
            if x.get('outlook') not in OUTLOOKS: e.append(f'{c}.{a}: outlook {x.get("outlook")!r} not allowed')
            if not url(x.get('source_url')): e.append(f'{c}.{a}: source_url missing')
        t = v.get('corporate_tax_pct')
        if t is not None:
            if not num(t, 0, 60): e.append(f'{c}: corporate_tax_pct out of range')
            if not url(v.get('tax_source_url')): e.append(f'{c}: tax_source_url missing')
        b = v.get('eurobond')
        if b is not None:
            if not isinstance(b, dict) or not num(b.get('yield_pct'), 0, 100): e.append(f'{c}: eurobond.yield_pct missing or out of range')
            elif not url(b.get('source_url')): e.append(f'{c}: eurobond.source_url missing')
        s = v.get('project_spread_pct')
        if s is not None:
            if not num(s, 0, 20): e.append(f'{c}: project_spread_pct out of range')
            if not url(v.get('project_spread_source_url')): e.append(f'{c}: project_spread_source_url missing')
        if not DATE.match(str(v.get('checked', ''))): e.append(f'{c}: checked must be YYYY-MM-DD')
        if all(r.get(a) is None for a in ('moodys', 'sp', 'fitch')) and t is None and not v.get('note'):
            e.append(f'{c}: no rating and no tax rate — explain in note')
    for i, ch in enumerate(doc.get('changes') or []):
        if not isinstance(ch, dict) or ch.get('iso3') not in codes or not ch.get('what'): e.append(f'changes[{i}]: needs iso3 and what')
    return e

if __name__ == '__main__':
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    codes = iso3_list(root)
    bad = False
    for p in sys.argv[1:]:
        with open(p, encoding='utf-8') as f: doc = json.load(f)
        errs = check(doc, codes)
        if errs:
            bad = True
            print(f'{p}: {len(errs)} problem(s)'); [print('  -', x) for x in errs[:80]]
        else:
            print(f'{p}: OK ({len(doc["countries"])} countries)')
    sys.exit(1 if bad else 0)
