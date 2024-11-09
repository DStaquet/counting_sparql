CREATE TABLE Project_737488522057274480 AS
SELECT x,
       z,
       SUM(k_count) AS k_count
FROM Filter_3699958788462208976
GROUP BY x,
         z;