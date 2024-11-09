INSERT INTO nu_prep_SelectQuery_7326146391645809822 (x, y1, y2, z, k_count)
SELECT x,
       y1,
       y2,
       z,
       k_count
FROM SelectQuery_7326146391645809822;

INSERT INTO nu_prep_SelectQuery_7326146391645809822 (x, y1, y2, z, k_count)
SELECT x,
       y1,
       y2,
       z,
       k_count
FROM delta_SelectQuery_7326146391645809822;

INSERT INTO nu_SelectQuery_7326146391645809822 (x, y1, y2, z, k_count)
SELECT x,
       y1,
       y2,
       z,
       SUM(k_count) AS k_count
FROM nu_prep_SelectQuery_7326146391645809822
GROUP BY x,
         y1,
         y2,
         z
HAVING SUM(k_count) > 0;