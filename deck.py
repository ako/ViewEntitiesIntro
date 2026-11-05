#!/usr/bin/env python3
"""Mendix View Entities: the deck script.

    python3 deck.py            # draws the slides into view-entities.html

build(html) draws every slide into a Sketch Deck page and returns the frames
as [(frame_id, x, y, w, h, t), ...]; examples/build.py-style builders use it to
make the standalone presentation for the video. Every slide and build step
carries its narration line (data-say).
"""
from slide_kit import *

W_, H_ = LOCAL_W, LOCAL_H
COLS, GAP = 4, 220
DARK = "#16232b"; CODEFG = "#dfe6ec"; GREEN = "#2f8f5b"; GT = "#e3f2ea"; RT = "#fbe5dc"


# ---------- small drawing helpers ----------

def entity(x, y, w, name, attrs, kind="p", row=34, fs=21):
    """A domain-model entity box. kind p = persistent (cobalt), v = view (amber)."""
    head, fill, tint = (COB, COB, CT) if kind == "p" else (AMB, AMB, AT)
    h = 50 + row * len(attrs) + 10
    s = rect(x, y, w, h, W, head, 3, 10)
    s += f'<path d="M{x} {y+10}Q{x} {y} {x+10} {y}L{x+w-10} {y}Q{x+w} {y} {x+w} {y+10}L{x+w} {y+50}L{x} {y+50}Z" fill="{fill}"/>'
    s += text(x + 16, y + 34, fs + 2, name, "d5", W if kind == "p" else INK)
    for i, a in enumerate(attrs):
        s += text(x + 16, y + 50 + row * (i + 0.5) + 12, fs, a, "m", INK)
    return s


def ent_h(n, row=34): return 50 + row * n + 10


def code(x, y, w, lines, fs=22, title=None, hl=(), lh=1.5):
    h = len(lines) * fs * lh + 46 + (30 if title else 0)
    s = rect(x, y, w, h, DARK, DARK, 0, 12)
    yy = y + 40
    if title:
        s += text(x + 22, yy - 4, 17, title.upper(), "m", AMB, weight=500); yy += 32
    for i, l in enumerate(lines):
        col = AMB if i in hl else CODEFG
        if l.strip():
            s += f'<text class="m" x="{x+22}" y="{yy}" font-size="{fs}" style="fill:{col};white-space:pre" xml:space="preserve">{E(l)}</text>'
        yy += fs * lh
    return s


def code_h(n, fs=22, title=False, lh=1.5): return n * fs * lh + 46 + (30 if title else 0)


def pill(x, y, w, label, fill=CT, fg=COB, h=44, fs=20):
    return rect(x, y, w, h, fill, fill, 0, h / 2) + text(x + w / 2, y + h / 2 + fs * 0.36, fs, label, "m", fg, "middle", 500)


def card_box(x, y, w, h, title, lines, accent=COB, tint=CT, ts=26, fs=21, lc=MUT):
    s = rect(x, y, w, h, W, HAIR, 2, 14) + f'<rect x="{x}" y="{y}" width="8" height="{h}" rx="4" fill="{accent}"/>'
    s += text(x + 30, y + 46, ts, title, "d5", INK)
    yy = y + 46 + ts * 0.6 + 26
    for l in lines:
        s += text(x + 30, yy, fs, l, "b", lc); yy += fs * 1.45
    return s


def cross(cx, cy, r=13):
    return dot(cx, cy, r, RED) + f'<path d="M{cx-r*.4} {cy-r*.4}L{cx+r*.4} {cy+r*.4}M{cx+r*.4} {cy-r*.4}L{cx-r*.4} {cy+r*.4}" stroke="#fff" stroke-width="{r*.28}" stroke-linecap="round"/>'


def partial(cx, cy, r=13):
    return dot(cx, cy, r, AMB) + f'<path d="M{cx-r*.45} {cy}L{cx+r*.45} {cy}" stroke="#fff" stroke-width="{r*.3}" stroke-linecap="round"/>'


