CREATE TEMP TABLE nu_prep_Filter_3699958788462208976 (x, y, z, k_count INT) AS
SELECT x,
       y,
       z,
       k_count
FROM Filter_3699958788462208976;

INSERT INTO nu_prep_Filter_3699958788462208976 (x, y, z, k_count)
SELECT x,
       y,
       z,
       k_count
FROM delta_Filter_3699958788462208976;

CREATE TABLE nu_Filter_3699958788462208976 (x, y, z, k_count INT) AS
SELECT x,
       y,
       z,
       SUM(k_count) AS k_count
FROM nu_prep_Filter_3699958788462208976
GROUP BY x,
         y,
         z
HAVING SUM(k_count) > 0;