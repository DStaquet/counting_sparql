CREATE TEMP TABLE prep_delta_BGP_7479567498023511432 AS
SELECT G1.s AS x,
       G2.s AS y,
       G2.o AS z,
       G1.k_count
FROM delta_G G1,
     G G2
WHERE G1.p = '<http://example.org/edges/link>'
  AND G1.o = G2.s
  AND G2.p = '<http://example.org/edges/link>';


INSERT INTO prep_delta_BGP_7479567498023511432 (x, y, z, k_count)
SELECT G1.s AS x,
       G2.s AS y,
       G2.o AS z,
       G2.k_count
FROM nu_G G1,
     delta_G G2
WHERE G1.p = '<http://example.org/edges/link>'
  AND G1.o = G2.s
  AND G2.p = '<http://example.org/edges/link>';


CREATE TABLE delta_BGP_7479567498023511432 AS
SELECT r1.x,
       r1.y,
       r1.z,
       SUM(r1.k_count) AS k_count
FROM prep_delta_BGP_7479567498023511432 AS r1
GROUP BY r1.x,
         r1.y,
         r1.z
HAVING SUM(r1.k_count) != 0;