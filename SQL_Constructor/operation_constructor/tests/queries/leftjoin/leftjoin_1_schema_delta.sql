CREATE TEMP TABLE prep_delta_LeftJoin_5062614984795814045 AS
SELECT r1.x AS x,
       r2.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM delta_BGP_747695058721694287 AS r1,
     BGP_4313253051102226119 AS r2
WHERE r1.x = r2.x;


INSERT INTO prep_delta_LeftJoin_5062614984795814045 (x, y, k_count)
SELECT r1.x AS x,
       r2.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM nu_BGP_747695058721694287 AS r1,
     delta_BGP_4313253051102226119 AS r2
WHERE r1.x = r2.x;


CREATE TABLE delta_LeftJoin_5062614984795814045 AS
SELECT r1.x,
       r1.y,
       SUM(r1.k_count) AS k_count
FROM prep_delta_LeftJoin_5062614984795814045 AS r1
GROUP BY r1.x,
         r1.y
HAVING SUM(r1.k_count) != 0;


CREATE TEMP TABLE prep_delta_LeftJoin_5062614984795814045_schema_5974201903695169563 AS
SELECT s1.x AS x,
       s1.k_count AS k_count
FROM delta_BGP_747695058721694287 AS s1
WHERE NOT EXISTS (
                  FROM BGP_4313253051102226119 AS s2
                  WHERE s1.x = s2.x);


INSERT INTO prep_delta_LeftJoin_5062614984795814045_schema_5974201903695169563 (x, k_count)
SELECT s1.x AS x,
       s1.k_count AS k_count
FROM nu_BGP_747695058721694287 AS s1
JOIN delta_BGP_4313253051102226119 AS s2 ON s1.x = s2.x
WHERE EXISTS (
              FROM BGP_4313253051102226119 AS s3
              WHERE s1.x = s3.x
                AND -s2.k_count = s3.k_count)
UNION
SELECT s1.x AS x, -s1.k_count AS k_count
FROM nu_BGP_747695058721694287 AS s1
JOIN delta_BGP_4313253051102226119 AS s2 ON s1.x = s2.x
WHERE NOT EXISTS (
                  FROM BGP_4313253051102226119 AS s3
                  WHERE s1.x = s3.x);


CREATE TABLE delta_LeftJoin_5062614984795814045_schema_5974201903695169563 AS
SELECT r1.x,
       SUM(r1.k_count) AS k_count
FROM prep_delta_LeftJoin_5062614984795814045_schema_5974201903695169563 AS r1
GROUP BY r1.x
HAVING SUM(r1.k_count) != 0;