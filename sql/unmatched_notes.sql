SELECT n.* FROM notes n LEFT JOIN lines l
 ON substr(l.order_date,1,7)=n.month AND l.category=n.category
WHERE l.row_id IS NULL ORDER BY n.month,n.category;
