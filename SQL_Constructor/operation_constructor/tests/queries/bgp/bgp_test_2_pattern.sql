CREATE TABLE BGP_7479567498023511432 AS
SELECT G1.s AS x,
       G2.s AS y,
       G2.o AS z,
       G1.k_count AS k_count
FROM G G1,
     G G2
WHERE G1.p = '<http://example.org/edges/link>'
  AND G1.o = G2.s
  AND G2.p = '<http://example.org/edges/link>';