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
FROM
  (SELECT G1.s AS x,
          G2.s AS y,
          G2.o AS z,
          G1.k_count
   FROM delta_G G1,
        G G2
   WHERE G1.p = 'http://example.org/edges/link'
     AND G1.o = G2.s
     AND G2.p = 'http://example.org/edges/link') AS R0
FULL OUTER JOIN (
                   (SELECT G1.s AS x,
                           G2.s AS y,
                           G2.o AS z,
                           G2.k_count
                    FROM nu_G G1,
                         delta_G G2
                    WHERE G1.p = 'http://example.org/edges/link'
                      AND G1.o = G2.s
                      AND G2.p = 'http://example.org/edges/link') AS R1
                 FULL OUTER JOIN
                   (SELECT G1.s AS x,
                           G2.s AS y,
                           G2.o AS z,
                           G3.k_count
                    FROM nu_G G1,
                         nu_G G2
                    WHERE G1.p = 'http://example.org/edges/link'
                      AND G1.o = G2.s
                      AND G2.p = 'http://example.org/edges/link') AS R1_2 ON R1_2.x = R1.x
                 AND R1_2.y = R1.y
                 AND R1_2.z = R1.z) AS R0_1 ON R0_1.x = R0.x
AND R0_1.y = R0.y
AND R0_1.z = R0.z;