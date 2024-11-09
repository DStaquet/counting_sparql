INSERT INTO nu_Minus_8000998619767935179 (label, p1, p3, product, k_count)
SELECT (CASE
            WHEN r1.label NOT NULL THEN r1.label
            ELSE r2.label
        END) AS label,
       (CASE
            WHEN r1.p1 NOT NULL THEN r1.p1
            ELSE r2.p1
        END) AS p1,
       (CASE
            WHEN r1.p3 NOT NULL THEN r1.p3
            ELSE r2.p3
        END) AS p3,
       (CASE
            WHEN r1.product NOT NULL THEN r1.product
            ELSE r2.product
        END) AS product,
       coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) AS k_count
FROM Minus_8000998619767935179 AS r1
FULL OUTER JOIN delta_Minus_8000998619767935179 AS r2 ON r1.label = r2.label
AND r1.p1 = r2.p1
AND r1.p3 = r2.p3
AND r1.product = r2.product
WHERE (coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0)) > 0;