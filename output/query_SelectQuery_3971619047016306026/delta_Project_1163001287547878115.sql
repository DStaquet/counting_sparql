CREATE TABLE delta_Project_1163001287547878115 AS
SELECT x,
       z,
       SUM(k_count) AS k_count
FROM delta_Join_4483357797573630587
GROUP BY x,
         z;