def grid_widget(x, y, w, cols, rows, title=None, hl_col=None, fs=19):
    """A data grid: header row plus body rows (lists of strings)."""
    rh = 42
    h = rh * (len(rows) + 1) + (44 if title else 0)
    s = rect(x, y, w, h, W, INK, 2.5, 10)
    yy = y
    if title:
        s += text(x + 18, y + 30, 20, title, "d5", INK); yy += 44
        s += line(x, yy, x + w, yy, HAIR, 2)
    cw = [w * c[1] for c in cols]
    cx = [x + sum(cw[:i]) for i in range(len(cols))]
    if hl_col is not None:
        s += f'<rect x="{cx[hl_col]}" y="{yy}" width="{cw[hl_col]}" height="{rh*(len(rows)+1)}" fill="{AT}"/>'
    s += f'<rect x="{x+1.5}" y="{yy}" width="{w-3}" height="{rh}" fill="{PAPER}"/>'
    for i, (c, _) in enumerate(cols):
        s += text(cx[i] + 14, yy + 28, fs, c, "b", INK, weight=600)
    for r_, row in enumerate(rows):
        ry = yy + rh * (r_ + 1)
        s += line(x, ry, x + w, ry, HAIR, 1.5)
        for i, v in enumerate(row):
            s += text(cx[i] + 14, ry + 28, fs, v, "m" if any(ch.isdigit() for ch in v) else "b", INK)
    return s


def label(x, y, t, fill=MUT, fs=19, anchor="start"):
    return text(x, y, fs, t, "m", fill, anchor, 500)


# ---------- the slides ----------

def s01():  # title
    v = text(90, 300, 21, "MENDIX · INTRODUCTION", "m", AMB, weight=500)
    v += text(90, 410, 104, "View", "d") + text(90, 530, 104, "entities", "d")
    v += text(90, 620, 32, "Query-shaped data, with the full entity API.", "b", MUT)
    v += text(90, 800, 22, "For Mendix developers, support and pre-sales", "m", MUT)
    # right: entities -> OQL -> view entity -> consumers
    ex = 960
    v += entity(ex, 150, 250, "SalesOrder", ["OrderDate"], row=32, fs=19)
    v += entity(ex, 290, 250, "Customer", ["Name"], row=32, fs=19)
    v += entity(ex, 430, 250, "OrderLine", ["Quantity"], row=32, fs=19)
    for yy in (196, 336, 476):
        v += curve(ex + 255, yy, 1290, 360, COB, 3)
    v += code(1270, 300, 140, ["OQL"], 26)
    v += entity(1300, 560, 300, "OrderOverview", ["CustomerName", "OrderTotal"], "v", row=32, fs=19)
    v += line(1340, 385, 1340, 548, COB, 3, arrow=True)
    v += text(1600, 790, 20, "grids · charts · APIs · microflows", "m", MUT, "end")
    return dict(n=1, label="Intro", title="View entities", body="", visual=v, full=True,
                say="View entities in Mendix: data in exactly the shape a page, chart or API needs, "
                    "with everything you expect from a normal entity.")


def s02():  # roadmap
    qs = [("01", "The problem", "Pages need data in another shape than the model"),
          ("02", "The solution", "An entity defined by an OQL query"),
          ("03", "How it works", "Design time, run time, composition, security"),
          ("04", "Why it is right", "Compared with the usual workarounds"),
          ("05", "Tips and tricks", "Modelling, OQL gotchas, support checklist")]
    v = ""
    for i, (n, t, sub) in enumerate(qs):
        y = 150 + i * 140
        v += step(f"q{i}", t, rect(80, y, 860, 112, W, HAIR, 2, 14) +
                  text(120, y + 70, 40, n, "d", AMB) + text(220, y + 52, 30, t, "d5") + text(220, y + 88, 21, sub, "b", MUT))
    return dict(n=2, label="Agenda", title="Five questions",
                body="Written for developers who build with it, support engineers who troubleshoot it, "
                     "and pre-sales who explain it.", visual=v,
                say="We will answer five questions: what problem view entities solve, what they are, "
                    "how they work, why they are the right answer, and how to use them well.")


