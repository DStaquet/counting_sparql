CREATE TEMP TABLE prep_delta_Minus_9178504235855424463 AS
SELECT s1.x AS x,
       s1.k_count AS k_count
FROM delta_BGP_6412654939285419064 AS s1
WHERE NOT EXISTS (
                  FROM Union_880182546380184037_schema_4427885478980723971 AS s2
                  WHERE s1.x = s2.x)
  AND NOT EXISTS (
                  FROM Union_880182546380184037_schema_1048960622663883677 AS s3
                  WHERE s1.x = s3.x);


INSERT INTO prep_delta_Minus_9178504235855424463 (x, k_count)
SELECT s1.x AS x,
       s1.k_count AS k_count
FROM nu_BGP_6412654939285419064 AS s1
JOIN delta_Union_880182546380184037_schema_4427885478980723971 AS s2 ON s1.x = s2.x
WHERE NOT EXISTS (
                  FROM nu_Union_880182546380184037_schema_4427885478980723971 AS s3
                  WHERE s1.x = s3.x)
  AND NOT EXISTS (
                  FROM nu_Union_880182546380184037_schema_1048960622663883677 AS s4
                  WHERE s1.x = s4.x)
UNION
SELECT s1.x AS x, -s1.k_count AS k_count
FROM nu_BGP_6412654939285419064 AS s1
JOIN delta_Union_880182546380184037_schema_4427885478980723971 AS s2 ON s1.x = s2.x
WHERE NOT EXISTS (
                  FROM Union_880182546380184037_schema_4427885478980723971 AS s3
                  WHERE s1.x = s3.x)
  AND NOT EXISTS (
                  FROM Union_880182546380184037_schema_1048960622663883677 AS s4
                  WHERE s1.x = s4.x);


INSERT INTO prep_delta_Minus_9178504235855424463 (x, k_count)
SELECT s1.x AS x,
       s1.k_count AS k_count
FROM nu_BGP_6412654939285419064 AS s1
JOIN delta_Union_880182546380184037_schema_1048960622663883677 AS s2 ON s1.x = s2.x
WHERE NOT EXISTS (
                  FROM nu_Union_880182546380184037_schema_4427885478980723971 AS s3
                  WHERE s1.x = s3.x)
  AND NOT EXISTS (
                  FROM nu_Union_880182546380184037_schema_1048960622663883677 AS s4
                  WHERE s1.x = s4.x)
UNION
SELECT s1.x AS x, -s1.k_count AS k_count
FROM nu_BGP_6412654939285419064 AS s1
JOIN delta_Union_880182546380184037_schema_1048960622663883677 AS s2 ON s1.x = s2.x
WHERE NOT EXISTS (
                  FROM Union_880182546380184037_schema_4427885478980723971 AS s3
                  WHERE s1.x = s3.x)
  AND NOT EXISTS (
                  FROM Union_880182546380184037_schema_1048960622663883677 AS s4
                  WHERE s1.x = s4.x);


CREATE TABLE delta_Minus_9178504235855424463 AS
SELECT r1.x,
       SUM(r1.k_count) AS k_count
FROM prep_delta_Minus_9178504235855424463 AS r1
GROUP BY r1.x
HAVING SUM(r1.k_count) != 0;