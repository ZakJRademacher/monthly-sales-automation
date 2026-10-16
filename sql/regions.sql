SELECT region,COUNT(*) lines,COUNT(DISTINCT order_id) orders,SUM(sales_units) sales_units
FROM lines GROUP BY region ORDER BY sales_units DESC,region;
