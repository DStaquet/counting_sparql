CREATE TEMP TABLE prep_delta_Join_6729856109576745271_schema_57734893926349734 AS
SELECT r1.w AS w,
       r2.x AS x,
       r1.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM delta_BGP_5127379026335911785 AS r1,
     Union_1860242193064701327_schema_5536938746033674259 AS r2
WHERE r1.y = r2.y;


INSERT INTO prep_delta_Join_6729856109576745271_schema_57734893926349734 (w, x, y, k_count)
SELECT r1.w AS w,
       r2.x AS x,
       r1.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM nu_BGP_5127379026335911785 AS r1,
     delta_Union_1860242193064701327_schema_5536938746033674259 AS r2
WHERE r1.y = r2.y;


CREATE TABLE delta_Join_6729856109576745271_schema_57734893926349734 AS
SELECT r1.w,
       r1.x,
       r1.y,
       SUM(r1.k_count) AS k_count
FROM prep_delta_Join_6729856109576745271_schema_57734893926349734 AS r1
GROUP BY r1.w,
         r1.x,
         r1.y
HAVING SUM(r1.k_count) != 0;


CREATE TEMP TABLE prep_delta_Join_6729856109576745271_schema_3615708767843743351 AS
SELECT r1.w AS w,
       r1.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM delta_BGP_5127379026335911785 AS r1,
     Union_1860242193064701327_schema_3615708767843743351 AS r2
WHERE r1.w = r2.w
  AND r1.y = r2.y;


INSERT INTO prep_delta_Join_6729856109576745271_schema_3615708767843743351 (w, y, k_count)
SELECT r1.w AS w,
       r1.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM nu_BGP_5127379026335911785 AS r1,
     delta_Union_1860242193064701327_schema_3615708767843743351 AS r2
WHERE r1.w = r2.w
  AND r1.y = r2.y;


CREATE TABLE delta_Join_6729856109576745271_schema_3615708767843743351 AS
SELECT r1.w,
       r1.y,
       SUM(r1.k_count) AS k_count
FROM prep_delta_Join_6729856109576745271_schema_3615708767843743351 AS r1
GROUP BY r1.w,
         r1.y
HAVING SUM(r1.k_count) != 0;