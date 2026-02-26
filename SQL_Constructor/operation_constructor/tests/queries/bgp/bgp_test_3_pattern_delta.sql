CREATE TEMP TABLE prep_delta_BGP_1643608900845163115 AS
SELECT G3.o AS w,
       G2.s AS x,
       G1.s AS y,
       G3.s AS z,
       G1.k_count
FROM delta_G G1,
     G G2,
     G G3
WHERE G1.p = 'http://example.org/edges/link'
  AND G2.p = 'http://example.org/edges/link'
  AND G1.s = G2.o
  AND G1.o = G3.s
  AND G3.p = 'http://example.org/edges/link';


INSERT INTO prep_delta_BGP_1643608900845163115 (w, x, y, z, k_count)
SELECT G3.o AS w,
       G2.s AS x,
       G1.s AS y,
       G3.s AS z,
       G2.k_count
FROM nu_G G1,
     delta_G G2,
     G G3
WHERE G1.p = 'http://example.org/edges/link'
  AND G2.p = 'http://example.org/edges/link'
  AND G1.s = G2.o
  AND G1.o = G3.s
  AND G3.p = 'http://example.org/edges/link';


INSERT INTO prep_delta_BGP_1643608900845163115 (w, x, y, z, k_count)
SELECT G3.o AS w,
       G2.s AS x,
       G1.s AS y,
       G3.s AS z,
       G3.k_count
FROM nu_G G1,
     nu_G G2,
     delta_G G3
WHERE G1.p = 'http://example.org/edges/link'
  AND G2.p = 'http://example.org/edges/link'
  AND G1.s = G2.o
  AND G1.o = G3.s
  AND G3.p = 'http://example.org/edges/link';


CREATE TABLE delta_BGP_1643608900845163115 AS
SELECT r1.w,
       r1.x,
       r1.y,
       r1.z,
       SUM(r1.k_count) AS k_count
FROM prep_delta_BGP_1643608900845163115 AS r1
GROUP BY r1.w,
         r1.x,
         r1.y,
         r1.z
HAVING SUM(r1.k_count) != 0;