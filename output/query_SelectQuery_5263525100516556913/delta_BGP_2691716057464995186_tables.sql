CREATE TEMP TABLE delta_BGP_2691716057464995186_1 AS
SELECT G1.s AS x,
       G2.s AS y,
       G2.o AS z,
       G1.k_count
FROM delta_G G1,
     G G2
WHERE G1.p = 'http://example.org/edges/link'
  AND G1.o = G2.s
  AND G2.p = 'http://example.org/edges/link';


CREATE TEMP TABLE delta_BGP_2691716057464995186_2 AS
SELECT G1.s AS x,
       G2.s AS y,
       G2.o AS z,
       G2.k_count
FROM nu_G G1,
     delta_G G2
WHERE G1.p = 'http://example.org/edges/link'
  AND G1.o = G2.s
  AND G2.p = 'http://example.org/edges/link';