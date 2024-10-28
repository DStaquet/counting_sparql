CREATE TABLE delta_BGP_2691716057464995186 AS
SELECT (CASE
            WHEN R1.y NOT NULL THEN R1.y
            ELSE R2.y
        END) AS y,
       (CASE
            WHEN R1.z NOT NULL THEN R1.z
            ELSE R2.z
        END) AS z,
       (CASE
            WHEN R1.x NOT NULL THEN R1.x
            ELSE R2.x
        END) AS x,
       (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
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
     AND G2.p = 'http://example.org/edges/link') AS R1
FULL OUTER JOIN
  (SELECT G1.s AS x,
          G2.s AS y,
          G2.o AS z,
          G2.k_count
   FROM nu_G G1,
        delta_G G2
   WHERE G1.p = 'http://example.org/edges/link'
     AND G1.o = G2.s
     AND G2.p = 'http://example.org/edges/link') AS R2 ON R1.y = R2.y
AND R1.z = R2.z
AND R1.x = R2.x;