CREATE TEMP TABLE prep_delta_Join_4718063118473701382_schema_5110681566428164075 AS
SELECT r1.w AS w,
       r2.x AS x,
       r1.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM delta_BGP_4828852104882819343 AS r1,
     Union_9052630879156566306_schema_4427885478980723971 AS r2
WHERE r1.y = r2.y;


INSERT INTO prep_delta_Join_4718063118473701382_schema_5110681566428164075 (w, x, y, k_count)
SELECT r1.w AS w,
       r2.x AS x,
       r1.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM nu_BGP_4828852104882819343 AS r1,
     delta_Union_9052630879156566306_schema_4427885478980723971 AS r2
WHERE r1.y = r2.y;


CREATE TABLE delta_Join_4718063118473701382_schema_5110681566428164075 AS
SELECT r1.w,
       r1.x,
       r1.y,
       SUM(r1.k_count) AS k_count
FROM prep_delta_Join_4718063118473701382_schema_5110681566428164075 AS r1
GROUP BY r1.w,
         r1.x,
         r1.y
HAVING SUM(r1.k_count) != 0;


CREATE TEMP TABLE prep_delta_Join_4718063118473701382_schema_1737849758471438459 AS
SELECT r1.w AS w,
       r1.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM delta_BGP_4828852104882819343 AS r1,
     Union_9052630879156566306_schema_1737849758471438459 AS r2
WHERE r1.w = r2.w
  AND r1.y = r2.y;


INSERT INTO prep_delta_Join_4718063118473701382_schema_1737849758471438459 (w, y, k_count)
SELECT r1.w AS w,
       r1.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM nu_BGP_4828852104882819343 AS r1,
     delta_Union_9052630879156566306_schema_1737849758471438459 AS r2
WHERE r1.w = r2.w
  AND r1.y = r2.y;


CREATE TABLE delta_Join_4718063118473701382_schema_1737849758471438459 AS
SELECT r1.w,
       r1.y,
       SUM(r1.k_count) AS k_count
FROM prep_delta_Join_4718063118473701382_schema_1737849758471438459 AS r1
GROUP BY r1.w,
         r1.y
HAVING SUM(r1.k_count) != 0;