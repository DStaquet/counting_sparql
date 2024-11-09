INSERT INTO nu_prep_Project_6111485832092847760 (x, y, k_count)
SELECT x,
       y,
       k_count
FROM Project_6111485832092847760;

INSERT INTO nu_prep_Project_6111485832092847760 (x, y, k_count)
SELECT x,
       y,
       k_count
FROM delta_Project_6111485832092847760;

INSERT INTO nu_Project_6111485832092847760 (x, y, k_count)
SELECT x,
       y,
       SUM(k_count) AS k_count
FROM nu_prep_Project_6111485832092847760
GROUP BY x,
         y
HAVING SUM(k_count) > 0;