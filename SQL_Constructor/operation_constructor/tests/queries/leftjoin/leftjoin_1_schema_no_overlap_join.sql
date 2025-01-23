CREATE TEMP TABLE delta_LeftJoin_1471124881643212234_0 AS
SELECT r1.x AS x,
       r2.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM delta_BGP_5969360655464534899 AS r1,
     BGP_740711529997989213 AS r2 ;


CREATE TEMP TABLE delta_LeftJoin_1471124881643212234_1 AS
SELECT r1.x AS x,
       r2.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM nu_BGP_5969360655464534899 AS r1,
     delta_BGP_740711529997989213 AS r2 ;


CREATE TABLE delta_LeftJoin_1471124881643212234 AS
SELECT (CASE
            WHEN R1.y NOT NULL THEN R1.y
            ELSE R2.y
        END) AS y,
       (CASE
            WHEN R1.x NOT NULL THEN R1.x
            ELSE R2.x
        END) AS x,
       (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
        END) AS k_count
FROM delta_LeftJoin_1471124881643212234_0 AS R1
FULL OUTER JOIN delta_LeftJoin_1471124881643212234_1 AS R2 ON R1.y = R2.y
AND R1.x = R2.x
WHERE coalesce(R1.k_count, 0) + coalesce(R2.k_count, 0) != 0;