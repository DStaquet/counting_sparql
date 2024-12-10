CREATE TEMP TABLE Join_8039763548589018781_0 AS
SELECT r1.w AS w,
       r1.y AS y,
       r2.x AS x,
       r1.k_count * r2.k_count AS k_count
FROM BGP_5127379026335911785 AS r1,
     Union_3180718904663486803_schema_5536938746033674259 AS r2 ON r1.y = r2.y;


CREATE TEMP TABLE Join_8039763548589018781_1 AS
SELECT r1.w AS w,
       r1.y AS y,
       r2.x AS x,
       r1.k_count * r2.k_count AS k_count
FROM BGP_5127379026335911785 AS r1,
     Union_3180718904663486803_schema_122147079200776137 AS r2 ON r1.w = r2.w;


CREATE TABLE Join_8039763548589018781 AS
SELECT (CASE
            WHEN R1.y NOT NULL THEN R1.y
            ELSE R2.y
        END) AS y,
       (CASE
            WHEN R1.x NOT NULL THEN R1.x
            ELSE R2.x
        END) AS x,
       (CASE
            WHEN R1.w NOT NULL THEN R1.w
            ELSE R2.w
        END) AS w,
       (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
        END) AS k_count
FROM Join_8039763548589018781_0 AS R1
FULL OUTER JOIN Join_8039763548589018781_1 AS R2 ON R1.y = R2.y
AND R1.x = R2.x
AND R1.w = R2.w;