INSERT INTO delta_Filter_4062382548913049243(label, p1, product, propertyTextual, k_count)
SELECT label,
       p1,
       product,
       propertyTextual,
       k_count
FROM delta_BGP_2732790592149769836
WHERE CAST(p1 AS INT) > CAST(122 AS INT);