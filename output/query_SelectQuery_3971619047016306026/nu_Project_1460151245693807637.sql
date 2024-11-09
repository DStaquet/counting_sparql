CREATE TEMP TABLE nu_prep_Project_1460151245693807637 (y, k_count INT) AS
SELECT y,
       k_count
FROM Project_1460151245693807637;

INSERT INTO nu_prep_Project_1460151245693807637 (y, k_count)
SELECT y,
       k_count
FROM delta_Project_1460151245693807637;

CREATE TABLE nu_Project_1460151245693807637 (y, k_count INT) AS
SELECT y,
       SUM(k_count) AS k_count
FROM nu_prep_Project_1460151245693807637
GROUP BY y
HAVING SUM(k_count) > 0;