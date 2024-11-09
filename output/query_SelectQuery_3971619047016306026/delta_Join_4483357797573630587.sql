CREATE TABLE delta_Join_4483357797573630587 AS
SELECT r1.x AS x,
       r1.y AS y,
       r1.z AS z,
       r1.k_count * r2.k_count AS k_count
FROM delta_BGP_4313253051102226119 AS r1
JOIN ToMultiSet_8105340002863607763 AS r2 ON r1.y = r2.y;


INSERT INTO delta_Join_4483357797573630587 (x, y, z, k_count)
SELECT r1.x AS x,
       r1.y AS y,
       r1.z AS z,
       r1.k_count * r2.k_count AS k_count
FROM nu_BGP_4313253051102226119 AS r1
JOIN delta_ToMultiSet_8105340002863607763 AS r2 ON r1.y = r2.y;


CREATE TABLE delta_Join_4483357797573630587 AS
SELECT x,
       y,
       z,
       SUM(k_count) AS k_count
FROM delta_prep_Join_4483357797573630587
GROUP BY x,
         y,
         z;