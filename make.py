#!/usr/bin/env python3
"""Draw the deck and build its outputs.

    python3 make.py [--shots]

1. deck.build() draws every slide into view-entities.html (the Sketch Deck page).
2. A temporary copy is loaded in headless Chromium with the deck's frames, in the
   Clean view, and the page's own Download code writes:
     presentation.html  standalone presentation (input for deck_video.py)
     drawing.svg        Inkscape drawing (inkscape-presenter layer conventions)
     frames.json        ArtifactData batch writes that load the frames into the deck's database
3. --shots also writes render/slide-NN.png, one screenshot per slide.

Set CHROMIUM to a Chromium binary if Playwright's own download is missing.
"""
import json, os, shutil, ssl, sys, tempfile, urllib.request
import deck

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(HERE, 'view-entities.html')
HOOK = ('resize();\nsyncClean();',
        'window.__build = { frames, drawFrames, setView, buildDownload, camG };\nresize();\nsyncClean();')


def fetch_font(route):
    try:
        ctx = ssl.create_default_context(cafile=os.environ.get('SSL_CERT_FILE') or os.environ.get('REQUESTS_CA_BUNDLE') or None)
        req = urllib.request.Request(route.request.url, headers={'User-Agent': route.request.headers.get('user-agent', '')})
        with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
            route.fulfill(status=r.status, body=r.read(),
                          headers={'content-type': r.headers.get('content-type', ''), 'access-control-allow-origin': '*'})
    except Exception:
        route.abort()


def main(shots):
    frames = deck.build(PAGE)
    work = tempfile.mkdtemp(prefix='ve-build-')
    tmp = os.path.join(work, 'deck.html')
    s = open(PAGE).read()
    assert s.count(HOOK[0]) == 1, 'template changed: update HOOK'
    open(tmp, 'w').write(s.replace(HOOK[0], HOOK[1]))
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        exe = os.environ.get('CHROMIUM')
        b = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
        pg = b.new_page(viewport={'width': 1600, 'height': 900})
        pg.route('https://fonts.googleapis.com/**', fetch_font)
        pg.route('https://fonts.gstatic.com/**', fetch_font)
        errors = []
        pg.on('pageerror', lambda e: errors.append(str(e)))
        pg.goto('file://' + tmp)
        pg.wait_for_timeout(500)
        pg.evaluate('''fr => { const t = window.__build;
            fr.forEach(([id, x, y, w, h, n]) => t.frames.set(id, { x, y, w, h, t: n }));
            t.drawFrames(); t.setView('clean'); }''', [list(f) for f in frames])
        pg.evaluate('document.fonts.ready')
        pg.wait_for_timeout(800)
        if shots:
            os.makedirs(os.path.join(HERE, 'render'), exist_ok=True)
            pg.add_style_tag(content='#hint,#hud,#toolbar,#status,.panel{display:none!important}')
            for i, (fid, x, y, w, h, _) in enumerate(frames):
                k = 1600 / w * 0.98
                pg.evaluate(f'''window.__build.camG.setAttribute('transform',
                    'translate(800 450) scale({k}) translate({-(x + w / 2)} {-(y + h / 2)})')''')
                pg.wait_for_timeout(60)
                pg.screenshot(path=os.path.join(HERE, 'render', f'slide-{i+1:02d}.png'))
        out = pg.evaluate('''async () => { const t = window.__build;
            const html = await t.buildDownload('html'), svg = await t.buildDownload('svg');
            return { html: html.text, svg: svg.text, missing: html.failedImages + html.failedFonts + svg.failedImages + svg.failedFonts }; }''')
        b.close()
    shutil.rmtree(work)
    if errors:
        raise SystemExit('page errors: ' + '; '.join(errors))
    if out['missing']:
        print(f'warning: {out["missing"]} images or fonts not embedded')
    open(os.path.join(HERE, 'presentation.html'), 'w').write(out['html'])
    open(os.path.join(HERE, 'drawing.svg'), 'w').write(out['svg'])
    writes = [{'op': 'set', 'collection': 'frames', 'doc_id': fid, 'data': {'x': x, 'y': y, 'w': w, 'h': h, 't': n}}
              for fid, x, y, w, h, n in frames]
    writes.append({'op': 'set', 'collection': 'meta', 'doc_id': 'settings', 'data': {'cols': deck.COLS, 'grid': False}})
    open(os.path.join(HERE, 'frames.json'), 'w').write('[\n' + ',\n'.join(json.dumps(w) for w in writes) + '\n]\n')
    print(f'{len(frames)} slides; presentation.html {len(out["html"]) // 1024} KB, drawing.svg {len(out["svg"]) // 1024} KB')


if __name__ == '__main__':
    main('--shots' in sys.argv)
