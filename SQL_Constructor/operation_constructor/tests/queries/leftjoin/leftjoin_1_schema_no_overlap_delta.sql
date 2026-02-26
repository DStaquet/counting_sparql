CREATE TEMP TABLE prep_delta_LeftJoin_272100257129553905 AS
SELECT r1.x AS x,
       r2.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM delta_BGP_2378230508219361412 AS r1,
     BGP_5735499650974426227 AS r2 ;


INSERT INTO prep_delta_LeftJoin_272100257129553905 (x, y, k_count)
SELECT r1.x AS x,
       r2.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM nu_BGP_2378230508219361412 AS r1,
     delta_BGP_5735499650974426227 AS r2 ;


CREATE TABLE delta_LeftJoin_272100257129553905 AS
SELECT r1.x,
       r1.y,
       SUM(r1.k_count) AS k_count
FROM prep_delta_LeftJoin_272100257129553905 AS r1
GROUP BY r1.x,
         r1.y
HAVING SUM(r1.k_count) != 0;