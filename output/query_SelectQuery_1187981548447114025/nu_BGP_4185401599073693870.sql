INSERT INTO nu_BGP_4185401599073693870 (label, product, value1, k_count)
SELECT (CASE
            WHEN r1.label NOT NULL THEN r1.label
            ELSE r2.label
        END) AS label,
       (CASE
            WHEN r1.product NOT NULL THEN r1.product
            ELSE r2.product
        END) AS product,
       (CASE
            WHEN r1.value1 NOT NULL THEN r1.value1
            ELSE r2.value1
        END) AS value1,
       coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) AS k_count
FROM BGP_4185401599073693870 AS r1
FULL OUTER JOIN delta_BGP_4185401599073693870 AS r2 ON r1.label = r2.label
AND r1.product = r2.product
AND r1.value1 = r2.value1
WHERE (coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0)) > 0;