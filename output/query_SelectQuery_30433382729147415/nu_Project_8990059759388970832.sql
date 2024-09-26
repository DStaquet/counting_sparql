INSERT INTO nu_prep_Project_8990059759388970832 (s, x, k_count)
SELECT s,
       x,
       k_count
FROM Project_8990059759388970832;

INSERT INTO nu_prep_Project_8990059759388970832 (s, x, k_count)
SELECT s,
       x,
       k_count
FROM delta_Project_8990059759388970832;

INSERT INTO nu_Project_8990059759388970832 (s, x, k_count)
SELECT s,
       x,
       SUM(k_count) AS k_count
FROM nu_prep_Project_8990059759388970832
GROUP BY s,
         x
HAVING SUM(k_count) > 0;