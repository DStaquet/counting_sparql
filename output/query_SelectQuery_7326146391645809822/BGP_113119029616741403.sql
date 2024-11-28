CREATE TABLE BGP_113119029616741403 (x, y1, y2, z, k_count INT) AS
SELECT G2.s AS x,
       G1.s AS y1,
       G3.s AS y2,
       G3.o AS z,
       G1.k_count AS k_count
FROM G G1,
     G G2,
     G G3
WHERE G1.p = 'http://example.org/edges/link'
  AND G2.p = 'http://example.org/edges/link'
  AND G1.s = G2.o
  AND G1.o = G3.s
  AND G3.p = 'http://example.org/edges/link';