def s03():  # the problem: model shape vs page shape
    v = label(80, 140, "DOMAIN MODEL: SHAPED FOR STORAGE")
    v += entity(80, 160, 250, "Customer", ["Name", "Country"], row=32, fs=19)
    v += entity(380, 160, 250, "SalesOrder", ["OrderNumber", "OrderDate"], row=32, fs=19)
    v += entity(680, 160, 250, "OrderLine", ["Quantity", "UnitPrice"], row=32, fs=19)
    v += line(330, 205, 380, 205, INK, 2.5) + line(630, 205, 680, 205, INK, 2.5)
    page = label(80, 470, "PAGE: SHAPED FOR PEOPLE")
    page += grid_widget(80, 490, 850, [("Order", .2), ("Date", .2), ("Customer", .3), ("Lines", .12), ("Total", .18)],
                        [["SO-1041", "3 Nov", "Acme Corp", "4", "1,280.00"],
                         ["SO-1042", "3 Nov", "Globex", "2", "310.50"],
                         ["SO-1043", "4 Nov", "Initech", "7", "4,912.75"]], "Order overview")
    links = curve(205, 286, 600, 580, AMB, 3, dash="8 7") + curve(805, 286, 820, 580, AMB, 3, dash="8 7") + curve(805, 286, 900, 580, AMB, 3, dash="8 7")
    links += label(560, 445, "join + count + sum", AMB)
    return dict(n=3, label="The problem", title="Model shape is not page shape",
                body="An order overview needs the customer's name, a line count and a total. "
                     "None of those are attributes of SalesOrder.",
                visual=v + step("page", "The page", page, say="But the page people want shows orders with a customer name, a line count and a total.")
                + step("gap", "The gap", links, say="Every one of those columns has to be joined, counted or summed from other entities."),
                say="A domain model is shaped for storing data: customers, orders and order lines, each in its own entity.")


