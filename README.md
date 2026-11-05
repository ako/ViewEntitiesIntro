# Mendix View Entities: intro deck

A Sketch Deck ([ako/inkscape-presenter](https://github.com/ako/inkscape-presenter)) introducing view entities in Mendix: the problem, the solution, how it works, why it is the right solution, tips, and how to build and measure them with mxcli and its analyze-runtime skill. It is written for Mendix developers, support and pre-sales.

| File | What it is |
|---|---|
| `view-entities.html` | The Sketch Deck page, with the finished slides in its clean layer |
| `deck.py` | The deck script: every slide, build step and narration line |
| `make.py` | Draws the deck, renders `render/slide-NN.png`, and builds `presentation.html`, `drawing.svg` and `frames.json` |
| `presentation.html` | Standalone offline presentation |
| `drawing.svg` | Inkscape drawing, using inkscape-presenter layer conventions |
| `view-entities.mp4` | Narrated video, made with `deck_video.py` |
| `demo/` | `ShopReports` Mendix 11.16 app bootstrapped with mxcli: example view entities (`view-entities.mdl`), the SQL the runtime sends (`sql-trace.md`), before/after pages (`app/mdlsource/performance-demo.mdl`), demo data (`seed-demo-data.sql`) and the measurement (`measure.py`, `measure.json`, `trace-*.log`) |

## Rebuild

```bash
export CHROMIUM=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome   # if needed
python3 make.py --shots
python3 deck_video.py presentation.html -o view-entities.mp4
```

## Demo app

```bash
cd demo/app
./mxcli check ../view-entities.mdl -p ShopReports.mpr --references
./mxcli docker check -p ShopReports.mpr      # real mx check: 0 errors on 11.16.0
./mxcli run --local --setup --ensure-db -p ShopReports.mpr && ./mxcli run --local --detach -p ShopReports.mpr
./mxcli oql -p ShopReports.mpr "SELECT v.CustomerName, v.OrderTotal FROM Shop.OrderOverview AS v"
```
