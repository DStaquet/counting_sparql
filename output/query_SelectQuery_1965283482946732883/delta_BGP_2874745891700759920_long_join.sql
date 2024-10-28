CREATE TABLE delta_BGP_2874745891700759920 AS
SELECT (CASE
            WHEN R0.t1 NOT NULL THEN R0.t1
            ELSE R0_1.t1
        END) AS t1,
       (CASE
            WHEN R0.t3 NOT NULL THEN R0.t3
            ELSE R0_1.t3
        END) AS t3,
       (CASE
            WHEN R0.x NOT NULL THEN R0.x
            ELSE R0_1.x
        END) AS x,
       (CASE
            WHEN R0.t4 NOT NULL THEN R0.t4
            ELSE R0_1.t4
        END) AS t4,
       (CASE
            WHEN R0.t2 NOT NULL THEN R0.t2
            ELSE R0_1.t2
        END) AS t2,
       (CASE
            WHEN R0.t5 NOT NULL THEN R0.t5
            ELSE R0_1.t5
        END) AS t5,
       (CASE
            WHEN R0.y NOT NULL THEN R0.y
            ELSE R0_1.y
        END) AS y,
       (CASE
            WHEN R0.k_count IS NULL THEN R0_1.k_count
            WHEN R0_1.k_count IS NULL THEN R0.k_count
            ELSE R0.k_count + R0_1.k_count
        END) AS k_count
FROM
  (SELECT G1.s AS t1,
          G2.s AS t2,
          G3.s AS t3,
          G4.s AS t4,
          G5.s AS t5,
          G6.s AS x,
          G5.o AS y,
          G1.k_count
   FROM delta_G G1,
        G G2,
        G G3,
        G G4,
        G G5,
        G G6
   WHERE G1.p = 'http://example.org/edges/link'
     AND G1.o = G2.s
     AND G2.p = 'http://example.org/edges/link'
     AND G2.o = G3.s
     AND G3.p = 'http://example.org/edges/link'
     AND G3.o = G4.s
     AND G4.p = 'http://example.org/edges/link'
     AND G4.o = G5.s
     AND G5.p = 'http://example.org/edges/link'
     AND G6.p = 'http://example.org/edges/link'
     AND G1.s = G6.o) AS R0
