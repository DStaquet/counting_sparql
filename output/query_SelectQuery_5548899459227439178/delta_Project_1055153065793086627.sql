INSERT INTO delta_Project_1055153065793086627(label, product, k_count)
SELECT label,
       product,
       SUM(k_count) AS k_count
FROM delta_Filter_331046825976329928
GROUP BY label,
         product;