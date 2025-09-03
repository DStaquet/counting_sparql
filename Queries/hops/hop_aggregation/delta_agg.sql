CREATE TABLE delta_Agg AS
SELECT delta_Agg.y AS y,
       (COUNT(delta_Agg.x) + COUNT(Agg.x)) AS x, 
       1 AS k_count
FROM delta_Project_8618330694388824078 AS delta_Agg, Project_8618330694388824078 AS Agg
WHERE (delta_Agg.y = Agg.y) AND delta_Agg.y IN (SELECT y FROM Project_8618330694388824078)
GROUP BY delta_Agg.y
UNION
SELECT Agg.y,
       COUNT(Agg.x) AS x,
       -Agg.k_count AS k_count
FROM Project_8618330694388824078 AS Agg, delta_Project_8618330694388824078 AS delta_Agg
WHERE delta_Agg.y = Agg.y
GROUP BY Agg.y, Agg.k_count
UNION
SELECT delta_Agg.y,
       (COUNT(Agg.x) - COUNT(delta_Agg.x)) AS x,
       1 AS k_count
FROM delta_Project_8618330694388824078 AS delta_Agg, Project_8618330694388824078 AS Agg
WHERE (delta_Agg.y = Agg.y) AND delta_Agg.y NOT IN (SELECT y FROM nu_Project_8618330694388824078)
GROUP BY delta_Agg.y;

CREATE TABLE nu_Agg_increm AS
SELECT (CASE
            WHEN R1.y NOT NULL THEN R1.y
            ELSE R2.y
        END) AS y,
         (CASE
            WHEN R1.x NOT NULL THEN CAST (R1.x AS INT)
            ELSE CAST (R2.x AS INT)
        END) AS x,
         (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
        END) AS k_count
FROM Agg AS R1
FULL OUTER JOIN delta_Agg AS R2 ON R1.y = R2.y
AND R1.x = R2.x
WHERE coalesce(R1.k_count, 0) + coalesce(R2.k_count, 0) > 0;