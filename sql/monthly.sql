-- A missing delivery is unavailable; an explicit header-only delivery is known zero.
SELECT p.month,p.coverage,
 CASE WHEN p.coverage='Imported' THEN COUNT(l.row_id) END lines,
 CASE WHEN p.coverage='Imported' THEN COUNT(DISTINCT l.order_id) END orders,
 CASE WHEN p.coverage='Imported' THEN COALESCE(SUM(l.sales_units),0) END sales_units
FROM periods p LEFT JOIN lines l ON substr(l.order_date,1,7)=p.month
GROUP BY p.month,p.coverage ORDER BY p.month;
