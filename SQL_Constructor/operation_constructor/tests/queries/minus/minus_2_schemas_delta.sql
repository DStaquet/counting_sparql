CREATE TABLE delta_prep_Minus_5787900088682136291 AS
SELECT s1.x AS x,
       s1.k_count AS k_count
FROM delta_BGP_747695058721694287 AS s1
WHERE NOT EXISTS (
                  FROM Union_6981146949604561737_schema_5536938746033674259 AS s2
                  WHERE s1.x = s2.x)
  AND NOT EXISTS (
                  FROM Union_6981146949604561737_schema_388442962187960249 AS s3
                  WHERE s1.x = s3.x);


INSERT INTO delta_prep_Minus_5787900088682136291
SELECT *
FROM nu_BGP_747695058721694287 AS s1
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
FROM nu_BGP_747695058721694287 AS s1
JOIN delta_Union_6981146949604561737 AS s2 ON s1.x = s2.x
WHERE NOT EXISTS (
                  FROM Union_6981146949604561737_schema_5536938746033674259 AS s3
                  WHERE s1.x = s3.x)
  AND NOT EXISTS (
                  FROM Union_6981146949604561737_schema_388442962187960249 AS s4
                  WHERE s1.x = s4.x);


CREATE TABLE delta_Minus_5787900088682136291 AS
SELECT r1.x,
       SUM(r1.k_count) AS k_count
FROM delta_prep_Minus_5787900088682136291 AS r1
GROUP BY r1.x;