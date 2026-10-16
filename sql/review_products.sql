WITH scoped AS (
 SELECT product_id,
 SUM(CASE WHEN order_date BETWEEN :start AND :end THEN sales_units ELSE 0 END) current_sales_units,
 SUM(CASE WHEN order_date BETWEEN :prior_start AND :prior_end THEN sales_units ELSE 0 END) prior_sales_units
 FROM lines WHERE ((:scope='category' AND category=:member) OR (:scope='region' AND region=:member))
 AND ((order_date BETWEEN :start AND :end) OR (order_date BETWEEN :prior_start AND :prior_end))
 GROUP BY product_id
) SELECT *,current_sales_units-prior_sales_units change_units FROM scoped
WHERE current_sales_units<prior_sales_units ORDER BY change_units,product_id LIMIT 3;
