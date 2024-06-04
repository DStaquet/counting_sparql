INSERT INTO delta_LeftJoin_7483953543868752126(comment, f, label, p, producer, productFeature, propertyNumeric1, propertyNumeric2, propertyTextual1, propertyTextual2, propertyTextual3, propertyTextual4, propertyTextual5, propertyNumeric4, k_count)
SELECT comment, f, label, p, producer, productFeature, propertyNumeric1, propertyNumeric2, propertyTextual1, propertyTextual2, propertyTextual3, propertyTextual4, propertyTextual5, propertyNumeric4, r1.k_count as k_count
FROM delta_LeftJoin_6275415322198649408 AS r1 LEFT OUTER JOIN BGP_405584237077899936 AS r2 ON TRUE;
INSERT INTO delta_LeftJoin_7483953543868752126
SELECT producer, propertyTextual3, propertyTextual5, p, propertyNumeric2, label, propertyTextual2, f, propertyTextual1, propertyTextual4, propertyNumeric1, productFeature, comment, propertyNumeric4, r2.k_count as k_count FROM nu_LeftJoin_6275415322198649408 AS r1 LEFT OUTER JOIN delta_BGP_405584237077899936 AS r2 ON 1 = 1 WHERE r2.k_count < 0;
