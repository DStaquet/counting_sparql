INSERT INTO BGP_2874745891700759920 (t1, t2, t3, t4, t5, x, y, k_count)
SELECT G1.s AS t1,
       G2.s AS t2,
       G3.s AS t3,
       G4.s AS t4,
       G5.s AS t5,
       G6.s AS x,
       G5.o AS y,
       G1.k_count AS k_count
FROM G G1,
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
  AND G1.s = G6.o;