INSERT INTO delta_Filter_331046825976329928(label, product, value1, k_count)
SELECT label,
       product,
       value1,
       k_count
FROM delta_BGP_8188015215573083507
WHERE CAST(value1 AS INT) > CAST(332 AS INT);