CREATE TABLE delta_Project_8025848657704693069 AS
SELECT x,
       z,
       SUM(k_count) AS k_count
FROM delta_BGP_2691716057464995186
GROUP BY x,
         z;