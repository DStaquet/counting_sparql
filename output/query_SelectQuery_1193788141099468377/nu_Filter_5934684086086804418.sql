INSERT INTO nu_Filter_5934684086086804418 (label, p2, product, propertyTextual, k_count)
SELECT (CASE
            WHEN r1.label NOT NULL THEN r1.label
            ELSE r2.label
        END) AS label,
       (CASE
            WHEN r1.p2 NOT NULL THEN r1.p2
            ELSE r2.p2
        END) AS p2,
       (CASE
            WHEN r1.product NOT NULL THEN r1.product
            ELSE r2.product
        END) AS product,
       (CASE
            WHEN r1.propertyTextual NOT NULL THEN r1.propertyTextual
            ELSE r2.propertyTextual
        END) AS propertyTextual,
       coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) AS k_count
FROM Filter_5934684086086804418 AS r1
FULL OUTER JOIN delta_Filter_5934684086086804418 AS r2 ON r1.label = r2.label
AND r1.p2 = r2.p2
AND r1.product = r2.product
AND r1.propertyTextual = r2.propertyTextual
WHERE (coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0)) > 0;