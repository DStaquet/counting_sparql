
echo 'Constructing 1000 products for the BSBM queries'
python3 example_constructor/bsbm_setup.py example_constructor/bsbm_data/input_data/new_dataset.ttl example_constructor/bsbm_data/input_data/test_1000.nt example_constructor/bsbm_data/output_data/1000_product




echo 'Running the benchmark for Query1 with 1000 products'
python3 main.py benchmarker/Queries/BSBM/Query1/query1.sparql temp_tests/chain_benchmark -d example_constructor/bsbm_data/output_data/1000_product/base.csv -dl example_constructor/bsbm_data/output_data/1000_product -nf example_constructor/bsbm_data/output_data/1000_product -m -r 5 -s    