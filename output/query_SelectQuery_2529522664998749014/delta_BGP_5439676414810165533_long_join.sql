CREATE TABLE delta_BGP_5439676414810165533 AS
SELECT (CASE
            WHEN R0.y NOT NULL THEN R0.y
            ELSE R0_1.y
        END) AS y,
       (CASE
            WHEN R0.z NOT NULL THEN R0.z
            ELSE R0_1.z
        END) AS z,
       (CASE
            WHEN R0.k_count IS NULL THEN R0_1.k_count
            WHEN R0_1.k_count IS NULL THEN R0.k_count
            ELSE R0.k_count + R0_1.k_count
        END) AS k_count
FROM delta_BGP_5439676414810165533_1;