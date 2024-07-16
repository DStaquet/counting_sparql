INSERT INTO BGP_3492496584436433866 (product, k_count)
SELECT G1.s AS product, (G1.k_count) AS k_count
 FROM G G1
 WHERE G1.p = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productFeature' AND G1.o = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature320';
