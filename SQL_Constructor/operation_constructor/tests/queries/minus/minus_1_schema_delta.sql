CREATE TEMP TABLE prep_delta_Minus_5016477813953594459 AS
SELECT s1.x AS x,
       s1.k_count AS k_count
FROM delta_BGP_6412654939285419064 AS s1
WHERE NOT EXISTS (
                  FROM BGP_8639977824181032562 AS s2
                  WHERE s1.x = s2.x);


INSERT INTO prep_delta_Minus_5016477813953594459 (x, k_count)
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


CREATE TABLE delta_Minus_5016477813953594459 AS
SELECT r1.x,
       SUM(r1.k_count) AS k_count
FROM prep_delta_Minus_5016477813953594459 AS r1
GROUP BY r1.x
HAVING SUM(r1.k_count) != 0;