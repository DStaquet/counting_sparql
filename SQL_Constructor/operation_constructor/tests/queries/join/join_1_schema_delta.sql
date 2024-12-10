CREATE TEMP TABLE prep_delta_Join_1233181518159936422 AS
SELECT r1.w AS w,
       r1.y AS y,
       r2.x AS x,
       r1.k_count * r2.k_count AS k_count
FROM delta_BGP_5127379026335911785 AS r1,
     BGP_4313253051102226119 AS r2 ON r1.y = r2.y;


INSERT INTO prep_delta_Join_1233181518159936422
SELECT r1.w AS w,
       r1.y AS y,
       r2.x AS x,
       r1.k_count * r2.k_count AS k_count
FROM nu_BGP_5127379026335911785 AS r1,
     delta_BGP_4313253051102226119 AS r2 ON r1.y = r2.y;


CREATE TABLE delta_Join_1233181518159936422 AS
SELECT r1.w,
       r1.x,
       r1.y,
       SUM(r1.k_count) AS k_count
FROM prep_delta_Join_1233181518159936422 AS r1
GROUP BY r1.w,
         r1.x,
         r1.y;