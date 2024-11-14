CREATE TABLE delta_Project_7268717039862799428 AS
SELECT x,
       z,
       SUM(k_count) AS k_count
FROM delta_Union_5968519747945714539
GROUP BY x,
         z;