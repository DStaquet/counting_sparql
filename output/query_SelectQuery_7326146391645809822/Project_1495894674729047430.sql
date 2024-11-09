INSERT INTO Project_1495894674729047430(x, z, k_count)
SELECT x,
       z,
       SUM(k_count) AS k_count
FROM BGP_113119029616741403
GROUP BY x,
         z;