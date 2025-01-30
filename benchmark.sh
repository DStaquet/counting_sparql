#!/usr/bin/env bash

# Tri_hop query

echo "Installing pip requirements."
python3 -m pip install -r requirements.txt

# Generate the exemplary data for the tri_hop query with 1000 nodes and 1000^2/1000 edges
echo 'Constructing 1000 nodes/group and 1000^2/1000 edges graph for the tri_hop query.'
python3 example_constructor/graph_constructor.py -m 1000 -t hop -fr 1000 -b 4 -k 50 -nc data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_nu_1000_50.csv -csv data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_1000.csv -dc data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_delta_1000_50.csv
echo 'Constructing 1000 nodes/group and 1000^2/100 edges graph for the tri_hop query.'
python3 example_constructor/graph_constructor.py -m 1000 -t hop -fr 100 -b 4 -k 50 -nc data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_nu_100_50.csv -csv data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_100.csv -dc data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_delta_100_50.csv
echo 'Constructing 1000 nodes/group and 1000^2/50 edges graph for the tri_hop query.'
python3 example_constructor/graph_constructor.py -m 1000 -t hop -fr 50 -b 4 -k 50 -nc data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_nu_50_50.csv -csv data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_50.csv -dc data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_delta_50_50.csv
echo 'Constructing 1000 nodes/group and 1000^2/35 edges graph for the tri_hop query.'
python3 example_constructor/graph_constructor.py -m 1000 -t hop -fr 35 -b 4 -k 50 -nc data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_nu_35_50.csv -csv data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_35.csv -dc data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_delta_35_50.csv
echo 'Constructing 1000 nodes/group and 1000^2/30 edges graph for the tri_hop query.'
python3 example_constructor/graph_constructor.py -m 1000 -t hop -fr 30 -b 4 -k 50 -nc data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_nu_30_50.csv -csv data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_30.csv -dc data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_delta_30_50.csv
echo 'Constructing 1000 nodes/group and 1000^2/25 edges graph for the tri_hop query.'
python3 example_constructor/graph_constructor.py -m 1000 -t hop -fr 25 -b 4 -k 50 -nc data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_nu_25_50.csv -csv data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_25.csv -dc data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_delta_25_50.csv

echo 'Running the benchmark for the tri hop query with 1000 nodes (n).'
# Run the benchmark for the tri_hop query with 1000 nodes 50 delta values
echo 'Running with n=1000, p=1000, k=50'
python3 main.py Queries/hops/tri_hop.sparql temp_tests -d data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_1000.csv -dl data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_delta_1000_50.csv -nf data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_nu_1000_50.csv -icsv -ocsv measurements/output.csv -s -r 50 > measurements/tri_hop_1000_50.txt

# Run the benchmark for the tri_hop query with 100 nodes and 50 delta values
echo 'Running with n=1000, p=100, k=50'
python3 main.py Queries/hops/tri_hop.sparql temp_tests -d data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_100.csv -dl data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_delta_100_50.csv -nf data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_nu_100_50.csv -ocsv measurements/output.csv -r 5 > measurements/tri_hop_100_50.txt

# Run the benchmark for the tri_hop query with 50 nodes and 50 delta values
echo 'Running with n=1000, p=50, k=50'
python3 main.py Queries/hops/tri_hop.sparql temp_tests -d data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_50.csv -dl data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_delta_50_50.csv -nf data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_nu_50_50.csv -ocsv measurements/output.csv -r 5 > measurements/tri_hop_50_50.txt

# Run the benchmark for the tri_hop query with 32 nodes 50 delta values
echo 'Running with n=1000, p=35, k=50'
python3 main.py Queries/hops/tri_hop.sparql temp_tests -d data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_35.csv -dl data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_delta_35_50.csv -nf data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_nu_35_50.csv -ocsv measurements/output.csv -r 5 > measurements/tri_hop_35_50.txt

echo 'Running with n=1000, p=30, k=50'
python3 main.py Queries/hops/tri_hop.sparql temp_tests -d data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_30.csv -dl data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_delta_30_50.csv -nf data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_nu_30_50.csv -ocsv measurements/output.csv -r 5 > measurements/tri_hop_30_50.txt

echo 'Running with n=1000, p=25, k=50'
python3 main.py Queries/hops/tri_hop.sparql temp_tests -d data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_25.csv -dl data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_delta_25_50.csv -nf data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_nu_25_50.csv -ocsv measurements/output.csv -r 3 > measurements/tri_hop_25_50.txt