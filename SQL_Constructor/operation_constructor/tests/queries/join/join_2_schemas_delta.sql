CREATE TEMP TABLE prep_delta_Join_8039763548589018781 AS
SELECT r1.w AS w,
       r2.x AS x,
       r1.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM delta_BGP_5127379026335911785 AS r1,
     Union_3180718904663486803_schema_5536938746033674259 AS r2 ON r1.y = r2.y;


INSERT INTO prep_delta_Join_8039763548589018781 (w, x, y, k_count)
SELECT r1.w AS w,
       r2.x AS x,
       r1.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM delta_BGP_5127379026335911785 AS r1,
     Union_3180718904663486803_schema_122147079200776137 AS r2 ON r1.w = r2.w;


INSERT INTO prep_delta_Join_8039763548589018781 (w, x, y, k_count)
SELECT r1.w AS w,
       r2.x AS x,
       r1.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM nu_BGP_5127379026335911785 AS r1,
     delta_Union_3180718904663486803_schema_5536938746033674259 AS r2 ON r1.y = r2.y;


INSERT INTO prep_delta_Join_8039763548589018781 (w, x, y, k_count)
SELECT r1.w AS w,
       r2.x AS x,
       r1.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM nu_BGP_5127379026335911785 AS r1,
     delta_Union_3180718904663486803_schema_122147079200776137 AS r2 ON r1.w = r2.w;


CREATE TABLE delta_Join_8039763548589018781 AS
SELECT r1.w,
       r1.x,
       r1.y,
       SUM(r1.k_count) AS k_count
FROM prep_delta_Join_8039763548589018781 AS r1
GROUP BY r1.w,
         r1.x,
         r1.y;