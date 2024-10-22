INSERT INTO nu_prep_SelectQuery_5263525100516556913 (x, y, z, k_count)
SELECT x,
       y,
       z,
       k_count
FROM SelectQuery_5263525100516556913;

INSERT INTO nu_prep_SelectQuery_5263525100516556913 (x, y, z, k_count)
SELECT x,
       y,
       z,
       k_count
FROM delta_SelectQuery_5263525100516556913;

INSERT INTO nu_SelectQuery_5263525100516556913 (x, y, z, k_count)
SELECT x,
       y,
       z,
       SUM(k_count) AS k_count
FROM nu_prep_SelectQuery_5263525100516556913
GROUP BY x,
         y,
         z
HAVING SUM(k_count) > 0;