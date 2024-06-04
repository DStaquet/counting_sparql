INSERT INTO delta_LeftJoin_5874294442988197449(comment, f, label, p, producer, productFeature, propertyNumeric1, propertyNumeric2, propertyTextual1, propertyTextual2, propertyTextual3, propertyTextual4, k_count)
SELECT comment, f, label, p, producer, productFeature, propertyNumeric1, propertyNumeric2, propertyTextual1, propertyTextual2, propertyTextual3, propertyTextual4, r1.k_count as k_count
FROM delta_BGP_6096836102481082072 AS r1 LEFT OUTER JOIN BGP_1320827854144898937 AS r2 ON TRUE;
INSERT INTO delta_LeftJoin_5874294442988197449
SELECT producer, propertyTextual3, p, propertyNumeric2, label, propertyTextual2, f, propertyTextual1, propertyNumeric1, productFeature, comment, propertyTextual4, r2.k_count as k_count FROM nu_BGP_6096836102481082072 AS r1 LEFT OUTER JOIN delta_BGP_1320827854144898937 AS r2 ON 1 = 1 WHERE r2.k_count < 0;
