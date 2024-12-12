CREATE TEMP TABLE delta_BGP_4313253051102226119_0 AS
SELECT G1.s AS x,
       G1.o AS y,
       G1.k_count
FROM delta_G G1
WHERE G1.p = 'http://example.org/edges/link';


CREATE TABLE delta_BGP_4313253051102226119 AS
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
FROM AS R1
FULL OUTER JOIN delta_BGP_4313253051102226119_0 AS R2 ON R1.y = R2.y
AND R1.x = R2.x
WHERE coalesce(R1.k_count, 0) + coalesce(R2.k_count, 0) != 0;