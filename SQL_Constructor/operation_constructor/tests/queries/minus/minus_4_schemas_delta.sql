CREATE TEMP TABLE prep_delta_Minus_5001696111420667855_schema_5974201903695169563 AS
SELECT s1.x AS x,
       s1.k_count AS k_count
FROM delta_Union_1443468051870521748_schema_5974201903695169563 AS s1
WHERE NOT EXISTS (
                  FROM Union_6981146949604561737_schema_5536938746033674259 AS s2
                  WHERE s1.x = s2.x)
  AND NOT EXISTS (
                  FROM Union_6981146949604561737_schema_388442962187960249 AS s3
                  WHERE s1.x = s3.x);


INSERT INTO prep_delta_Minus_5001696111420667855_schema_5974201903695169563 (x, k_count)
SELECT s1.x AS x,
       s1.k_count AS k_count
FROM nu_Union_1443468051870521748 AS s1
JOIN delta_Union_6981146949604561737 AS s2 ON s1.x = s2.x
WHERE EXISTS (
              FROM Union_6981146949604561737_schema_5536938746033674259 AS s3
              WHERE s1.x = s3.x
                AND -s2.k_count = s3.k_count)
  AND EXISTS (
              FROM Union_6981146949604561737_schema_388442962187960249 AS s4
              WHERE s1.x = s4.x
                AND -s2.k_count = s4.k_count)
UNION
SELECT s1.x AS x, -s1.k_count AS k_count
FROM nu_Union_1443468051870521748 AS s1
JOIN delta_Union_6981146949604561737 AS s2 ON s1.x = s2.x
WHERE NOT EXISTS (
                  FROM Union_6981146949604561737_schema_5536938746033674259 AS s3
                  WHERE s1.x = s3.x)
  AND NOT EXISTS (
                  FROM Union_6981146949604561737_schema_388442962187960249 AS s4
                  WHERE s1.x = s4.x);


CREATE TABLE delta_Minus_5001696111420667855_schema_5974201903695169563 AS
SELECT r1.x,
       SUM(r1.k_count) AS k_count
FROM prep_delta_Minus_5001696111420667855_schema_5974201903695169563 AS r1
GROUP BY r1.x;


CREATE TEMP TABLE prep_delta_Minus_5001696111420667855_schema_6925710393041315400 AS
SELECT s1.y AS y,
       s1.k_count AS k_count
FROM delta_Union_1443468051870521748_schema_6925710393041315400 AS s1
WHERE NOT EXISTS (
                  FROM Union_6981146949604561737_schema_5536938746033674259 AS s2
                  WHERE s1.y = s2.y);


INSERT INTO prep_delta_Minus_5001696111420667855_schema_6925710393041315400 (y, k_count)
SELECT s1.y AS y,
       s1.k_count AS k_count
FROM nu_Union_1443468051870521748 AS s1
JOIN delta_Union_6981146949604561737 AS s2 ON s1.y = s2.y
WHERE EXISTS (
              FROM Union_6981146949604561737_schema_5536938746033674259 AS s3
              WHERE s1.y = s3.y
                AND -s2.k_count = s3.k_count)
UNION
SELECT s1.y AS y, -s1.k_count AS k_count
FROM nu_Union_1443468051870521748 AS s1
JOIN delta_Union_6981146949604561737 AS s2 ON s1.y = s2.y
WHERE NOT EXISTS (
                  FROM Union_6981146949604561737_schema_5536938746033674259 AS s3
                  WHERE s1.y = s3.y);


CREATE TABLE delta_Minus_5001696111420667855_schema_6925710393041315400 AS
SELECT r1.y,
       SUM(r1.k_count) AS k_count
FROM prep_delta_Minus_5001696111420667855_schema_6925710393041315400 AS r1
GROUP BY r1.y;