CREATE TEMP TABLE nu_prep_BGP_113119029616741403 (x, y1, y2, z, k_count INT) AS
SELECT x,
       y1,
       y2,
       z,
       k_count
FROM BGP_113119029616741403;

INSERT INTO nu_prep_BGP_113119029616741403 (x, y1, y2, z, k_count)
SELECT x,
       y1,
       y2,
       z,
       k_count
FROM delta_BGP_113119029616741403;

CREATE TABLE nu_BGP_113119029616741403 (x, y1, y2, z, k_count INT) AS
SELECT x,
       y1,
       y2,
       z,
       SUM(k_count) AS k_count
FROM nu_prep_BGP_113119029616741403
GROUP BY x,
         y1,
         y2,
         z
HAVING SUM(k_count) > 0;