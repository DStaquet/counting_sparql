INSERT INTO Filter_7141111257548129695(label, p1, p3, product, k_count)
SELECT label,
       p1,
       p3,
       product,
       k_count
FROM BGP_4245425749932949804
WHERE CAST(p1 AS INT) > CAST(88 AS INT)
  AND CAST(p3 AS INT) < CAST(448 AS INT);