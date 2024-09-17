INSERT INTO nu_prep_BGP_5631193804359433266 (o, p, s, x, y, k_count)
SELECT o,
       p,
       s,
       x,
       y,
       k_count
FROM BGP_5631193804359433266;

INSERT INTO nu_prep_BGP_5631193804359433266 (o, p, s, x, y, k_count)
SELECT o,
       p,
       s,
       x,
       y,
       k_count
FROM delta_BGP_5631193804359433266;

INSERT INTO nu_BGP_5631193804359433266 (o, p, s, x, y, k_count)
SELECT o,
       p,
       s,
       x,
       y,
       SUM(k_count) AS k_count
FROM nu_prep_BGP_5631193804359433266
GROUP BY o,
         p,
         s,
         x,
         y;

DELETE
FROM nu_BGP_5631193804359433266
WHERE k_count <= 0;