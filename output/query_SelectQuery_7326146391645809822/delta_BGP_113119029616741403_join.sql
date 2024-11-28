CREATE TEMP TABLE delta_BGP_113119029616741403_2_temp AS
SELECT (CASE
            WHEN R1.z NOT NULL THEN R1.z
            ELSE R2.z
        END) AS z,
       (CASE
            WHEN R1.y1 NOT NULL THEN R1.y1
            ELSE R2.y1
        END) AS y1,
       (CASE
            WHEN R1.x NOT NULL THEN R1.x
            ELSE R2.x
        END) AS x,
       (CASE
            WHEN R1.y2 NOT NULL THEN R1.y2
            ELSE R2.y2
        END) AS y2,
       (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
        END) AS k_count
FROM delta_BGP_113119029616741403_1 AS R1
FULL OUTER JOIN delta_BGP_113119029616741403_2 AS R2 ON R1.z = R2.z
AND R1.y1 = R2.y1
AND R1.x = R2.x
AND R1.y2 = R2.y2;

CREATE TABLE delta_BGP_113119029616741403 AS
SELECT (CASE
            WHEN R1.z NOT NULL THEN R1.z
            ELSE R2.z
        END) AS z,
       (CASE
            WHEN R1.y1 NOT NULL THEN R1.y1
            ELSE R2.y1
        END) AS y1,
       (CASE
            WHEN R1.x NOT NULL THEN R1.x
            ELSE R2.x
        END) AS x,
       (CASE
            WHEN R1.y2 NOT NULL THEN R1.y2
            ELSE R2.y2
        END) AS y2,
       (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
        END) AS k_count
FROM delta_BGP_113119029616741403_2_temp AS R1
FULL OUTER JOIN delta_BGP_113119029616741403_3 AS R2 ON R1.z = R2.z
AND R1.y1 = R2.y1
AND R1.x = R2.x
AND R1.y2 = R2.y2;