INSERT INTO Project_4311502299989220311(label, product, propertyTextual, k_count)
SELECT label, product, propertyTextual, SUM(k_count) AS k_count
FROM Union_6291923553636737850
GROUP BY label, product, propertyTextual;