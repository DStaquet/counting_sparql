echo "Running script with 1000 products, 50 inputs per product, 10 products to delta, 10 samples per delta, 10 runs"
python3 ./aggregation_test.py benchmarker/Queries/BSBM/Query1/query1_agg.sparql temptemp_tests/aggregation benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/delta_agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/nu_agg.sql -n 1000 -m 50 -dc 10 -sas 10 -r 10

echo "\n\nRunning script with 1000 products, 100 inputs per product, 10 products to delta, 10 samples per delta, 10 runs"
python3 ./aggregation_test.py benchmarker/Queries/BSBM/Query1/query1_agg.sparql temptemp_tests/aggregation benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/delta_agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/nu_agg.sql -n 1000 -m 100 -dc 10 -sas 10 -r 10

echo "\n\nRunning script with 1000 products, 1000 inputs per product, 10 products to delta, 10 samples per delta, 10 runs"
python3 ./aggregation_test.py benchmarker/Queries/BSBM/Query1/query1_agg.sparql temptemp_tests/aggregation benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/delta_agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/nu_agg.sql -n 1000 -m 1000 -dc 10 -sas 10 -r 10

echo "\n\nRunning script with 5000 products, 50 inputs per product, 10 products to delta, 10 samples per delta, 10 runs"
python3 ./aggregation_test.py benchmarker/Queries/BSBM/Query1/query1_agg.sparql temptemp_tests/aggregation benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/delta_agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/nu_agg.sql -n 5000 -m 50 -dc 10 -sas 10 -r 10

echo "\n\nRunning script with 5000 products, 100 inputs per product, 10 products to delta, 10 samples per delta, 10 runs"
python3 ./aggregation_test.py benchmarker/Queries/BSBM/Query1/query1_agg.sparql temptemp_tests/aggregation benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/delta_agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/nu_agg.sql -n 5000 -m 100 -dc 10 -sas 10 -r 10

echo "\n\nRunning script with 5000 products, 1000 inputs per product, 10 products to delta, 10 samples per delta, 10 runs"
python3 ./aggregation_test.py benchmarker/Queries/BSBM/Query1/query1_agg.sparql temptemp_tests/aggregation benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/delta_agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/nu_agg.sql -n 5000 -m 1000 -dc 10 -sas 10 -r 10

echo "\n\nRunning script with 10000 products, 50 inputs per product, 10 products to delta, 10 samples per delta, 10 runs"
python3 ./aggregation_test.py benchmarker/Queries/BSBM/Query1/query1_agg.sparql temptemp_tests/aggregation benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/delta_agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/nu_agg.sql -n 10000 -m 50 -dc 10 -sas 10 -r 10

echo "\n\nRunning script with 10000 products, 100 inputs per product, 10 products to delta, 10 samples per delta, 10 runs"
python3 ./aggregation_test.py benchmarker/Queries/BSBM/Query1/query1_agg.sparql temptemp_tests/aggregation benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/delta_agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/nu_agg.sql -n 10000 -m 100 -dc 10 -sas 10 -r 10

echo "\n\nRunning script with 20000 products, 50 inputs per product, 10 products to delta, 10 samples per delta, 10 runs"
python3 ./aggregation_test.py benchmarker/Queries/BSBM/Query1/query1_agg.sparql temptemp_tests/aggregation benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/delta_agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/nu_agg.sql -n 20000 -m 50 -dc 10 -sas 10 -r 10

echo "\n\nRunning script with 20000 products, 100 inputs per product, 10 products to delta, 10 samples per delta, 10 runs"
python3 ./aggregation_test.py benchmarker/Queries/BSBM/Query1/query1_agg.sparql temptemp_tests/aggregation benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/delta_agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/nu_agg.sql -n 20000 -m 100 -dc 10 -sas 10 -r 10

echo "\n\nRunning script with 50000 products, 50 inputs per product, 10 products to delta, 10 samples per delta, 10 runs"
python3 ./aggregation_test.py benchmarker/Queries/BSBM/Query1/query1_agg.sparql temptemp_tests/aggregation benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/delta_agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/nu_agg.sql -n 50000 -m 50 -dc 10 -sas 10 -r 10

echo "\n\nRunning script with 50000 products, 100 inputs per product, 10 products to delta, 10 samples per delta, 10 runs"
python3 ./aggregation_test.py benchmarker/Queries/BSBM/Query1/query1_agg.sparql temptemp_tests/aggregation benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/delta_agg.sql benchmarker/Queries/BSBM/Query1/selfmade_files/new_agg/nu_agg.sql -n 50000 -m 100 -dc 10 -sas 10 -r 10