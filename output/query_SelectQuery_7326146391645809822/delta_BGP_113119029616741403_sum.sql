CREATE TABLE delta_BGP_113119029616741403 AS
SELECT x,
       y1,
       y2,
       z,
       SUM(k_count) AS k_count
FROM delta_prep_BGP_113119029616741403
GROUP BY x,
         y1,
         y2,
         z;