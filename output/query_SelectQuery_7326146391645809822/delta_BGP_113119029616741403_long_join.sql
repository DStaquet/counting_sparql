CREATE TABLE delta_BGP_113119029616741403 AS
SELECT (CASE
            WHEN R0.z NOT NULL THEN R0.z
            ELSE R0_1.z
        END) AS z,
       (CASE
            WHEN R0.y1 NOT NULL THEN R0.y1
            ELSE R0_1.y1
        END) AS y1,
       (CASE
            WHEN R0.x NOT NULL THEN R0.x
            ELSE R0_1.x
        END) AS x,
       (CASE
            WHEN R0.y2 NOT NULL THEN R0.y2
            ELSE R0_1.y2
        END) AS y2,
       (CASE
            WHEN R0.k_count IS NULL THEN R0_1.k_count
            WHEN R0_1.k_count IS NULL THEN R0.k_count
            ELSE R0.k_count + R0_1.k_count
        END) AS k_count
FROM (delta_BGP_113119029616741403_1 AS R0
      FULL OUTER JOIN (delta_BGP_113119029616741403_2 AS R1
                       FULL OUTER JOIN delta_BGP_113119029616741403_3 AS R1_2 ON R1_2.x = R1.x
                       AND R1_2.y1 = R1.y1
                       AND R1_2.y2 = R1.y2
                       AND R1_2.z = R1.z) AS R0_1 ON R0_1.x = R0.x
      AND R0_1.y1 = R0.y1
      AND R0_1.y2 = R0.y2
      AND R0_1.z = R0.z);