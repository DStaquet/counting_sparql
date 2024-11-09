INSERT INTO delta_Minus_8000998619767935179
SELECT p1.label,
       p1.p1,
       p1.p3,
       p1.product,
       p1.k_count AS k_count
FROM delta_Filter_7141111257548129695 AS p1
WHERE (p1.product) NOT IN
    (SELECT p2.product
     FROM BGP_3492496584436433866 AS p2) ON CONFLICT DO
  UPDATE
  SET k_count = EXCLUDED.k_count + k_count WHERE label = EXCLUDED.label
  AND p1 = EXCLUDED.p1
  AND p3 = EXCLUDED.p3
  AND product = EXCLUDED.product;


INSERT INTO delta_Minus_8000998619767935179
SELECT p1.label,
       p1.p1,
       p1.p3,
       p1.product,
       p1.k_count AS k_count
FROM nu_Filter_7141111257548129695 AS p1,
     delta_BGP_3492496584436433866 AS p2,
     BGP_3492496584436433866 AS p3
WHERE (p1.product = p2.product)
  AND p1.product = p3.product
  AND -p2.k_count = p3.k_count;


INSERT INTO delta_Minus_8000998619767935179
SELECT p1.label,
       p1.p1,
       p1.p3,
       p1.product, -p1.k_count
FROM nu_Filter_7141111257548129695 AS p1,
     delta_BGP_3492496584436433866 AS p2
WHERE (p1.product = p2.product)
  AND EXISTS
    (SELECT product
     FROM BGP_3492496584436433866 AS p3
     WHERE p2.k_count = p3.k_count);