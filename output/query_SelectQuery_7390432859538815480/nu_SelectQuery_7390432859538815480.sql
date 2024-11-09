CREATE TEMP TABLE nu_prep_SelectQuery_7390432859538815480 (x, y, z, k_count INT) AS
SELECT x,
       y,
       z,
       k_count
FROM SelectQuery_7390432859538815480;

INSERT INTO nu_prep_SelectQuery_7390432859538815480 (x, y, z, k_count)
SELECT x,
       y,
       z,
       k_count
FROM delta_SelectQuery_7390432859538815480;

CREATE TABLE nu_SelectQuery_7390432859538815480 (x, y, z, k_count INT) AS
SELECT x,
       y,
       z,
       SUM(k_count) AS k_count
FROM nu_prep_SelectQuery_7390432859538815480
GROUP BY x,
         y,
         z
HAVING SUM(k_count) > 0;