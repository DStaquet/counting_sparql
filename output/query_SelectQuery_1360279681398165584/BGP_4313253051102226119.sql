CREATE TABLE BGP_4313253051102226119 (x, y, k_count INT) AS
SELECT G1.s AS x,
       G1.o AS y,
       G1.k_count AS k_count
FROM G G1
WHERE G1.p = 'http://example.org/edges/link';