INSERT INTO Project_6111485832092847760(x, y, k_count)
SELECT x,
       y,
       SUM(k_count) AS k_count
FROM BGP_2874745891700759920
GROUP BY x,
         y;