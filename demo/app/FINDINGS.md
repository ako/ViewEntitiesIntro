
## View entity deck: performance demo (2026-11-05)

- Added `Shop.Orders_Classic` (Data grid 2 over SalesOrder, associated customer column, calculated `OrderTotalCalc`) and
  `Shop.Orders_View` (same grid over the `Shop.OrderOverview` view entity). Seeded with `../seed-demo-data.sql`.
- Measured with `../measure.py` (Prometheus `mx_runtime_stats_connectionbus_selects_total` delta per page load, 5 runs):
  classic 25 selects, view entity 3. PostgreSQL statement log: classic 23 statements on shop tables
  (20 are one `shop$orderline` query per row from the calculated attribute), view entity 2 (page + count).
  Wall time locally is similar (~230-250 ms median); the difference is round trips.
- `mxcli log set ConnectionBus_Queries TRACE` was accepted, but no query lines appeared in `.mxcli/runtime.log`
  after the runtime logged "Logging to file: .../runtime.log". Used PostgreSQL `log_statement=all` instead.
