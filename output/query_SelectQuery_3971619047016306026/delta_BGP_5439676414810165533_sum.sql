CREATE TABLE delta_BGP_5439676414810165533 AS
SELECT y,
       z,
       SUM(k_count) AS k_count
FROM delta_prep_BGP_5439676414810165533
GROUP BY y,
         z;