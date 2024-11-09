CREATE TEMP TABLE nu_prep_ToMultiSet_8105340002863607763 (y, z, k_count INT) AS
SELECT y,
       z,
       k_count
FROM ToMultiSet_8105340002863607763;

INSERT INTO nu_prep_ToMultiSet_8105340002863607763 (y, z, k_count)
SELECT y,
       z,
       k_count
FROM delta_ToMultiSet_8105340002863607763;

CREATE TABLE nu_ToMultiSet_8105340002863607763 (y, z, k_count INT) AS
SELECT y,
       z,
       SUM(k_count) AS k_count
FROM nu_prep_ToMultiSet_8105340002863607763
GROUP BY y,
         z
HAVING SUM(k_count) > 0;