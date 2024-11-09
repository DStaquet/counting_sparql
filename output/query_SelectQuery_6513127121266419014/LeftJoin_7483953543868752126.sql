INSERT INTO LeftJoin_7483953543868752126
SELECT comment, f, label, p, producer, productFeature, propertyNumeric1, propertyNumeric2, propertyTextual1, propertyTextual2, propertyTextual3, propertyTextual4, propertyTextual5, propertyNumeric4, r1.k_count * r2.k_count as k_count
FROM LeftJoin_6275415322198649408 AS r1 JOIN BGP_405584237077899936 AS r2 
ON CONFLICT DO
UPDATE SET
	k_count = EXCLUDED.k_count + k_count
WHERE comment = EXCLUDED.comment AND f = EXCLUDED.f AND label = EXCLUDED.label AND p = EXCLUDED.p AND producer = EXCLUDED.producer AND productFeature = EXCLUDED.productFeature AND propertyNumeric1 = EXCLUDED.propertyNumeric1 AND propertyNumeric2 = EXCLUDED.propertyNumeric2 AND propertyTextual1 = EXCLUDED.propertyTextual1 AND propertyTextual2 = EXCLUDED.propertyTextual2 AND propertyTextual3 = EXCLUDED.propertyTextual3 AND propertyTextual4 = EXCLUDED.propertyTextual4 AND propertyTextual5 = EXCLUDED.propertyTextual5propertyNumeric4 = EXCLUDED.propertyNumeric4;
INSERT INTO LeftJoin_7483953543868752126
SELECT comment, f, label, p, producer, productFeature, propertyNumeric1, propertyNumeric2, propertyTextual1, propertyTextual2, propertyTextual3, propertyTextual4, propertyTextual5, coalesce(p2.propertyNumeric4, 'UNBOUND'), p1.k_count as k_count
FROM LeftJoin_6275415322198649408 AS p1
WHERE () NOT IN (SELECT  FROM BGP_405584237077899936 AS p2)
ON CONFLICT DO
UPDATE SET
	k_count = EXCLUDED.k_count + k_count
WHERE comment = EXCLUDED.comment AND f = EXCLUDED.f AND label = EXCLUDED.label AND p = EXCLUDED.p AND producer = EXCLUDED.producer AND productFeature = EXCLUDED.productFeature AND propertyNumeric1 = EXCLUDED.propertyNumeric1 AND propertyNumeric2 = EXCLUDED.propertyNumeric2 AND propertyTextual1 = EXCLUDED.propertyTextual1 AND propertyTextual2 = EXCLUDED.propertyTextual2 AND propertyTextual3 = EXCLUDED.propertyTextual3 AND propertyTextual4 = EXCLUDED.propertyTextual4 AND propertyTextual5 = EXCLUDED.propertyTextual5 AND propertyNumeric4 = EXCLUDED.propertyNumeric4;
