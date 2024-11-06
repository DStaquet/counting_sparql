CREATE TEMP TABLE delta_BGP_113119029616741403_1 AS
SELECT G2.s AS x,
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
  AND G3.p = 'http://example.org/edges/link';


CREATE TEMP TABLE delta_BGP_113119029616741403_2 AS
SELECT G2.s AS x,
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
  AND G3.p = 'http://example.org/edges/link';


CREATE TEMP TABLE delta_BGP_113119029616741403_3 AS
SELECT G2.s AS x,
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
  AND G3.p = 'http://example.org/edges/link';