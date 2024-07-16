INSERT INTO delta_BGP_3492496584436433866
SELECT delta_G1.s AS product, delta_G1.k_count 
 FROM delta_G delta_G1
 WHERE delta_G1.p = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productFeature' AND delta_G1.o = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature320';
