CREATE TABLE delta_BGP_2691716057464995186 AS
SELECT (CASE
            WHEN R0.y NOT NULL THEN R0.y
            ELSE R0_1.y
        END) AS y,
       (CASE
            WHEN R0.z NOT NULL THEN R0.z
            ELSE R0_1.z
        END) AS z,
       (CASE
            WHEN R0.x NOT NULL THEN R0.x
            ELSE R0_1.x
        END) AS x,
       (CASE
            WHEN R0.k_count IS NULL THEN R0_1.k_count
            WHEN R0_1.k_count IS NULL THEN R0.k_count
            ELSE R0.k_count + R0_1.k_count
        END) AS k_count
FROM (delta_BGP_2691716057464995186_1 AS R0
      FULL OUTER JOIN delta_BGP_2691716057464995186_2 AS R0_1 ON R0_1.x = R0.x
      AND R0_1.y = R0.y
      AND R0_1.z = R0.z);