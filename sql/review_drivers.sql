-- Matched calendar cutoffs; category and region are alternative, overlapping views.
WITH scoped AS (
 SELECT CASE WHEN :scope='category' THEN category ELSE region END member,
 order_id,sales_units,
 CASE WHEN order_date BETWEEN :start AND :end THEN 'current' ELSE 'prior' END period
 FROM lines WHERE (order_date BETWEEN :start AND :end) OR (order_date BETWEEN :prior_start AND :prior_end)
)
SELECT member,
 SUM(CASE WHEN period='current' THEN sales_units ELSE 0 END) current_sales_units,
 SUM(CASE WHEN period='prior' THEN sales_units ELSE 0 END) prior_sales_units,
 COUNT(DISTINCT CASE WHEN period='current' THEN order_id END) current_orders,
 COUNT(DISTINCT CASE WHEN period='prior' THEN order_id END) prior_orders
FROM scoped GROUP BY member;
