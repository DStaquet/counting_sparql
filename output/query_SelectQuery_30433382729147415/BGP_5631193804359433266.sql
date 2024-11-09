INSERT INTO BGP_5631193804359433266 (o, p, s, x, y, k_count)
SELECT G1.o AS o,
       G1.p AS p,
       G1.s AS s,
       G2.p AS x,
       G2.o AS y,
       G1.k_count AS k_count
FROM G G1,
     G G2
WHERE G1.s = G2.s;