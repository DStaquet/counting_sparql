CREATE TABLE Join_1233181518159936422 AS
SELECT r1.w AS w,
       r2.x AS x,
       r1.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM BGP_5127379026335911785 AS r1,
     BGP_4313253051102226119 AS r2 ON r1.y = r2.y;