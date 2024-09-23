INSERT INTO nu_prep_Project_8708420436429866325 (x, z, k_count)
SELECT x,
       z,
       k_count
FROM Project_8708420436429866325;

INSERT INTO nu_prep_Project_8708420436429866325 (x, z, k_count)
SELECT x,
       z,
       k_count
FROM delta_Project_8708420436429866325;

INSERT INTO nu_Project_8708420436429866325 (x, z, k_count)
SELECT x,
       z,
       SUM(k_count) AS k_count
FROM nu_prep_Project_8708420436429866325
GROUP BY x,
         z;

DELETE
FROM nu_Project_8708420436429866325
WHERE k_count <= 0;