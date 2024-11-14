CREATE TEMP TABLE nu_prep_Project_7268717039862799428 (x, z, k_count INT) AS
SELECT x,
       z,
       k_count
FROM Project_7268717039862799428;

INSERT INTO nu_prep_Project_7268717039862799428 (x, z, k_count)
SELECT x,
       z,
       k_count
FROM delta_Project_7268717039862799428;

CREATE TABLE nu_Project_7268717039862799428 (x, z, k_count INT) AS
SELECT x,
       z,
       SUM(k_count) AS k_count
FROM nu_prep_Project_7268717039862799428
GROUP BY x,
         z
HAVING SUM(k_count) > 0;