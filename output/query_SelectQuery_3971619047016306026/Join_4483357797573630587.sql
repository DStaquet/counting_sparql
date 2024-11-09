CREATE TABLE Join_4483357797573630587 AS
SELECT r1.x AS x,
       r1.y AS y,
       r1.z AS z,
       r1.k_count * r2.k_count AS k_count
FROM BGP_4313253051102226119 AS r1
JOIN ToMultiSet_8105340002863607763 AS r2 ON r1.y = r2.y;