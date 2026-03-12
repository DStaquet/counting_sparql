CREATE TEMP TABLE delta_BGP_1643608900845163115_0 AS
SELECT G3.o AS w,
       G2.s AS x,
       G1.s AS y,
       G3.s AS z,
       G1.k_count
FROM delta_G G1,
     G G2,
     G G3
WHERE G1.p = '<http://example.org/edges/link>'
  AND G2.p = '<http://example.org/edges/link>'
  AND G1.s = G2.o
  AND G1.o = G3.s
  AND G3.p = '<http://example.org/edges/link>';


CREATE TEMP TABLE delta_BGP_1643608900845163115_1 AS
SELECT G3.o AS w,
       G2.s AS x,
       G1.s AS y,
       G3.s AS z,
       G2.k_count
FROM nu_G G1,
     delta_G G2,
     G G3
WHERE G1.p = '<http://example.org/edges/link>'
  AND G2.p = '<http://example.org/edges/link>'
  AND G1.s = G2.o
  AND G1.o = G3.s
  AND G3.p = '<http://example.org/edges/link>';


CREATE TEMP TABLE delta_BGP_1643608900845163115_temp_1 AS
SELECT (CASE
            WHEN R1.y NOT NULL THEN R1.y
            ELSE R2.y
        END) AS y,
       (CASE
            WHEN R1.x NOT NULL THEN R1.x
            ELSE R2.x
        END) AS x,
       (CASE
            WHEN R1.w NOT NULL THEN R1.w
            ELSE R2.w
        END) AS w,
       (CASE
            WHEN R1.z NOT NULL THEN R1.z
            ELSE R2.z
        END) AS z,
       (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
        END) AS k_count
FROM delta_BGP_1643608900845163115_0 AS R1
FULL OUTER JOIN delta_BGP_1643608900845163115_1 AS R2 ON R1.y = R2.y
AND R1.x = R2.x
AND R1.w = R2.w
AND R1.z = R2.z;

CREATE TEMP TABLE delta_BGP_1643608900845163115_2 AS
SELECT G3.o AS w,
       G2.s AS x,
       G1.s AS y,
       G3.s AS z,
       G3.k_count
FROM nu_G G1,
     nu_G G2,
     delta_G G3
WHERE G1.p = '<http://example.org/edges/link>'
  AND G2.p = '<http://example.org/edges/link>'
  AND G1.s = G2.o
  AND G1.o = G3.s
  AND G3.p = '<http://example.org/edges/link>';


CREATE TEMP TABLE delta_BGP_1643608900845163115 AS
SELECT (CASE
            WHEN R1.y NOT NULL THEN R1.y
            ELSE R2.y
        END) AS y,
       (CASE
            WHEN R1.x NOT NULL THEN R1.x
            ELSE R2.x
        END) AS x,
       (CASE
            WHEN R1.w NOT NULL THEN R1.w
            ELSE R2.w
        END) AS w,
       (CASE
            WHEN R1.z NOT NULL THEN R1.z
            ELSE R2.z
        END) AS z,
       (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
        END) AS k_count
FROM delta_BGP_1643608900845163115_temp_1 AS R1
FULL OUTER JOIN delta_BGP_1643608900845163115_2 AS R2 ON R1.y = R2.y
AND R1.x = R2.x
AND R1.w = R2.w
AND R1.z = R2.z
WHERE coalesce(R1.k_count, 0) + coalesce(R2.k_count, 0) != 0;