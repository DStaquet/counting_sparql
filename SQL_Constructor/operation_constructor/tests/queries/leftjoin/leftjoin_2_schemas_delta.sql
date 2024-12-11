CREATE TEMP TABLE prep_delta_LeftJoin_7202945294355753096_schema_5536938746033674259 AS
SELECT r1.x AS x,
       r2.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM delta_BGP_747695058721694287 AS r1,
     Union_3180718904663486803_schema_5536938746033674259 AS r2 ON r1.x = r2.x;


INSERT INTO prep_delta_LeftJoin_7202945294355753096_schema_5536938746033674259 (x, y, k_count)
SELECT r1.x AS x,
       r2.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM nu_BGP_747695058721694287 AS r1,
     delta_Union_3180718904663486803_schema_5536938746033674259 AS r2 ON r1.x = r2.x;


CREATE TABLE delta_LeftJoin_7202945294355753096_schema_5536938746033674259 AS
SELECT r1.x,
       r1.y,
       SUM(r1.k_count) AS k_count
FROM prep_delta_LeftJoin_7202945294355753096_schema_5536938746033674259 AS r1
GROUP BY r1.x,
         r1.y;


CREATE TEMP TABLE prep_delta_LeftJoin_7202945294355753096_schema_122147079200776137 AS
SELECT r2.w AS w,
       r1.x AS x,
       r1.k_count * r2.k_count AS k_count
FROM delta_BGP_747695058721694287 AS r1,
     Union_3180718904663486803_schema_122147079200776137 AS r2 ON r1.x = r2.x;


INSERT INTO prep_delta_LeftJoin_7202945294355753096_schema_122147079200776137 (w, x, k_count)
SELECT r2.w AS w,
       r1.x AS x,
       r1.k_count * r2.k_count AS k_count
FROM nu_BGP_747695058721694287 AS r1,
     delta_Union_3180718904663486803_schema_122147079200776137 AS r2 ON r1.x = r2.x;


CREATE TABLE delta_LeftJoin_7202945294355753096_schema_122147079200776137 AS
SELECT r1.w,
       r1.x,
       SUM(r1.k_count) AS k_count
FROM prep_delta_LeftJoin_7202945294355753096_schema_122147079200776137 AS r1
GROUP BY r1.w,
         r1.x;


CREATE TEMP TABLE prep_delta_LeftJoin_7202945294355753096_schema_5974201903695169563 AS
SELECT s1.x AS x,
       s1.k_count AS k_count
FROM delta_BGP_747695058721694287 AS s1
WHERE NOT EXISTS (
                  FROM Union_3180718904663486803_schema_5536938746033674259 AS s2
                  WHERE s1.x = s2.x)
  AND NOT EXISTS (
                  FROM Union_3180718904663486803_schema_122147079200776137 AS s3
                  WHERE s1.x = s3.x);


INSERT INTO prep_delta_LeftJoin_7202945294355753096_schema_5974201903695169563 (x, k_count)
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
SELECT r1.x,
       SUM(r1.k_count) AS k_count
FROM prep_delta_LeftJoin_7202945294355753096_schema_5974201903695169563 AS r1
GROUP BY r1.x;