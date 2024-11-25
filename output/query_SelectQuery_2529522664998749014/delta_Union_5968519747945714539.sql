CREATE TABLE delta_Union_5968519747945714539_schema_5536938746033674259 AS
SELECT (CASE
            WHEN r1.x IS NOT NULL THEN r1.x
            ELSE r2.x
        END) AS x,
       (CASE
            WHEN r1.y IS NOT NULL THEN r1.y
            ELSE r2.y
        END) AS y,
       coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) AS k_count
FROM delta_BGP_4313253051102226119 AS r1
FULL OUTER JOIN delta_BGP_5439676414810165533 AS r2 ON r1.y = r2.y;


CREATE TABLE delta_Union_5968519747945714539_schema_7808164217916843974 AS
SELECT (CASE
            WHEN r1.y IS NOT NULL THEN r1.y
            ELSE r2.y
        END) AS y,
       (CASE
            WHEN r1.z IS NOT NULL THEN r1.z
            ELSE r2.z
        END) AS z,
       coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) AS k_count
FROM delta_BGP_4313253051102226119 AS r1
FULL OUTER JOIN delta_BGP_5439676414810165533 AS r2 ON r1.y = r2.y;