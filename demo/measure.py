#!/usr/bin/env python3
"""Open the two order overview pages in the running ShopReports app and measure each:
database selects (Prometheus mx_runtime_stats_connectionbus_selects_total, from
`mxcli run --local --metrics`) and time until the grid shows its rows.
Usage: python3 measure.py [runs]   (writes measure.json next to this file)"""
import json, os, re, statistics, sys, time, urllib.request
from playwright.sync_api import sync_playwright

APP, PROM = 'http://127.0.0.1:8080/', 'http://127.0.0.1:8090/prometheus'
PAGES = [('classic', 'Orders (classic)'), ('view', 'Orders (view entity)')]


def selects():
    txt = urllib.request.urlopen(PROM).read().decode()
    return sum(float(m) for m in re.findall(r'^mx_runtime_stats_connectionbus_selects_total\{[^}]*\} ([\d.e+]+)', txt, re.M))


def main(runs):
    res = {k: [] for k, _ in PAGES}
    with sync_playwright() as p:
        exe = os.environ.get('CHROMIUM')
        b = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
        pg = b.new_page(viewport={'width': 1400, 'height': 900})
        for r in range(runs + 1):                      # run 0 warms caches and is not counted
            for key, caption in PAGES:
                pg.goto(APP); pg.wait_for_load_state('networkidle')
                pg.get_by_text('Welcome to your homepage').wait_for()
                time.sleep(0.5)
                s0 = selects(); t0 = time.perf_counter()
                pg.locator('a', has_text=caption).first.click(force=True)
                pg.get_by_text('SO-', exact=False).first.wait_for(timeout=60000)
                pg.wait_for_load_state('networkidle')
                ms = (time.perf_counter() - t0) * 1000
                time.sleep(0.5)
                n = selects() - s0
                if r: res[key].append({'ms': round(ms), 'selects': n})
                if r == runs: pg.screenshot(path=os.path.join(os.path.dirname(__file__), f'measure-{key}.png'))
        b.close()
    out = {k: {'runs': v, 'median_ms': statistics.median(x['ms'] for x in v),
               'median_selects': statistics.median(x['selects'] for x in v)} for k, v in res.items()}
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'measure.json'), 'w'), indent=2)
    print(json.dumps({k: (v['median_ms'], v['median_selects']) for k, v in out.items()}))


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 5)
