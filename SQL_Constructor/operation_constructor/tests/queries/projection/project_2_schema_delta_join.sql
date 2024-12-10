CREATE TEMP TABLE delta_Project_719589965937824876_0 AS
SELECT x,
       SUM(k_count) AS k_count
FROM delta_Union_6981146949604561737_schema_5536938746033674259
GROUP BY x;

CREATE TEMP TABLE delta_Project_719589965937824876_1 AS
SELECT x,
       SUM(k_count) AS k_count
FROM delta_Union_6981146949604561737_schema_388442962187960249
GROUP BY x;

CREATE TABLE delta_Project_719589965937824876 AS
SELECT (CASE
            WHEN R1.x NOT NULL THEN R1.x
            ELSE R2.x
        END) AS x,
       (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
        END) AS k_count
FROM delta_Project_719589965937824876_0 AS R1
FULL OUTER JOIN delta_Project_719589965937824876_1 AS R2 ON R1.x = R2.x;