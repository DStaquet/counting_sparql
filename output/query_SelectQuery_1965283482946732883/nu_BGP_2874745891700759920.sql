INSERT INTO nu_prep_BGP_2874745891700759920 (t1, t2, t3, t4, t5, x, y, k_count)
SELECT t1,
       t2,
       t3,
       t4,
       t5,
       x,
       y,
       k_count
FROM BGP_2874745891700759920;

INSERT INTO nu_prep_BGP_2874745891700759920 (t1, t2, t3, t4, t5, x, y, k_count)
SELECT t1,
       t2,
       t3,
       t4,
       t5,
       x,
       y,
       k_count
FROM delta_BGP_2874745891700759920;

INSERT INTO nu_BGP_2874745891700759920 (t1, t2, t3, t4, t5, x, y, k_count)
SELECT t1,
       t2,
       t3,
       t4,
       t5,
       x,
       y,
       SUM(k_count) AS k_count
FROM nu_prep_BGP_2874745891700759920
GROUP BY t1,
         t2,
         t3,
         t4,
         t5,
         x,
         y
HAVING SUM(k_count) > 0;