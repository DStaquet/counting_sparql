CREATE TABLE delta_BGP_4313253051102226119 AS
SELECT (CASE
            WHEN R0.y NOT NULL THEN R0.y
            ELSE R0_1.y
        END) AS y,
       (CASE
            WHEN R0.x NOT NULL THEN R0.x
            ELSE R0_1.x
        END) AS x,
       (CASE
            WHEN R0.k_count IS NULL THEN R0_1.k_count
            WHEN R0_1.k_count IS NULL THEN R0.k_count
            ELSE R0.k_count + R0_1.k_count
        END) AS k_count
FROM delta_BGP_4313253051102226119_1;