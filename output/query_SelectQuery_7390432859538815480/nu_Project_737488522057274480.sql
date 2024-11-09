CREATE TEMP TABLE nu_prep_Project_737488522057274480 (x, z, k_count INT) AS
SELECT x,
       z,
       k_count
FROM Project_737488522057274480;

INSERT INTO nu_prep_Project_737488522057274480 (x, z, k_count)
SELECT x,
       z,
       k_count
FROM delta_Project_737488522057274480;

CREATE TABLE nu_Project_737488522057274480 (x, z, k_count INT) AS
SELECT x,
       z,
       SUM(k_count) AS k_count
FROM nu_prep_Project_737488522057274480
GROUP BY x,
         z
HAVING SUM(k_count) > 0;