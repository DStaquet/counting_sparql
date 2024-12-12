CREATE TEMP TABLE delta_LeftJoin_7202945294355753096_schema_5536938746033674259_0 AS
SELECT r1.x AS x,
       r2.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM delta_BGP_747695058721694287 AS r1,
     Union_3180718904663486803_schema_5536938746033674259 AS r2
WHERE r1.x = r2.x;


CREATE TEMP TABLE delta_LeftJoin_7202945294355753096_schema_5536938746033674259_1 AS
SELECT r1.x AS x,
       r2.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM nu_BGP_747695058721694287 AS r1,
     delta_Union_3180718904663486803_schema_5536938746033674259 AS r2
WHERE r1.x = r2.x;


CREATE TABLE delta_LeftJoin_7202945294355753096_schema_5536938746033674259 AS
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
FROM delta_LeftJoin_7202945294355753096_schema_5536938746033674259_0 AS R1
FULL OUTER JOIN delta_LeftJoin_7202945294355753096_schema_5536938746033674259_1 AS R2 ON R1.y = R2.y
AND R1.x = R2.x
WHERE coalesce(R1.k_count, 0) + coalesce(R2.k_count, 0) != 0;


CREATE TEMP TABLE delta_LeftJoin_7202945294355753096_schema_122147079200776137_0 AS
SELECT r2.w AS w,
       r1.x AS x,
       r1.k_count * r2.k_count AS k_count
FROM delta_BGP_747695058721694287 AS r1,
     Union_3180718904663486803_schema_122147079200776137 AS r2
WHERE r1.x = r2.x;


CREATE TEMP TABLE delta_LeftJoin_7202945294355753096_schema_122147079200776137_1 AS
SELECT r2.w AS w,
       r1.x AS x,
       r1.k_count * r2.k_count AS k_count
FROM nu_BGP_747695058721694287 AS r1,
     delta_Union_3180718904663486803_schema_122147079200776137 AS r2
WHERE r1.x = r2.x;


CREATE TABLE delta_LeftJoin_7202945294355753096_schema_122147079200776137 AS
SELECT (CASE
            WHEN R1.w NOT NULL THEN R1.w
            ELSE R2.w
        END) AS w,
       (CASE
            WHEN R1.x NOT NULL THEN R1.x
            ELSE R2.x
        END) AS x,
       (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
        END) AS k_count
FROM delta_LeftJoin_7202945294355753096_schema_122147079200776137_0 AS R1
FULL OUTER JOIN delta_LeftJoin_7202945294355753096_schema_122147079200776137_1 AS R2 ON R1.w = R2.w
AND R1.x = R2.x
WHERE coalesce(R1.k_count, 0) + coalesce(R2.k_count, 0) != 0;


CREATE TEMP TABLE delta_LeftJoin_7202945294355753096_schema_5974201903695169563_0 AS
SELECT s1.x AS x,
       s1.k_count AS k_count
FROM delta_BGP_747695058721694287 AS s1
WHERE NOT EXISTS (
                  FROM Union_3180718904663486803_schema_5536938746033674259 AS s2
                  WHERE s1.x = s2.x)
  AND NOT EXISTS (
                  FROM Union_3180718904663486803_schema_122147079200776137 AS s3
                  WHERE s1.x = s3.x);


CREATE TEMP TABLE delta_LeftJoin_7202945294355753096_schema_5974201903695169563_1 AS
SELECT s1.x AS x,
       s1.k_count AS k_count
FROM nu_BGP_747695058721694287 AS s1
JOIN delta_Union_3180718904663486803 AS s2 ON s1.x = s2.x
WHERE EXISTS (
              FROM Union_3180718904663486803_schema_5536938746033674259 AS s3
              WHERE s1.x = s3.x
                AND -s2.k_count = s3.k_count)
  AND EXISTS (
              FROM Union_3180718904663486803_schema_122147079200776137 AS s4
              WHERE s1.x = s4.x
                AND -s2.k_count = s4.k_count)
UNION
SELECT s1.x AS x, -s1.k_count AS k_count
FROM nu_BGP_747695058721694287 AS s1
JOIN delta_Union_3180718904663486803 AS s2 ON s1.x = s2.x
WHERE NOT EXISTS (
                  FROM Union_3180718904663486803_schema_5536938746033674259 AS s3
                  WHERE s1.x = s3.x)
  AND NOT EXISTS (
                  FROM Union_3180718904663486803_schema_122147079200776137 AS s4
                  WHERE s1.x = s4.x);


CREATE TABLE delta_LeftJoin_7202945294355753096_schema_5974201903695169563 AS
SELECT (CASE
            WHEN R1.x NOT NULL THEN R1.x
            ELSE R2.x
        END) AS x,
       (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
        END) AS k_count
FROM delta_LeftJoin_7202945294355753096_schema_5974201903695169563_0 AS R1
FULL OUTER JOIN delta_LeftJoin_7202945294355753096_schema_5974201903695169563_1 AS R2 ON R1.x = R2.x
WHERE coalesce(R1.k_count, 0) + coalesce(R2.k_count, 0) != 0;