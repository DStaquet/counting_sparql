CREATE TABLE delta_Agg AS
SELECT Agg.product,
       (CAST (delta_Agg.value1 AS INT) + CAST (Agg.value1 AS INT)) AS value1,
       1 AS k_count
FROM delta_Project_6206501852706074180 AS delta_Agg, Project_6206501852706074180 AS Agg
WHERE (delta_Agg.product = Agg.product) AND delta_Agg.product IN (SELECT product FROM Project_6206501852706074180)
UNION
SELECT Agg.product,
       Agg.value1 AS value1,
       -Agg.k_count AS k_count
FROM Project_6206501852706074180 AS Agg, delta_Project_6206501852706074180 AS delta_Agg
WHERE delta_Agg.product = Agg.product
UNION
SELECT delta_Agg.product,
       (CAST (Agg.value1 AS INT) - CAST (delta_Agg.value1 AS INT)) AS value1,
       1 AS k_count
FROM delta_Project_6206501852706074180 AS delta_Agg, Project_6206501852706074180 AS Agg
WHERE (delta_Agg.product = Agg.product) AND delta_Agg.product NOT IN (SELECT product FROM nu_Project_6206501852706074180);

CREATE TABLE nu_Agg_increm AS
SELECT (CASE
            WHEN R1.product NOT NULL THEN R1.product
            ELSE R2.product
        END) AS product,
         (CASE
            WHEN R1.value1 NOT NULL THEN CAST (R1.value1 AS INT)
            ELSE CAST (R2.value1 AS INT)
        END) AS value1,
         (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
        END) AS k_count
FROM Agg AS R1
FULL OUTER JOIN delta_Agg AS R2 ON R1.product = R2.product
AND R1.value1 = R2.value1
WHERE coalesce(R1.k_count, 0) + coalesce(R2.k_count, 0) > 0;