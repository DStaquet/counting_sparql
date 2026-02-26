CREATE TEMP TABLE prep_delta_Join_8668205654064478100 AS
SELECT r1.w AS w,
       r2.x AS x,
       r1.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM delta_BGP_4828852104882819343 AS r1,
     BGP_8639977824181032562 AS r2
WHERE r1.y = r2.y;


INSERT INTO prep_delta_Join_8668205654064478100 (w, x, y, k_count)
SELECT r1.w AS w,
       r2.x AS x,
       r1.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM nu_BGP_4828852104882819343 AS r1,
     delta_BGP_8639977824181032562 AS r2
WHERE r1.y = r2.y;


CREATE TABLE delta_Join_8668205654064478100 AS
SELECT r1.w,
       r1.x,
       r1.y,
       SUM(r1.k_count) AS k_count
FROM prep_delta_Join_8668205654064478100 AS r1
GROUP BY r1.w,
         r1.x,
         r1.y
HAVING SUM(r1.k_count) != 0;