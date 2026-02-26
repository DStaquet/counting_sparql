CREATE TABLE Join_8668205654064478100 AS
SELECT r1.w AS w,
       r2.x AS x,
       r1.y AS y,
       r1.k_count * r2.k_count AS k_count
FROM BGP_4828852104882819343 AS r1,
     BGP_8639977824181032562 AS r2
WHERE r1.y = r2.y;