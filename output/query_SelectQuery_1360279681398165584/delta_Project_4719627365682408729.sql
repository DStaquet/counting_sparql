CREATE TABLE delta_Project_4719627365682408729 AS
SELECT x,
       z,
       SUM(k_count) AS k_count
FROM delta_Join_5968519747945714539
GROUP BY x,
         z;