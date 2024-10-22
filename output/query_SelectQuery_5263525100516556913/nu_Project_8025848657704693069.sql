INSERT INTO nu_prep_Project_8025848657704693069 (x, z, k_count)
SELECT x,
       z,
       k_count
FROM Project_8025848657704693069;

INSERT INTO nu_prep_Project_8025848657704693069 (x, z, k_count)
SELECT x,
       z,
       k_count
FROM delta_Project_8025848657704693069;

INSERT INTO nu_Project_8025848657704693069 (x, z, k_count)
SELECT x,
       z,
       SUM(k_count) AS k_count
FROM nu_prep_Project_8025848657704693069
GROUP BY x,
         z
HAVING SUM(k_count) > 0;