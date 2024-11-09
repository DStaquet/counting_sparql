INSERT INTO nu_prep_SelectQuery_30433382729147415 (o, p, s, x, y, k_count)
SELECT o,
       p,
       s,
       x,
       y,
       k_count
FROM SelectQuery_30433382729147415;

INSERT INTO nu_prep_SelectQuery_30433382729147415 (o, p, s, x, y, k_count)
SELECT o,
       p,
       s,
       x,
       y,
       k_count
FROM delta_SelectQuery_30433382729147415;

INSERT INTO nu_SelectQuery_30433382729147415 (o, p, s, x, y, k_count)
SELECT o,
       p,
       s,
       x,
       y,
       SUM(k_count) AS k_count
FROM nu_prep_SelectQuery_30433382729147415
GROUP BY o,
         p,
         s,
         x,
         y
HAVING SUM(k_count) > 0;