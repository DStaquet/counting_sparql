CREATE TEMP TABLE delta_prep_BGP_5439676414810165533 AS
SELECT G1.s AS y,
       G1.o AS z,
       G1.k_count
FROM delta_G G1
WHERE G1.p = 'http://example.org/edges/link';


CREATE TABLE delta_BGP_5439676414810165533 AS
SELECT y,
       z,
       SUM(k_count) AS k_count
FROM delta_prep_BGP_5439676414810165533
GROUP BY y,
         z;