def s04():  # workarounds
    cards = [("Calculated attribute", ["A microflow runs per object,", "every time it is read.", "Not sortable or filterable."]),
             ("Microflow + NPE", ["Loads objects into the runtime", "and loops over them.", "Grid loses paging and filters."]),
             ("Associated columns", ["Grid fetches related objects", "page by page: many retrieves.", "Aggregates are not possible."]),
             ("Stored copy", ["Denormalised attribute kept", "in sync by event handlers.", "Extra writes, drift, bugs."])]
    v = ""
    for i, (t, ls) in enumerate(cards):
        x = 80 + (i % 2) * 440; y = 140 + (i // 2) * 360
        v += step(f"w{i}", t, card_box(x, y, 410, 320, t, ls, RED, RT, ts=25, fs=21) + cross(x + 370, y + 40))
    return dict(n=4, label="The problem", title="Four workarounds, four costs",
                body="Each pattern works, but moves the work into the runtime or spreads it over many "
                     "queries. Large data makes it slow; the code makes it hard to change.", visual=v,
                say="Until now we had workarounds. Calculated attributes run a microflow for every object. "
                    "Microflows with non-persistable entities load everything into the runtime. "
                    "Associated grid columns fire many retrieves. Stored copies need event handlers to stay in sync.")


def s05():  # round trips
    v = label(80, 150, "BEFORE: MANY ROUND TRIPS")
    v += rect(80, 170, 200, 70, CT, COB, 2.5, 10) + text(180, 214, 22, "Runtime", "d5", INK, "middle")
    v += rect(760, 170, 200, 70, PAPER, INK, 2.5, 10) + text(860, 214, 22, "Database", "d5", INK, "middle")
    trips = ""
    for i in range(6):
        yy = 270 + i * 30
        trips += line(290, yy, 750, yy, RED if i else INK, 2.5, arrow=True)
    trips += label(300, 470, "1 + N retrieves, totals summed in Java", RED)
    v += step("before", "Before", trips, say="With associated columns and calculated values, one page can mean one retrieve for the orders, "
                                             "then more for customers and lines, with the sums done in the runtime.")
    after = label(80, 560, "AFTER: ONE QUERY")
    after += rect(80, 580, 200, 70, CT, COB, 2.5, 10) + text(180, 624, 22, "Runtime", "d5", INK, "middle")
    after += rect(760, 580, 200, 70, PAPER, INK, 2.5, 10) + text(860, 624, 22, "Database", "d5", INK, "middle")
    after += line(290, 615, 750, 615, COB, 4, arrow=True) + check(520, 680, 15)
    after += label(300, 740, "join, group and sum done by the optimizer", COB)
    v += step("after", "After", after, say="With a view entity it is a single query. The database joins, groups and sums, which is what it is built for.")
    return dict(n=5, label="The problem", title="Where the time goes",
                body="Early adopters report grid pages going from 5-10 seconds to under one second, "
                     "keeping all Data grid 2 features.", visual=v,
                say="So where does the time go?")


SQL_OQL = ["SELECT o.OrderNumber AS OrderNumber,",
           "       o.OrderDate   AS OrderDate,",
           "       c.Name        AS CustomerName,",
           "       count(l.ID)   AS LineCount,",
           "       sum(l.Quantity * l.UnitPrice)",
           "                     AS OrderTotal",
           "FROM Shop.SalesOrder AS o",
           "JOIN o/Shop.SalesOrder_Customer/Shop.Customer AS c",
           "LEFT JOIN o/Shop.OrderLine_SalesOrder/Shop.OrderLine AS l",
           "GROUP BY o.OrderNumber, o.OrderDate, c.Name"]


def s06():  # the solution
    v = code(70, 150, 890, SQL_OQL, 19, "OQL query · Shop.OrderOverview", lh=1.45)
    ent = entity(380, 600, 330, "OrderOverview", ["OrderNumber", "OrderDate", "CustomerName", "LineCount", "OrderTotal"], "v", row=30, fs=19)
    ent += line(545, 560, 545, 595, AMB, 3, arrow=False)
    ent += f'<path d="M538 586L545 598L552 586Z" fill="{AMB}"/>'
    ent += label(730, 640, "a view entity", AMB) + label(730, 668, "in the domain model", MUT)
    return dict(n=6, label="The solution", title="An entity defined by a query",
                body="A view entity lives in the domain model like any other entity, but its rows come from "
                     "an OQL query. Each SELECT alias becomes an attribute.",
                visual=v + step("entity", "The entity", ent, say="Studio Pro turns it into an entity in the domain model. Every column alias becomes an attribute."),
                say="The solution is a view entity: you write one OQL query that returns exactly the rows and columns the page needs.")


def s07():  # design time
    cols = [("OrderNumber", "string(20)"), ("CustomerName", "string(200)"), ("LineCount", "integer"), ("OrderTotal", "decimal")]
    srcs = ["o.OrderNumber", "c.Name", "count(l.ID)", "sum(l.Quantity * l.UnitPrice)"]
    v = label(80, 150, "SELECT COLUMN") + label(620, 150, "VIEW ATTRIBUTE · TYPE")
    for i, (s_, (a, t)) in enumerate(zip(srcs, cols)):
        y = 175 + i * 92
        v += rect(80, y, 440, 64, DARK, DARK, 0, 10) + text(100, y + 41, 19, s_, "m", CODEFG)
        v += line(525, y + 32, 612, y + 32, AMB, 3) + f'<path d="M606 {y+25}L618 {y+32}L606 {y+39}Z" fill="{AMB}"/>'
        v += rect(620, y, 340, 64, AT, AMB, 2, 10) + text(640, y + 41, 20, a, "m", INK) + text(944, y + 41, 17, t, "m", MUT, "end")
    prev = label(80, 575, "RUN QUERY: LIVE PREVIEW")
    prev += grid_widget(80, 595, 880, [("OrderNumber", .25), ("CustomerName", .35), ("LineCount", .17), ("OrderTotal", .23)],
                        [["SO-1041", "Acme Corp", "4", "1280.00"], ["SO-1042", "Globex", "2", "310.50"], ["SO-1043", "Initech", "7", "4912.75"]])
    return dict(n=7, label="How it works", title="Design time",
                body="Write the query in the view entity editor, check the rows with Run Query, and the "
                     "attributes follow. Types must match the source columns exactly.",
                visual=v + step("preview", "Run Query", prev, say="Run Query shows a live preview from your running app, so you see the rows before you build a page."),
                say="At design time, each column of the SELECT maps to an attribute, with its type taken from the source column.")


def s08():  # runtime
    v = rect(80, 150, 260, 96, CT, COB, 2.5, 12) + text(210, 192, 24, "Data grid 2", "d5", INK, "middle") + text(210, 224, 18, "filter · sort · page", "m", MUT, "middle")
    req = line(350, 198, 420, 198, COB, 3, arrow=True)
    req += code(430, 140, 530, ["SELECT ... FROM Shop.OrderOverview", "WHERE OrderTotal > 100", "ORDER BY OrderTotal DESC", "LIMIT 20"], 18, "Request from the widget", hl=(1, 2, 3))
    sql = ['SELECT "v"."CustomerName", "v"."OrderTotal"', "FROM (", '  SELECT "o"."ordernumber" AS "OrderNumber", ...', '         SUM("l"."quantity" * "l"."unitprice")', '  FROM "shop$salesorder" "o"', '  INNER JOIN "shop$customer" "c" ON ...', '  LEFT OUTER JOIN "shop$orderline" "l" ON ...', "  GROUP BY ...", ') "v"', 'WHERE "v"."OrderTotal" > $1', 'ORDER BY "v"."OrderTotal" DESC LIMIT $2']
    wrapd = line(695, 345, 695, 385, COB, 3, arrow=True) + code(80, 395, 880, sql, 17, "SQL sent to PostgreSQL (traced)", hl=(9, 10), lh=1.4)
    db = rect(80, 805, 880, 56, GT, GREEN, 0, 10) + text(520, 841, 20, "one statement · the database optimizer plans it all", "m", GREEN, "middle", 500)
    return dict(n=8, label="How it works", title="Run time: one SQL query",
                body="The view's query is inlined as a subquery. The caller's filter, sort and paging wrap "
                     "around it. No database view, no copy: always current.",
                visual=v + step("req", "Request", req, say="A data grid asks for page one: filtered, sorted, twenty rows.")
                + step("sql", "Inlined", wrapd, say="The runtime inlines the view's query as a subquery and wraps the grid's filter, sort and limit around it.")
                + step("db", "One statement", db, say="That is one SQL statement, so the database optimizer can plan the whole thing."),
                say="At run time, nothing is stored. Let's follow one request.")


def s09():  # composition
    v = entity(80, 160, 230, "OrderLine", ["Quantity"], row=30, fs=18) + entity(80, 300, 230, "SalesOrder", ["OrderDate"], row=30, fs=18) + entity(80, 440, 230, "Product", ["Name"], row=30, fs=18) + entity(80, 580, 230, "Category", ["Name"], row=30, fs=18)
    l1 = "".join(curve(315, y, 400, 380, COB, 2.5) for y in (200, 340, 480, 620))
    l1 += entity(405, 300, 250, "SalesFact", ["OrderYear", "OrderMonth", "CategoryName", "Amount"], "v", row=30, fs=18)
    l1 += label(405, 290, "LAYER 1: FLAT FACTS", AMB)
    l2 = line(660, 380, 700, 380, AMB, 3, arrow=True) + entity(705, 300, 255, "MonthlySales", ["OrderYear", "OrderMonth", "CategoryName", "Revenue"], "v", row=30, fs=18)
    l2 += label(705, 290, "LAYER 2: GROUPED", AMB)
    bars_ = ""
    for i, hgt in enumerate([60, 95, 80, 130, 115, 160]):
        bx = 720 + i * 38
        bars_ += f'<rect x="{bx}" y="{820-hgt}" width="26" height="{hgt}" rx="3" fill="{COB if i % 2 else AMB}"/>'
    l3 = line(830, 470, 830, 640, AMB, 3, arrow=True) + bars_ + line(705, 820, 960, 820, INK, 2)
    l3 += label(405, 700, "still one SQL statement", GREEN) + label(405, 728, "nested subqueries, traced", MUT)
    return dict(n=9, label="How it works", title="Compose views from views",
                body="A view entity can select from other view entities. Build small, readable layers; "
                     "the runtime still sends one statement.",
                visual=v + step("l1", "Facts", l1, say="First a flat fact view: one row per order line, with year, month and category.")
                + step("l2", "Grouped", l2, say="Then a second view groups those facts into revenue per month and category.")
                + step("l3", "Chart", l3, say="A chart uses it directly, and the whole stack is still one SQL statement."),
                say="View entities compose. You can build complex queries from small, simple ones.")


def s10():  # security
    v = entity(80, 170, 280, "Employee", ["Name", "Salary", "Department"], row=30, fs=19)
    v += label(80, 155, "SOURCE: RESTRICTED ROWS")
    v += rect(80, 340, 280, 44, RT, RT, 0, 8) + text(96, 369, 17, "access: HR only", "m", RED, weight=500)
    v += line(370, 230, 470, 230, AMB, 3, arrow=True)
    v += entity(480, 170, 300, "HeadcountByDept", ["Department", "Headcount"], "v", row=30, fs=19)
    v += label(480, 155, "VIEW: ITS OWN ACCESS RULES", AMB)
    v += rect(480, 340, 300, 44, GT, GT, 0, 8) + text(496, 369, 17, "access: all managers", "m", GREEN, weight=500)
    warn = rect(80, 420, 880, 160, AT, AMB, 2, 14) + text(110, 470, 26, "Source rules are not applied", "d5")
    warn += text(110, 512, 21, "The view runs its query without the source entities' access rules.", "b", INK)
    warn += text(110, 545, 21, "Whatever the SELECT returns, its access rules decide who sees it.", "b", INK)
    fix = "".join(text(110, 640 + i * 46, 22, t, "b", INK) + check(90, 633 + i * 46, 11) for i, t in enumerate(
        ["Give every view entity access rules for its roles", "Filter rows in WHERE, or join a CurrentUser view", "Test with each role, not only as administrator"]))
    return dict(n=10, label="How it works", title="Security is the view's own",
                body="Great for exposing aggregates without detail rows. But it is a new door into the data: "
                     "secure it like one.",
                visual=v + step("warn", "Warning", warn, say="The flip side: the source entities' access rules are not applied. The view's own rules decide.")
                + step("fix", "Do this", fix, say="So give every view entity access rules, filter rows by user where needed, and test with each role."),
                say="A view entity has its own access rules. That lets you show headcount per department to managers who may not see individual salaries.")


def s11():  # read vs write
    v = entity(80, 180, 300, "OrderOverview", ["OrderNumber", "CustomerName", "OrderTotal"], "v", row=30, fs=19)
    v += label(80, 165, "VIEW ROW: NO STORAGE", AMB)
    v += rect(80, 345, 380, 44, AT, AT, 0, 8) + text(96, 374, 17, "edit in memory · commit does nothing", "m", INK, weight=500)
    flow = ""
    nodes = [("Retrieve", "SalesOrder by key"), ("Change", "source object"), ("Commit", "SalesOrder")]
    for i, (a, b) in enumerate(nodes):
        x = 80 + i * 300
        flow += rect(x, 520, 260, 110, CT, COB, 2.5, 14) + text(x + 130, 565, 24, a, "d5", INK, "middle") + text(x + 130, 600, 18, b, "m", MUT, "middle")
        if i < 2: flow += line(x + 265, 575, x + 295, 575, COB, 3, arrow=True)
    flow += label(80, 500, "SAVE: A MICROFLOW WRITES THROUGH THE SOURCE ENTITY", COB)
    flow += text(80, 700, 22, "Tip: select the source's ID in the view; it becomes an association", "b", MUT)
    flow += text(80, 732, 22, "you can follow to find the object to change.", "b", MUT)
    return dict(n=11, label="How it works", title="Read here, write there",
                body="A view row has no table behind it. A form may edit it in memory; saving means a microflow "
                     "that changes and commits the source entity.",
                visual=v + step("flow", "Write back", flow, say="To save, a microflow retrieves the source object, changes it and commits it."),
                say="View entities are for reading. A row can be edited in memory, but committing it stores nothing.")


def s12():  # why it's right: comparison table
    crit = ["Work runs in the database", "Grid filter, sort, page", "Reusable and composable", "No sync code to maintain", "Declarative, readable"]
    opts = [("Calculated attr.", "xx-pp+"), ("Microflow + NPE", "xx-x-"), ("Stored copy", "+p+x-"), ("View entity", "+++++")]
    x0, cw, y0, rh = 520, 270, 300, 92
    v = text(90, 150, 21, "12 · WHY IT IS RIGHT", "m", AMB, weight=500)
    v += text(90, 225, 50, "The right tool for read models", "d")
    for j, (o, _) in enumerate(opts):
        x = x0 + j * cw
        if o == "View entity":
            v += rect(x + 8, y0 - 10, cw - 16, rh * (len(crit) + 1) + 10, AT, AMB, 2.5, 14)
        v += text(x + cw / 2, y0 + 50, 22, o, "d5", INK, "middle")
    for i, c in enumerate(crit):
        y = y0 + rh * (i + 1)
        v += line(90, y, x0 + cw * len(opts), y, HAIR, 1.5)
        v += text(90, y + 55, 24, c, "b", INK)
        for j, (_, marks) in enumerate(opts):
            m = marks[i]; cx = x0 + j * cw + cw / 2; cy = y + 47
            v += check(cx, cy, 18) if m == "+" else cross(cx, cy, 18) if m == "x" else partial(cx, cy, 18)
    return dict(n=12, label="Why", title="The right tool for read models", body="", visual=v, full=True,
                say="Why is this the right solution? Compared with the workarounds, only the view entity does the work in the database, "
                    "keeps every grid feature, composes, needs no sync code, and stays readable as one declaration.")


def s13():  # why: entity API & decoupling
    v = entity(80, 360, 300, "View entity", ["the entity API"], "v", row=34, fs=20)
    cons = [("Data grid 2", "filter, sort, page"), ("Charts", "series from a query"), ("Microflow retrieve", "XPath constraints"), ("REST / OData", "published resource"), ("Export / mappings", "same as persistent")]
    c = ""
    for i, (a, b) in enumerate(cons):
        y = 150 + i * 140
        c += rect(560, y, 400, 108, W, HAIR, 2, 14) + text(590, y + 48, 24, a, "d5") + text(590, y + 82, 19, b, "m", MUT)
        c += curve(385, 410, 555, y + 54, AMB, 2.5, arrow=True)
    dec = rect(80, 600, 300, 150, CT, COB, 2, 14) + text(100, 645, 22, "Decoupled", "d5") + text(100, 682, 18, "Refactor the model;", "b", MUT) + text(100, 708, 18, "keep the view's columns,", "b", MUT) + text(100, 734, 18, "and pages and APIs hold.", "b", MUT)
    return dict(n=13, label="Why", title="Everything that takes an entity",
                body="No new widget, no special API: if it takes an entity, it takes a view entity. "
                     "And it shields pages and APIs from model refactoring.",
                visual=v + step("cons", "Consumers", c, say="Data grids, charts, microflow retrieves, published REST and OData resources, exports: if it takes an entity, it takes a view entity.")
                + step("dec", "Decoupling", dec, say="And because pages and APIs depend on the view, you can refactor the domain model behind it without breaking them."),
                say="The second reason: a view entity speaks the entity API that the whole platform already understands.")


def s14():  # use cases
    uc = [("Grid performance", "flatten associated columns"), ("Charting", "aggregate per series"), ("API decoupling", "stable contract"),
          ("Multi-lingual", "join the user's language"), ("Multi-tenant", "filter by tenant"), ("Active vs archived", "partition one table"),
          ("Versioning", "latest version per item"), ("Pivots and export", "one row per report line")]
    v = text(90, 150, 21, "14 · USE CASES", "m", AMB, weight=500) + text(90, 225, 50, "Where teams use them", "d")
    for i, (a, b) in enumerate(uc):
        x = 90 + (i % 4) * 382; y = 300 + (i // 4) * 280
        v += rect(x, y, 350, 240, W, HAIR, 2, 16) + f'<rect x="{x}" y="{y}" width="350" height="8" rx="4" fill="{COB if i < 4 else AMB}"/>'
        v += text(x + 28, y + 80, 44, f"{i+1:02d}", "d", CT if i < 4 else AT)
        v += text(x + 28, y + 150, 26, a, "d5") + text(x + 28, y + 190, 20, b, "b", MUT)
    return dict(n=14, label="Use cases", title="Where teams use them", body="", visual=v, full=True,
                say="Where do teams use them? Faster grids and charts first, then stable APIs, multi-lingual and multi-tenant data, "
                    "archiving, versioning, pivots and exports.")


def tips(n, label_, title, items, say, body):
    v = ""
    for i, (h, d_) in enumerate(items):
        y = 140 + i * 145
        v += rect(80, y, 880, 125, W, HAIR, 2, 14) + text(120, y + 68, 34, f"{i+1}", "d", AMB, "middle")
        v += text(160, y + 52, 25, h, "d5") + text(160, y + 90, 20, d_, "b", MUT)
    return dict(n=n, label=label_, title=title, body=body, visual=v, say=say)


def s15():
    return tips(15, "Tips", "Modelling tips", [
        ("Small views, composed", "A facts view, then grouped views on top. Easy to read and test."),
        ("LEFT JOIN unless rows must drop", "An inner join silently hides orders without lines or a category."),
        ("Sort in the widget, not the view", "ORDER BY needs LIMIT; keep views unsorted and let callers sort."),
        ("No parameters: filter from outside", "XPath on the view's attributes, or join a CurrentUser view."),
        ("Select the source ID", "It becomes an association back to the source, for drill-down and edits.")],
        "Five modelling tips. Keep views small and compose them. Use left joins unless rows should drop. Let the widget sort. "
        "Filter from outside, because views have no parameters. And select the source I D to get an association back.",
        "Habits that keep view entities fast, correct and easy to change.")


def s16():
    return tips(16, "Tips", "OQL gotchas", [
        ("Turn on OQL v2 first", "App settings, Runtime. View entities require it; check existing OQL."),
        ("Types must match exactly", "string(60) over a string(100) column fails: CE6770, out of sync."),
        ("OQL is not quite SQL", "':' divides, '!=' not '<>', count(x.ID) not count(*), enums as 'Text'."),
        ("Run Query needs the running app", "Restart after model changes, or the preview errors out."),
        ("Read the plan in development", "Log node DataStorage_QueryPlan at Debug. Never in production.")],
        "Five gotchas. Switch on O Q L version two first. Attribute types must match their source columns exactly. "
        "O Q L is not quite S Q L: a colon divides, and count takes an I D. Run Query needs the running app. "
        "And read the query plan in development only.",
        "The errors people meet in the first week, and how to avoid them.")


def s17():  # support & pre-sales
    sup = [("Slow page?", "Is the grid on a view? Check the plan for missing indexes."),
           ("Wrong rows visible?", "Check the view's own access rules and WHERE."),
           ("Rows missing?", "Look for an INNER JOIN on an optional association."),
           ("CE6770 on build?", "An attribute type differs from its source column.")]
    pre = [("One query, many consumers", "Grids, charts and APIs from one definition."),
           ("Real performance", "Database work, not runtime loops."),
           ("Standard skill", "OQL reads like SQL, the most known query language."),
           ("Low-code surface", "Widgets, XPath and security stay the same.")]
    v = text(90, 150, 21, "17 · FOR SUPPORT AND PRE-SALES", "m", AMB, weight=500) + text(90, 225, 50, "Talking points", "d")
    a = text(90, 310, 24, "SUPPORT CHECKLIST", "m", COB, weight=500)
    for i, (h, d_) in enumerate(sup):
        y = 340 + i * 135
        a += rect(90, y, 720, 115, W, HAIR, 2, 14) + text(120, y + 48, 24, h, "d5") + text(120, y + 85, 19, d_, "b", MUT)
    b = text(870, 310, 24, "PRE-SALES STORY", "m", AMB, weight=500)
    for i, (h, d_) in enumerate(pre):
        y = 340 + i * 135
        b += rect(870, y, 720, 115, AT, AT, 0, 14) + text(900, y + 48, 24, h, "d5") + text(900, y + 85, 19, d_, "b", INK)
    return dict(n=17, label="Talking points", title="Talking points", body="", full=True,
                visual=v + step("sup", "Support", a, say="For support: a slow page, wrong rows, missing rows or a build error each have a usual cause in the view.")
                + step("pre", "Pre-sales", b, say="For pre-sales: one definition feeds grids, charts and APIs, with real database performance, "
                                                   "a query language people already know, and the low-code surface unchanged."),
                say="A page for support and pre-sales colleagues.")


def s18():  # get started
    tl = [("10.19", "Beta|with OQL v2"), ("10.22", "General|availability"), ("11.0", "OQL Query|editor tab"), ("11.2", "string_agg|aggregate"), ("11.9", "Maia writes|view entities")]
    v = label(80, 150, "TIMELINE")
    v += line(110, 260, 940, 260, HAIR, 4)
    for i, (ver, t) in enumerate(tl):
        x = 140 + i * 195
        v += dot(x, 260, 14, AMB if i == 1 else COB) + text(x, 225, 24, ver, "d5", INK, "middle")
        a_, b_ = t.split("|")
        v += text(x, 305, 18, a_, "b", MUT, "middle") + text(x, 330, 18, b_, "b", MUT, "middle")
    steps_ = ["Enable OQL v2 in App Settings, Runtime", "Add a view entity from the domain model toolbox", "Write the query; check it with Run Query",
              "Add access rules for each user role", "Point a Data grid 2 or chart at it"]
    st = label(80, 420, "FIRST VIEW IN FIVE STEPS")
    for i, t in enumerate(steps_):
        y = 450 + i * 80
        st += rect(80, y, 880, 64, W, HAIR, 2, 12) + dot(122, y + 32, 20, COB) + text(122, y + 40, 22, str(i + 1), "d5", W, "middle") + text(162, y + 41, 23, t, "b", INK)
    return dict(n=18, label="Get started", title="Start with one slow page",
                body="Pick the slowest overview page in your app and rebuild its grid on a view entity. "
                     "Docs: docs.mendix.com/refguide/view-entities",
                visual=v + step("steps", "Five steps", st, say="Enable O Q L version two, add a view entity, write and check the query, add access rules, and point a grid or chart at it."),
                say="View entities have been generally available since Mendix ten point twenty-two and keep improving in Mendix eleven. "
                    "Start with your slowest overview page.")


SLIDES = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13, s14, s15, s16, s17, s18]


def frames():
    out = []
    for i, _ in enumerate(SLIDES):
        x = (i % COLS) * (W_ + GAP); y = (i // COLS) * (H_ + GAP)
        out.append((f"ve{i+1:02d}", x, y, W_, H_, (i + 1) * 10))
    return out


def build(html):
    groups = []
    for f, fn in zip(frames(), SLIDES):
        d = fn()
        g = slide(f, d["n"], d["label"], d["title"], d["body"], d["visual"], full_width=d.get("full", False))
        groups.append(narrate(g, d["say"]))
    inject(html, groups)
    return frames()


if __name__ == "__main__":
    fr = build("view-entities.html")
    print(len(fr), "slides drawn")
