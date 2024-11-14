CREATE TEMP TABLE delta_BGP_4313253051102226119_1 AS
SELECT G1.s AS x,
       G1.o AS y,
       G1.k_count
FROM delta_G G1
WHERE G1.p = 'http://example.org/edges/link';