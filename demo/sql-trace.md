# SQL trace: what the runtime sends for a view entity query

Mendix 11.16.0, PostgreSQL 16, captured with log_statement=all while running OQL through the M2EE admin API (mxcli oql).

## OrderOverview, filtered, sorted and limited by the caller

OQL: `SELECT v.CustomerName, v.OrderTotal FROM Shop.OrderOverview AS v WHERE v.OrderTotal > 100 ORDER BY v.OrderTotal DESC LIMIT 20`

```sql
SELECT "v"."CustomerName", "v"."OrderTotal" FROM ( SELECT "o"."ordernumber" AS "OrderNumber", "o"."orderdate" AS "OrderDate", "c"."name" AS "CustomerName", COUNT("l"."id") AS "LineCount", SUM(("l"."quantity" * "l"."unitprice")) AS "OrderTotal" FROM "shop$salesorder" "o" INNER JOIN "shop$customer" "c" ON "c"."id" = "o"."shop$salesorder_customer" LEFT OUTER JOIN "shop$orderline" "l" ON "l"."shop$orderline_salesorder" = "o"."id" GROUP BY "o"."ordernumber", "o"."orderdate", "c"."name" ) "v" WHERE "v"."OrderTotal" > $1 ORDER BY "v"."OrderTotal" DESC LIMIT $2
```

## MonthlySalesByCategory (a view entity over the SalesFact view entity)

```sql
SELECT "m"."CategoryName", "m"."Revenue" FROM ( SELECT "f"."OrderYear" AS "OrderYear", "f"."OrderMonth" AS "OrderMonth", "f"."CategoryName" AS "CategoryName", SUM("f"."Amount") AS "Revenue" FROM ( SELECT (EXTRACT(YEAR FROM "o"."orderdate"::timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'UTC'))::integer AS "OrderYear", (EXTRACT(MONTH FROM "o"."orderdate"::timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'UTC'))::integer AS "OrderMonth", "cat"."name" AS "CategoryName", ("l"."quantity" * "l"."unitprice") AS "Amount" FROM "shop$orderline" "l" INNER JOIN "shop$salesorder" "o" ON "o"."id" = "l"."shop$orderline_salesorder" INNER JOIN "shop$product" "p" ON "p"."id" = "l"."shop$orderline_product" INNER JOIN "shop$category" "cat" ON "cat"."id" = "p"."shop$product_category" ) "f" GROUP BY "f"."OrderYear", "f"."OrderMonth", "f"."CategoryName" ) "m" WHERE "m"."OrderYear" = $1
```

Both views are inlined as subqueries: one SQL statement, no database view object, and the caller's WHERE / ORDER BY / LIMIT wrapped around it.
