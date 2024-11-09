CREATE TEMP TABLE nu_prep_Join_4483357797573630587 (x, y, z, k_count INT) AS
SELECT x,
       y,
       z,
       k_count
FROM Join_4483357797573630587;

INSERT INTO nu_prep_Join_4483357797573630587 (x, y, z, k_count)
SELECT x,
       y,
       z,
       k_count
FROM delta_Join_4483357797573630587;

CREATE TABLE nu_Join_4483357797573630587 (x, y, z, k_count INT) AS
SELECT x,
       y,
       z,
       SUM(k_count) AS k_count
FROM nu_prep_Join_4483357797573630587
GROUP BY x,
         y,
         z
HAVING SUM(k_count) > 0;