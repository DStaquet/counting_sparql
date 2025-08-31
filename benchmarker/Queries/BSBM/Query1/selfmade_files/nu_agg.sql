CREATE TABLE nu_Agg AS
SELECT product,
        SUM(CAST (value1 AS INT)) AS value1,
        1 AS k_count
FROM nu_Project_6206501852706074180
GROUP BY product;