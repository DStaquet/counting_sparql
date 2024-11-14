CREATE TEMP TABLE nu_prep_BGP_5439676414810165533 (y, z, k_count INT) AS
SELECT y,
       z,
       k_count
FROM BGP_5439676414810165533;

INSERT INTO nu_prep_BGP_5439676414810165533 (y, z, k_count)
SELECT y,
       z,
       k_count
FROM delta_BGP_5439676414810165533;

CREATE TABLE nu_BGP_5439676414810165533 (y, z, k_count INT) AS
SELECT y,
       z,
       SUM(k_count) AS k_count
FROM nu_prep_BGP_5439676414810165533
GROUP BY y,
         z
HAVING SUM(k_count) > 0;