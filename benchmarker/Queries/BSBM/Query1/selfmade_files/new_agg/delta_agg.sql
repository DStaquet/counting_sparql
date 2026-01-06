CREATE TABLE delta_Agg AS
SELECT product_id, SUM(CAST (value1 AS INT) * k_count) as value1, 1 as k_count
FROM delta_Products
GROUP BY product_id;

/* CREATE TABLE nu_Agg_increm AS
SELECT * FROM Agg WHERE NOT EXISTS (SELECT * FROM delta_Agg WHERE delta_Agg.product_id = Agg.product_id)
UNION
SELECT * FROM delta_Agg WHERE NOT EXISTS (SELECT * FROM Agg WHERE Agg.product_id = delta_Agg.product_id)
UNION
SELECT Agg.product_id, CAST (Agg.value1 AS INT) + CAST (delta_Agg.value1 AS INT), 1 as k_count
FROM Agg, delta_Agg
WHERE Agg.product_id = delta_Agg.product_id; */

CREATE TABLE nu_Agg_increm AS
SELECT combined.product_id, SUM(CAST (combined.value1 AS INT)) as value1, 1 as k_count
FROM
(
    SELECT * FROM Agg
    UNION ALL
    SELECT * FROM delta_Agg
) AS combined
GROUP BY combined.product_id;
