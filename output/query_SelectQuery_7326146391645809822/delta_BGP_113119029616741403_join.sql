CREATE TEMP TABLE BGP_1131190296167414032 AS
SELECT (CASE
            WHEN R1.z NOT NULL THEN R1.z
            ELSE R2.z
        END) AS z,
       (CASE
            WHEN R1.y1 NOT NULL THEN R1.y1
            ELSE R2.y1
        END) AS y1,
       (CASE
            WHEN R1.x NOT NULL THEN R1.x
            ELSE R2.x
        END) AS x,
       (CASE
            WHEN R1.y2 NOT NULL THEN R1.y2
            ELSE R2.y2
        END) AS y2,
       (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
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
     AND G3.p = 'http://example.org/edges/link') AS R1
FULL OUTER JOIN
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
     AND G3.p = 'http://example.org/edges/link') AS R2 ON R1.z = R2.zAND R1.y1 = R2.y1AND R1.x = R2.xAND R1.y2 = R2.y2
WHERE COALESCE(R1.k_count, 0) + COALESCE(R2.k_count, 0) > 0;

CREATE TABLE delta_BGP_113119029616741403 AS
SELECT (CASE
            WHEN R1.z NOT NULL THEN R1.z
            ELSE R2.z
        END) AS z,
       (CASE
            WHEN R1.y1 NOT NULL THEN R1.y1
            ELSE R2.y1
        END) AS y1,
       (CASE
            WHEN R1.x NOT NULL THEN R1.x
            ELSE R2.x
        END) AS x,
       (CASE
            WHEN R1.y2 NOT NULL THEN R1.y2
            ELSE R2.y2
        END) AS y2,
       (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
        END) AS k_count
FROM delta_join_BGP_113119029616741403_2 AS R1
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
     AND G3.p = 'http://example.org/edges/link') AS R2 ON R1.z = R2.z
AND R1.y1 = R2.y1
AND R1.x = R2.x
AND R1.y2 = R2.y2
WHERE COALESCE(R1.k_count, 0) + COALESCE(R2.k_count, 0) > 0;