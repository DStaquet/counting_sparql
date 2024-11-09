INSERT INTO Filter_5934684086086804418(label, p2, product, propertyTextual, k_count)
SELECT label,
       p2,
       product,
       propertyTextual,
       k_count
FROM BGP_2020790532000715027
WHERE CAST(p2 AS INT) > CAST(293 AS INT);