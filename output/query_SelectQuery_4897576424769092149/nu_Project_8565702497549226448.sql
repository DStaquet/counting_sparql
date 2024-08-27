INSERT INTO nu_Project_8565702497549226448 (label, product, k_count)
SELECT (CASE
            WHEN r1.label NOT NULL THEN r1.label
            ELSE r2.label
        END) AS label,
       (CASE
            WHEN r1.product NOT NULL THEN r1.product
            ELSE r2.product
        END) AS product,
       coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) AS k_count
FROM Project_8565702497549226448 AS r1
FULL OUTER JOIN delta_Project_8565702497549226448 AS r2 ON r1.label = r2.label
AND r1.product = r2.product
WHERE (coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0)) > 0;