INSERT INTO delta_prep_BGP_5631193804359433266 (o, p, s, x, y, k_count)
SELECT G1.o AS o,
       G1.p AS p,
       G1.s AS s,
       G2.p AS x,
       G2.o AS y,
       G1.k_count
FROM delta_G G1,
     G G2
WHERE G1.s = G2.s;


INSERT INTO delta_prep_BGP_5631193804359433266 (o, p, s, x, y, k_count)
SELECT G1.o AS o,
       G1.p AS p,
       G1.s AS s,
       G2.p AS x,
       G2.o AS y,
       G2.k_count
FROM nu_G G1,
     delta_G G2
WHERE G1.s = G2.s;


INSERT INTO delta_BGP_5631193804359433266 (o, p, s, x, y, k_count)
SELECT o,
       p,
       s,
       x,
       y,
       SUM(k_count) AS k_count
FROM delta_prep_BGP_5631193804359433266
GROUP BY o,
         p,
         s,
         x,
         y;