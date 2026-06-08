SELECT x,
       y,
       SUM(k_count) AS k_count
FROM BGP_7148062387023275411
GROUP BY x,
         y;