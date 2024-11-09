INSERT INTO Project_5981214650323562087(label, product, k_count)
SELECT label, product, SUM(k_count) AS k_count
FROM Minus_6349949983044087158
GROUP BY label, product;