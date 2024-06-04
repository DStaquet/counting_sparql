INSERT INTO delta_Minus_6349949983044087158
SELECT label, p1, p3, product, p1.k_count as k_count
FROM delta_Filter_7107022666642246863 AS p1
WHERE (p1.product) NOT IN (SELECT p2.product FROM BGP_860228541250160113 AS p2)
ON CONFLICT DO
UPDATE SET
	k_count = EXCLUDED.k_count + k_count
WHERE label = EXCLUDED.label AND p1 = EXCLUDED.p1 AND p3 = EXCLUDED.p3 AND product = EXCLUDED.product AND ;
INSERT INTO delta_Minus_6349949983044087158
SELECT label, p1, p3, product, p1.k_count as k_count
FROM nu_Filter_7107022666642246863 AS p1, delta_BGP_860228541250160113 AS delta_p2
WHERE (p1.product = delta_p2.product, -delta_p2.k_count) IN (SELECT product, k_count
FROM BGP_860228541250160113 AS p2)
ON CONFLICT DO
UPDATE SET
	k_count = EXCLUDED.k_count + k_count
WHERE label = EXCLUDED.label AND p1 = EXCLUDED.p1 AND p3 = EXCLUDED.p3 AND product = EXCLUDED.product AND ;
INSERT INTO delta_Minus_6349949983044087158
SELECT label, p1, p3, product, -p1.k_count
FROM nu_Filter_7107022666642246863 AS p1, delta_BGP_860228541250160113 AS delta_p2
WHERE (p1.product = delta_p2.product, k_count) NOT IN (SELECT product, k_count
FROM BGP_860228541250160113 AS p2)
ON CONFLICT DO
UPDATE SET
	k_count = EXCLUDED.k_count + k_count
WHERE label = EXCLUDED.label AND p1 = EXCLUDED.p1 AND p3 = EXCLUDED.p3 AND product = EXCLUDED.product AND ;
