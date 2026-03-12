CREATE TABLE BGP_1643608900845163115 AS
SELECT G3.o AS w,
       G2.s AS x,
       G1.s AS y,
       G3.s AS z,
       G1.k_count AS k_count
FROM G G1,
     G G2,
     G G3
WHERE G1.p = '<http://example.org/edges/link>'
  AND G2.p = '<http://example.org/edges/link>'
  AND G1.s = G2.o
  AND G1.o = G3.s
  AND G3.p = '<http://example.org/edges/link>';