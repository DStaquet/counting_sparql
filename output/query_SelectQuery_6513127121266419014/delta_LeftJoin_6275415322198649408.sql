INSERT INTO delta_LeftJoin_6275415322198649408(comment, f, label, p, producer, productFeature, propertyNumeric1, propertyNumeric2, propertyTextual1, propertyTextual2, propertyTextual3, propertyTextual4, propertyTextual5, k_count)
SELECT comment, f, label, p, producer, productFeature, propertyNumeric1, propertyNumeric2, propertyTextual1, propertyTextual2, propertyTextual3, propertyTextual4, propertyTextual5, r1.k_count as k_count
FROM delta_LeftJoin_5874294442988197449 AS r1 LEFT OUTER JOIN BGP_5599850506786390090 AS r2 ON TRUE;
INSERT INTO delta_LeftJoin_6275415322198649408
SELECT producer, propertyTextual3, p, propertyNumeric2, label, propertyTextual2, f, propertyTextual1, propertyTextual4, propertyNumeric1, productFeature, comment, propertyTextual5, r2.k_count as k_count FROM nu_LeftJoin_5874294442988197449 AS r1 LEFT OUTER JOIN delta_BGP_5599850506786390090 AS r2 ON 1 = 1 WHERE r2.k_count < 0;
