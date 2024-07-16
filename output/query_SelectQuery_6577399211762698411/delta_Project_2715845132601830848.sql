INSERT INTO delta_Project_2715845132601830848(label, product, k_count)
SELECT label, product, SUM(k_count) AS k_count
FROM delta_Minus_8000998619767935179
GROUP BY label, product;