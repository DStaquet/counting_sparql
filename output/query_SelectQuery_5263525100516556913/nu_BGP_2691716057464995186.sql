INSERT INTO nu_prep_BGP_2691716057464995186 (x, y, z, k_count)
SELECT x,
       y,
       z,
       k_count
FROM BGP_2691716057464995186;

INSERT INTO nu_prep_BGP_2691716057464995186 (x, y, z, k_count)
SELECT x,
       y,
       z,
       k_count
FROM delta_BGP_2691716057464995186;

INSERT INTO nu_BGP_2691716057464995186 (x, y, z, k_count)
SELECT x,
       y,
       z,
       SUM(k_count) AS k_count
FROM nu_prep_BGP_2691716057464995186
GROUP BY x,
         y,
         z
HAVING SUM(k_count) > 0;