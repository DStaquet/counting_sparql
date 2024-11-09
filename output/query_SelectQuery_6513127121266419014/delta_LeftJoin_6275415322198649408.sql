INSERT INTO delta_LeftJoin_6275415322198649408
SELECT comment, f, label, p, producer, productFeature, propertyNumeric1, propertyNumeric2, propertyTextual1, propertyTextual2, propertyTextual3, propertyTextual4, propertyTextual5, r1.k_count * r2.k_count as k_count
FROM delta_LeftJoin_5874294442988197449 AS r1 JOIN BGP_5599850506786390090 AS r2 ON TRUE
ON CONFLICT DO
UPDATE SET
	k_count = EXCLUDED.k_count + k_count
WHERE producer = EXCLUDED.producer AND propertyTextual3 = EXCLUDED.propertyTextual3 AND p = EXCLUDED.p AND propertyNumeric2 = EXCLUDED.propertyNumeric2 AND label = EXCLUDED.label AND propertyTextual2 = EXCLUDED.propertyTextual2 AND f = EXCLUDED.f AND propertyTextual1 = EXCLUDED.propertyTextual1 AND propertyTextual4 = EXCLUDED.propertyTextual4 AND propertyNumeric1 = EXCLUDED.propertyNumeric1 AND productFeature = EXCLUDED.productFeature AND comment = EXCLUDED.commentpropertyTextual5 = EXCLUDED.propertyTextual5;
INSERT INTO delta_LeftJoin_6275415322198649408
SELECT comment, f, label, p, producer, productFeature, propertyNumeric1, propertyNumeric2, propertyTextual1, propertyTextual2, propertyTextual3, propertyTextual4, propertyTextual5, r1.k_count * r2.k_count as k_count
FROM nu_LeftJoin_5874294442988197449 AS r1 JOIN delta_BGP_5599850506786390090 AS r2
ON TRUE
ON CONFLICT DO
UPDATE SET
	k_count = EXCLUDED.k_count + k_count
WHERE producer = EXCLUDED.producer AND propertyTextual3 = EXCLUDED.propertyTextual3 AND p = EXCLUDED.p AND propertyNumeric2 = EXCLUDED.propertyNumeric2 AND label = EXCLUDED.label AND propertyTextual2 = EXCLUDED.propertyTextual2 AND f = EXCLUDED.f AND propertyTextual1 = EXCLUDED.propertyTextual1 AND propertyTextual4 = EXCLUDED.propertyTextual4 AND propertyNumeric1 = EXCLUDED.propertyNumeric1 AND productFeature = EXCLUDED.productFeature AND comment = EXCLUDED.commentpropertyTextual5 = EXCLUDED.propertyTextual5;
INSERT INTO delta_LeftJoin_6275415322198649408
SELECT comment, f, label, p, producer, productFeature, propertyNumeric1, propertyNumeric2, propertyTextual1, propertyTextual2, propertyTextual3, propertyTextual4, coalesce(p2.propertyTextual5, 'UNBOUND'), p1.k_count as k_count
FROM delta_LeftJoin_5874294442988197449 AS p1
WHERE () NOT IN (SELECT  FROM BGP_5599850506786390090 AS p2)
ON CONFLICT DO
UPDATE SET
	k_count = EXCLUDED.k_count + k_count
WHERE comment = EXCLUDED.comment AND f = EXCLUDED.f AND label = EXCLUDED.label AND p = EXCLUDED.p AND producer = EXCLUDED.producer AND productFeature = EXCLUDED.productFeature AND propertyNumeric1 = EXCLUDED.propertyNumeric1 AND propertyNumeric2 = EXCLUDED.propertyNumeric2 AND propertyTextual1 = EXCLUDED.propertyTextual1 AND propertyTextual2 = EXCLUDED.propertyTextual2 AND propertyTextual3 = EXCLUDED.propertyTextual3 AND propertyTextual4 = EXCLUDED.propertyTextual4 AND propertyTextual5 = EXCLUDED.propertyTextual5;
INSERT INTO delta_LeftJoin_6275415322198649408
SELECT comment, f, label, p, producer, productFeature, propertyNumeric1, propertyNumeric2, propertyTextual1, propertyTextual2, propertyTextual3, propertyTextual4, coalesce(p2.propertyTextual5, 'UNBOUND'), p1.k_count as k_count
FROM nu_LeftJoin_5874294442988197449 AS p1, delta_BGP_5599850506786390090 AS delta_p2
ON CONFLICT DO
UPDATE SET
	k_count = EXCLUDED.k_count + k_count
WHERE comment = EXCLUDED.comment AND f = EXCLUDED.f AND label = EXCLUDED.label AND p = EXCLUDED.p AND producer = EXCLUDED.producer AND productFeature = EXCLUDED.productFeature AND propertyNumeric1 = EXCLUDED.propertyNumeric1 AND propertyNumeric2 = EXCLUDED.propertyNumeric2 AND propertyTextual1 = EXCLUDED.propertyTextual1 AND propertyTextual2 = EXCLUDED.propertyTextual2 AND propertyTextual3 = EXCLUDED.propertyTextual3 AND propertyTextual4 = EXCLUDED.propertyTextual4 AND propertyTextual5 = EXCLUDED.propertyTextual5;
INSERT INTO delta_LeftJoin_6275415322198649408
SELECT comment, f, label, p, producer, productFeature, propertyNumeric1, propertyNumeric2, propertyTextual1, propertyTextual2, propertyTextual3, propertyTextual4, coalesce(p2.propertyTextual5, 'UNBOUND'), -p1.k_count
FROM nu_LeftJoin_5874294442988197449 AS p1, delta_BGP_5599850506786390090 AS delta_p2
ON CONFLICT DO
UPDATE SET
	k_count = EXCLUDED.k_count + k_count
WHERE comment = EXCLUDED.comment AND f = EXCLUDED.f AND label = EXCLUDED.label AND p = EXCLUDED.p AND producer = EXCLUDED.producer AND productFeature = EXCLUDED.productFeature AND propertyNumeric1 = EXCLUDED.propertyNumeric1 AND propertyNumeric2 = EXCLUDED.propertyNumeric2 AND propertyTextual1 = EXCLUDED.propertyTextual1 AND propertyTextual2 = EXCLUDED.propertyTextual2 AND propertyTextual3 = EXCLUDED.propertyTextual3 AND propertyTextual4 = EXCLUDED.propertyTextual4 AND propertyTextual5 = EXCLUDED.propertyTextual5;
