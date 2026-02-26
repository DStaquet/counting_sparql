CREATE TEMP TABLE prep_Join_2077603546748115218 AS
SELECT r1.w AS w,
       r2.x AS x,
       r1.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM BGP_4828852104882819343 AS r1,
     Union_3828675832794025323_schema_4427885478980723971 AS r2
WHERE r1.y = r2.y;


INSERT INTO prep_Join_2077603546748115218 (w, x, y, k_count)
SELECT r1.w AS w,
       r2.x AS x,
       r1.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM BGP_4828852104882819343 AS r1,
     Union_3828675832794025323_schema_2119801163867732365 AS r2
WHERE r1.w = r2.w;


CREATE TABLE Join_2077603546748115218 AS
SELECT r1.w,
       r1.x,
       r1.y,
       SUM(r1.k_count) AS k_count
FROM prep_Join_2077603546748115218 AS r1
GROUP BY r1.w,
         r1.x,
         r1.y
HAVING SUM(r1.k_count) > 0;