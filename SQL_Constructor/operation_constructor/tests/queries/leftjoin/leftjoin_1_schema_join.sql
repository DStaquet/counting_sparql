CREATE TEMP TABLE delta_LeftJoin_5016477813953594459_schema_4427885478980723971_0 AS
SELECT r1.x AS x,
       r2.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM delta_BGP_6412654939285419064 AS r1,
     BGP_8639977824181032562 AS r2
WHERE r1.x = r2.x;


CREATE TEMP TABLE delta_LeftJoin_5016477813953594459_schema_4427885478980723971_1 AS
SELECT r1.x AS x,
       r2.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM nu_BGP_6412654939285419064 AS r1,
     delta_BGP_8639977824181032562 AS r2
WHERE r1.x = r2.x;


CREATE TABLE delta_LeftJoin_5016477813953594459_schema_4427885478980723971 AS
SELECT (CASE
            WHEN R1.y NOT NULL THEN R1.y
            ELSE R2.y
        END) AS y,
       (CASE
            WHEN R1.x NOT NULL THEN R1.x
            ELSE R2.x
        END) AS x,
       (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
        END) AS k_count
FROM delta_LeftJoin_5016477813953594459_schema_4427885478980723971_0 AS R1
FULL OUTER JOIN delta_LeftJoin_5016477813953594459_schema_4427885478980723971_1 AS R2 ON R1.y = R2.y
AND R1.x = R2.x
WHERE coalesce(R1.k_count, 0) + coalesce(R2.k_count, 0) != 0;


CREATE TEMP TABLE delta_LeftJoin_5016477813953594459_schema_8057865995004935963_0 AS
SELECT s1.x AS x,
       s1.k_count AS k_count
FROM delta_BGP_6412654939285419064 AS s1
WHERE NOT EXISTS (
                  FROM BGP_8639977824181032562 AS s2
                  WHERE s1.x = s2.x);


CREATE TEMP TABLE delta_LeftJoin_5016477813953594459_schema_8057865995004935963_1 AS
SELECT s1.x AS x,
       s1.k_count AS k_count
FROM nu_BGP_6412654939285419064 AS s1
JOIN delta_BGP_8639977824181032562 AS s2 ON s1.x = s2.x
WHERE NOT EXISTS (
                  FROM nu_BGP_8639977824181032562 AS s3
                  WHERE s1.x = s3.x)
UNION
SELECT s1.x AS x, -s1.k_count AS k_count
FROM nu_BGP_6412654939285419064 AS s1
JOIN delta_BGP_8639977824181032562 AS s2 ON s1.x = s2.x
WHERE NOT EXISTS (
                  FROM BGP_8639977824181032562 AS s3
                  WHERE s1.x = s3.x);


CREATE TABLE delta_LeftJoin_5016477813953594459_schema_8057865995004935963 AS
SELECT (CASE
            WHEN R1.x NOT NULL THEN R1.x
            ELSE R2.x
        END) AS x,
       (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
        END) AS k_count
FROM delta_LeftJoin_5016477813953594459_schema_8057865995004935963_0 AS R1
FULL OUTER JOIN delta_LeftJoin_5016477813953594459_schema_8057865995004935963_1 AS R2 ON R1.x = R2.x
WHERE coalesce(R1.k_count, 0) + coalesce(R2.k_count, 0) != 0;