CREATE TEMP TABLE nu_prep_Join_5968519747945714539 (x, y, z, k_count INT) AS
SELECT x,
       y,
       z,
       k_count
FROM Join_5968519747945714539;

INSERT INTO nu_prep_Join_5968519747945714539 (x, y, z, k_count)
SELECT x,
       y,
       z,
       k_count
FROM delta_Join_5968519747945714539;

CREATE TABLE nu_Join_5968519747945714539 (x, y, z, k_count INT) AS
SELECT x,
       y,
       z,
       SUM(k_count) AS k_count
FROM nu_prep_Join_5968519747945714539
GROUP BY x,
         y,
         z
HAVING SUM(k_count) > 0;