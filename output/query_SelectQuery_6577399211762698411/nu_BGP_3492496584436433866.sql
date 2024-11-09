INSERT INTO nu_BGP_3492496584436433866 (product, k_count)
SELECT (CASE
            WHEN r1.product NOT NULL THEN r1.product
            ELSE r2.product
        END) AS product,
       coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) AS k_count
FROM BGP_3492496584436433866 AS r1
FULL OUTER JOIN delta_BGP_3492496584436433866 AS r2 ON r1.product = r2.product
WHERE (coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0)) > 0;