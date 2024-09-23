INSERT INTO delta_Project_8708420436429866325(x, z, k_count)
SELECT x,
       z,
       SUM(k_count) AS k_count
FROM delta_BGP_8402537564714151730
GROUP BY x,
         z;