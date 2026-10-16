SELECT substr(l.order_date,1,7) month,l.category,COUNT(*) lines,SUM(l.sales_units) sales_units,
 COALESCE(n.owner,'') owner,COALESCE(n.status,'Not started') status,COALESCE(n.note,'') note
FROM lines l LEFT JOIN notes n ON n.month=substr(l.order_date,1,7) AND n.category=l.category
GROUP BY substr(l.order_date,1,7),l.category ORDER BY month,l.category;
