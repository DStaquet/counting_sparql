CREATE TEMP TABLE delta_BGP_5439676414810165533_1 AS
SELECT G1.s AS y,
       G1.o AS z,
       G1.k_count
FROM delta_G G1
WHERE G1.p = 'http://example.org/edges/link';