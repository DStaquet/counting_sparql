INSERT INTO delta_BGP_3492496584436433866 (product, k_count)
SELECT G1.s AS product,
       delta_G1.k_count
FROM delta_G G1
WHERE G1.p = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productFeature'
  AND G1.o = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature320';