CREATE TABLE delta_BGP_2691716057464995186 AS
SELECT x,
       y,
       z,
       SUM(k_count) AS k_count
FROM delta_prep_BGP_2691716057464995186
GROUP BY x,
         y,
         z;