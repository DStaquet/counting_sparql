CREATE TABLE delta_Project_1495894674729047430 AS
SELECT x,
       z,
       SUM(k_count) AS k_count
FROM delta_BGP_113119029616741403
GROUP BY x,
         z;