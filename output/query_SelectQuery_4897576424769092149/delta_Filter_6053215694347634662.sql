INSERT INTO delta_Filter_6053215694347634662(label, product, value1, k_count)
SELECT label,
       product,
       value1,
       k_count
FROM delta_BGP_1397345390056075867
WHERE CAST(value1 AS INT) > CAST(162 AS INT);