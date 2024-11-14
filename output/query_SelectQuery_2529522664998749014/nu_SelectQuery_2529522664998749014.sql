CREATE TEMP TABLE nu_prep_SelectQuery_2529522664998749014 (x, y, z, k_count INT) AS
SELECT x,
       y,
       z,
       k_count
FROM SelectQuery_2529522664998749014;

INSERT INTO nu_prep_SelectQuery_2529522664998749014 (x, y, z, k_count)
SELECT x,
       y,
       z,
       k_count
FROM delta_SelectQuery_2529522664998749014;

CREATE TABLE nu_SelectQuery_2529522664998749014 (x, y, z, k_count INT) AS
SELECT x,
       y,
       z,
       SUM(k_count) AS k_count
FROM nu_prep_SelectQuery_2529522664998749014
GROUP BY x,
         y,
         z
HAVING SUM(k_count) > 0;