FULL OUTER JOIN (
                   (SELECT G1.s AS t1,
                           G2.s AS t2,
                           G3.s AS t3,
                           G4.s AS t4,
                           G5.s AS t5,
                           G6.s AS x,
                           G5.o AS y,
                           G2.k_count
                    FROM nu_G G1,
                         delta_G G2,
                         G G3,
                         G G4,
                         G G5,
                         G G6
                    WHERE G1.p = 'http://example.org/edges/link'
                      AND G1.o = G2.s
                      AND G2.p = 'http://example.org/edges/link'
                      AND G2.o = G3.s
                      AND G3.p = 'http://example.org/edges/link'
                      AND G3.o = G4.s
                      AND G4.p = 'http://example.org/edges/link'
                      AND G4.o = G5.s
                      AND G5.p = 'http://example.org/edges/link'
                      AND G6.p = 'http://example.org/edges/link'
                      AND G1.s = G6.o) AS R1
                 FULL OUTER JOIN (
                                    (SELECT G1.s AS t1,
                                            G2.s AS t2,
                                            G3.s AS t3,
                                            G4.s AS t4,
                                            G5.s AS t5,
                                            G6.s AS x,
                                            G5.o AS y,
                                            G3.k_count
                                     FROM nu_G G1,
                                          nu_G G2,
                                          delta_G G3,
                                          G G4,
                                          G G5,
                                          G G6
                                     WHERE G1.p = 'http://example.org/edges/link'
                                       AND G1.o = G2.s
                                       AND G2.p = 'http://example.org/edges/link'
                                       AND G2.o = G3.s
                                       AND G3.p = 'http://example.org/edges/link'
                                       AND G3.o = G4.s
                                       AND G4.p = 'http://example.org/edges/link'
                                       AND G4.o = G5.s
                                       AND G5.p = 'http://example.org/edges/link'
                                       AND G6.p = 'http://example.org/edges/link'
                                       AND G1.s = G6.o) AS R2
                                  FULL OUTER JOIN (
                                                     (SELECT G1.s AS t1,
                                                             G2.s AS t2,
                                                             G3.s AS t3,
                                                             G4.s AS t4,
                                                             G5.s AS t5,
                                                             G6.s AS x,
                                                             G5.o AS y,
                                                             G4.k_count
                                                      FROM nu_G G1,
                                                           nu_G G2,
                                                           nu_G G3,
                                                           delta_G G4,
                                                           G G5,
                                                           G G6
                                                      WHERE G1.p = 'http://example.org/edges/link'
                                                        AND G1.o = G2.s
                                                        AND G2.p = 'http://example.org/edges/link'
                                                        AND G2.o = G3.s
                                                        AND G3.p = 'http://example.org/edges/link'
                                                        AND G3.o = G4.s
                                                        AND G4.p = 'http://example.org/edges/link'
                                                        AND G4.o = G5.s
                                                        AND G5.p = 'http://example.org/edges/link'
                                                        AND G6.p = 'http://example.org/edges/link'
                                                        AND G1.s = G6.o) AS R3
                                                   FULL OUTER JOIN (
                                                                      (SELECT G1.s AS t1,
                                                                              G2.s AS t2,
                                                                              G3.s AS t3,
                                                                              G4.s AS t4,
                                                                              G5.s AS t5,
                                                                              G6.s AS x,
                                                                              G5.o AS y,
                                                                              G5.k_count
                                                                       FROM nu_G G1,
                                                                            nu_G G2,
                                                                            nu_G G3,
                                                                            nu_G G4,
                                                                            delta_G G5,
                                                                            G G6
                                                                       WHERE G1.p = 'http://example.org/edges/link'
                                                                         AND G1.o = G2.s
                                                                         AND G2.p = 'http://example.org/edges/link'
                                                                         AND G2.o = G3.s
                                                                         AND G3.p = 'http://example.org/edges/link'
                                                                         AND G3.o = G4.s
                                                                         AND G4.p = 'http://example.org/edges/link'
                                                                         AND G4.o = G5.s
                                                                         AND G5.p = 'http://example.org/edges/link'
                                                                         AND G6.p = 'http://example.org/edges/link'
                                                                         AND G1.s = G6.o) AS R4
                                                                    FULL OUTER JOIN (
                                                                                       (SELECT G1.s AS t1,
                                                                                               G2.s AS t2,
                                                                                               G3.s AS t3,
                                                                                               G4.s AS t4,
                                                                                               G5.s AS t5,
                                                                                               G6.s AS x,
                                                                                               G5.o AS y,
                                                                                               G6.k_count
                                                                                        FROM nu_G G1,
                                                                                             nu_G G2,
                                                                                             nu_G G3,
                                                                                             nu_G G4,
                                                                                             nu_G G5,
                                                                                             delta_G G6
                                                                                        WHERE G1.p = 'http://example.org/edges/link'
                                                                                          AND G1.o = G2.s
                                                                                          AND G2.p = 'http://example.org/edges/link'
                                                                                          AND G2.o = G3.s
                                                                                          AND G3.p = 'http://example.org/edges/link'
                                                                                          AND G3.o = G4.s
                                                                                          AND G4.p = 'http://example.org/edges/link'
                                                                                          AND G4.o = G5.s
                                                                                          AND G5.p = 'http://example.org/edges/link'
                                                                                          AND G6.p = 'http://example.org/edges/link'
                                                                                          AND G1.s = G6.o) AS R5
                                                                                     FULL OUTER JOIN
                                                                                       (SELECT G1.s AS t1,
                                                                                               G2.s AS t2,
                                                                                               G3.s AS t3,
                                                                                               G4.s AS t4,
                                                                                               G5.s AS t5,
                                                                                               G6.s AS x,
                                                                                               G5.o AS y,
                                                                                               G7.k_count
                                                                                        FROM nu_G G1,
                                                                                             nu_G G2,
                                                                                             nu_G G3,
                                                                                             nu_G G4,
                                                                                             nu_G G5,
                                                                                             nu_G G6
                                                                                        WHERE G1.p = 'http://example.org/edges/link'
                                                                                          AND G1.o = G2.s
                                                                                          AND G2.p = 'http://example.org/edges/link'
                                                                                          AND G2.o = G3.s
                                                                                          AND G3.p = 'http://example.org/edges/link'
                                                                                          AND G3.o = G4.s
                                                                                          AND G4.p = 'http://example.org/edges/link'
                                                                                          AND G4.o = G5.s
                                                                                          AND G5.p = 'http://example.org/edges/link'
                                                                                          AND G6.p = 'http://example.org/edges/link'
                                                                                          AND G1.s = G6.o) AS R5_6 ON R5_6.t1 = R5.t1
                                                                                     AND R5_6.t2 = R5.t2
                                                                                     AND R5_6.t3 = R5.t3
                                                                                     AND R5_6.t4 = R5.t4
                                                                                     AND R5_6.t5 = R5.t5
                                                                                     AND R5_6.x = R5.x
                                                                                     AND R5_6.y = R5.y) AS R4_5 ON R4_5.t1 = R4.t1
                                                                    AND R4_5.t2 = R4.t2
                                                                    AND R4_5.t3 = R4.t3
                                                                    AND R4_5.t4 = R4.t4
                                                                    AND R4_5.t5 = R4.t5
                                                                    AND R4_5.x = R4.x
                                                                    AND R4_5.y = R4.y) AS R3_4 ON R3_4.t1 = R3.t1
                                                   AND R3_4.t2 = R3.t2
                                                   AND R3_4.t3 = R3.t3
                                                   AND R3_4.t4 = R3.t4
                                                   AND R3_4.t5 = R3.t5
                                                   AND R3_4.x = R3.x
                                                   AND R3_4.y = R3.y) AS R2_3 ON R2_3.t1 = R2.t1
                                  AND R2_3.t2 = R2.t2
                                  AND R2_3.t3 = R2.t3
                                  AND R2_3.t4 = R2.t4
                                  AND R2_3.t5 = R2.t5
                                  AND R2_3.x = R2.x
                                  AND R2_3.y = R2.y) AS R1_2 ON R1_2.t1 = R1.t1
                 AND R1_2.t2 = R1.t2
                 AND R1_2.t3 = R1.t3
                 AND R1_2.t4 = R1.t4
                 AND R1_2.t5 = R1.t5
                 AND R1_2.x = R1.x
                 AND R1_2.y = R1.y) AS R0_1 ON R0_1.t1 = R0.t1
AND R0_1.t2 = R0.t2
AND R0_1.t3 = R0.t3
AND R0_1.t4 = R0.t4
AND R0_1.t5 = R0.t5
AND R0_1.x = R0.x
AND R0_1.y = R0.y;