CREATE TABLE Agg AS
SELECT product_id, SUM(CAST (value1 AS INT) * k_count) as value1, 1 as k_count
FROM Products
GROUP BY product_id;

/* CREATE TABLE Agg AS
SELECT product_id,
        SUM(CAST (value1 AS INT) * k_count) AS value1,
        1 AS k_count
FROM Products
GROUP BY product_id; */