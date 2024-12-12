CREATE TEMP TABLE delta_Join_1233181518159936422_0 AS
SELECT r1.w AS w,
       r1.y AS y,
       r2.x AS x,
       r1.k_count * r2.k_count AS k_count
FROM delta_BGP_5127379026335911785 AS r1,
     BGP_4313253051102226119 AS r2 
WHERE r1.y = r2.y;


CREATE TEMP TABLE delta_Join_1233181518159936422_1 AS
SELECT r1.w AS w,
       r1.y AS y,
       r2.x AS x,
       r1.k_count * r2.k_count AS k_count
FROM nu_BGP_5127379026335911785 AS r1,
     delta_BGP_4313253051102226119 AS r2 
WHERE r1.y = r2.y;


CREATE TABLE delta_Join_1233181518159936422 AS
SELECT (CASE
            WHEN R1.y NOT NULL THEN R1.y
            ELSE R2.y
        END) AS y,
       (CASE
            WHEN R1.x NOT NULL THEN R1.x
            ELSE R2.x
        END) AS x,
       (CASE
            WHEN R1.w NOT NULL THEN R1.w
            ELSE R2.w
        END) AS w,
       (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
        END) AS k_count
FROM delta_Join_1233181518159936422_0 AS R1
FULL OUTER JOIN delta_Join_1233181518159936422_1 AS R2 ON R1.y = R2.y
AND R1.x = R2.x
AND R1.w = R2.w;