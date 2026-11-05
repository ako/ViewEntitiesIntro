-- Demo data for the ShopReports app (Mendix IDs: short_id << 48 | sequence << 7).
-- 8 categories, 60 products, 500 customers, 5,000 orders, 25,000 order lines.
-- Short ids are this database's (see mendixsystem$entityidentifier); restart the app after seeding.
begin;
insert into "shop$category"(id, name)
select (56::bigint<<48)|(g::bigint<<7), (array['Bikes','Helmets','Lights','Locks','Tyres','Clothing','Tools','Bags'])[g]
from generate_series(1,8) g;
insert into "shop$product"(id, name, price, "shop$product_category")
select (32::bigint<<48)|(g::bigint<<7), 'Product '||g, round((5+random()*495)::numeric,2), (56::bigint<<48)|((1+g%8)::bigint<<7)
from generate_series(1,60) g;
insert into "shop$customer"(id, name, country)
select (1::bigint<<48)|(g::bigint<<7), 'Customer '||lpad(g::text,3,'0'), (array['NL','BE','DE','UK','US'])[1+g%5]
from generate_series(1,500) g;
insert into "shop$salesorder"(id, ordernumber, orderdate, status, "shop$salesorder_customer")
select (14::bigint<<48)|(g::bigint<<7), 'SO-'||lpad(g::text,5,'0'), timestamp '2025-01-01' + (g*137 % 670) * interval '1 day', 'Open',
       (1::bigint<<48)|((1+g%500)::bigint<<7)
from generate_series(1,5000) g;
insert into "shop$orderline"(id, quantity, unitprice, "shop$orderline_product", "shop$orderline_salesorder")
select (19::bigint<<48)|(g::bigint<<7), 1+g%5, round((5+random()*495)::numeric,2),
       (32::bigint<<48)|((1+g%60)::bigint<<7), (14::bigint<<48)|((1+(g-1)/5)::bigint<<7)
from generate_series(1,25000) g;
update mendixsystem$entityidentifier ei set object_sequence = v.n
from mendixsystem$entity e, (values ('Shop.Category',9),('Shop.Product',61),('Shop.Customer',501),('Shop.SalesOrder',5001),('Shop.OrderLine',25001)) v(name,n)
where e.id = ei.id and e.entity_name = v.name;
commit;
