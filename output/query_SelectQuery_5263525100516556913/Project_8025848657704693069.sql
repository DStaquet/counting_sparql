INSERT INTO Project_8025848657704693069(x, z, k_count)
SELECT x,
       z,
       SUM(k_count) AS k_count
FROM BGP_2691716057464995186
GROUP BY x,
         z;