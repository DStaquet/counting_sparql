CREATE TEMP TABLE nu_prep_Project_4719627365682408729 (x, z, k_count INT) AS
SELECT x,
       z,
       k_count
FROM Project_4719627365682408729;

INSERT INTO nu_prep_Project_4719627365682408729 (x, z, k_count)
SELECT x,
       z,
       k_count
FROM delta_Project_4719627365682408729;

CREATE TABLE nu_Project_4719627365682408729 (x, z, k_count INT) AS
SELECT x,
       z,
       SUM(k_count) AS k_count
FROM nu_prep_Project_4719627365682408729
GROUP BY x,
         z
HAVING SUM(k_count) > 0;