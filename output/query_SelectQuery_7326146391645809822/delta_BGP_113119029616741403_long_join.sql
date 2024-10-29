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
FROM
  (SELECT G2.s AS x,
          G1.s AS y1,
          G3.s AS y2,
          G3.o AS z,
          G1.k_count
   FROM delta_G G1,
        G G2,
        G G3
   WHERE G1.p = 'http://example.org/edges/link'
     AND G2.p = 'http://example.org/edges/link'
     AND G1.s = G2.o
     AND G1.o = G3.s
     AND G3.p = 'http://example.org/edges/link') AS R0
FULL OUTER JOIN (
                   (SELECT G2.s AS x,
                           G1.s AS y1,
                           G3.s AS y2,
                           G3.o AS z,
                           G2.k_count
                    FROM nu_G G1,
                         delta_G G2,
                         G G3
                    WHERE G1.p = 'http://example.org/edges/link'
                      AND G2.p = 'http://example.org/edges/link'
                      AND G1.s = G2.o
                      AND G1.o = G3.s
                      AND G3.p = 'http://example.org/edges/link') AS R1
                 FULL OUTER JOIN
                   (SELECT G2.s AS x,
                           G1.s AS y1,
                           G3.s AS y2,
                           G3.o AS z,
                           G3.k_count
                    FROM nu_G G1,
                         nu_G G2,
                         delta_G G3
                    WHERE G1.p = 'http://example.org/edges/link'
                      AND G2.p = 'http://example.org/edges/link'
                      AND G1.s = G2.o
                      AND G1.o = G3.s
                      AND G3.p = 'http://example.org/edges/link') AS R1_2 ON R1_2.x = R1.x
                 AND R1_2.y1 = R1.y1
                 AND R1_2.y2 = R1.y2
                 AND R1_2.z = R1.z) AS R0_1 ON R0_1.x = R0.x
AND R0_1.y1 = R0.y1
AND R0_1.y2 = R0.y2
AND R0_1.z = R0.z;