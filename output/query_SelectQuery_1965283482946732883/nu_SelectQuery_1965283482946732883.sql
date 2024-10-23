INSERT INTO nu_prep_SelectQuery_1965283482946732883 (t1, t2, t3, t4, t5, x, y, k_count)
SELECT t1,
       t2,
       t3,
       t4,
       t5,
       x,
       y,
       k_count
FROM SelectQuery_1965283482946732883;

INSERT INTO nu_prep_SelectQuery_1965283482946732883 (t1, t2, t3, t4, t5, x, y, k_count)
SELECT t1,
       t2,
       t3,
       t4,
       t5,
       x,
       y,
       k_count
FROM delta_SelectQuery_1965283482946732883;

INSERT INTO nu_SelectQuery_1965283482946732883 (t1, t2, t3, t4, t5, x, y, k_count)
SELECT t1,
       t2,
       t3,
       t4,
       t5,
       x,
       y,
       SUM(k_count) AS k_count
FROM nu_prep_SelectQuery_1965283482946732883
GROUP BY t1,
         t2,
         t3,
         t4,
         t5,
         x,
         y
HAVING SUM(k_count) > 0;