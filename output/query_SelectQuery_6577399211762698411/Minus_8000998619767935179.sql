INSERT INTO Minus_8000998619767935179
SELECT label,
       p1,
       p3,
       product,
       p1.k_count AS k_count
FROM Filter_7141111257548129695 AS p1
WHERE (p1.product) NOT IN
    (SELECT p2.product
     FROM BGP_3492496584436433866 AS p2) ON CONFLICT DO
  UPDATE
  SET k_count = EXCLUDED.k_count + k_count WHERE label = EXCLUDED.label
  AND p1 = EXCLUDED.p1
  AND p3 = EXCLUDED.p3
  AND product = EXCLUDED.product;