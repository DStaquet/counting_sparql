CREATE TABLE nu_Agg AS
SELECT product_id, SUM(CAST (value1 AS INT) * k_count) as value1, 1 as k_count
FROM nu_Products
GROUP BY product_id;