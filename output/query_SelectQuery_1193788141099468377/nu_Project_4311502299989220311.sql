INSERT INTO nu_Project_4311502299989220311 (label, product, propertyTextual, k_count)
SELECT (CASE
            WHEN r1.label NOT NULL THEN r1.label
            ELSE r2.label
        END) AS label,
       (CASE
            WHEN r1.product NOT NULL THEN r1.product
            ELSE r2.product
        END) AS product,
       (CASE
            WHEN r1.propertyTextual NOT NULL THEN r1.propertyTextual
            ELSE r2.propertyTextual
        END) AS propertyTextual,
       coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) AS k_count
FROM Project_4311502299989220311 AS r1
FULL OUTER JOIN delta_Project_4311502299989220311 AS r2 ON r1.label = r2.label
AND r1.product = r2.product
AND r1.propertyTextual = r2.propertyTextual
WHERE (coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0)) > 0;