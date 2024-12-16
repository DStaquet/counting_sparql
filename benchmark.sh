#!/usr/bin/env bash

# Tri_hop query

echo 'Running the benchmark for the tri hop query with 1000 nodes (n).'
# Run the benchmark for the tri_hop query with 1000 nodes 50 delta values
echo 'Running with n=1000, p=1000, k=50'
python3 main.py Queries/hops/tri_hop.sparql temp_tests -d data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_1000.csv -dl data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_delta_1000_50.csv -nf data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_nu_1000_50.csv -r 50 > benchmarker/data/tri_hop_1000_50.txt

# Run the benchmark for the tri_hop query with 100 nodes and 50 delta values
echo 'Running with n=1000, p=100, k=50'
python3 main.py Queries/hops/tri_hop.sparql temp_tests -d data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_100.csv -dl data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_delta_100_50.csv -nf data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_nu_100_50.csv -r 10 > benchmarker/data/tri_hop_100_50.txt

# Run the benchmark for the tri_hop query with 50 nodes and 50 delta values
echo 'Running with n=1000, p=50, k=50'
python3 main.py Queries/hops/tri_hop.sparql temp_tests -d data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_50.csv -dl data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_delta_50_50.csv -nf data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_nu_50_50.csv -r 10 > benchmarker/data/tri_hop_50_50.txt

# Run the benchmark for the tri_hop query with 32 nodes 50 delta values
echo 'Running with n=1000, p=32, k=50'
python3 main.py Queries/hops/tri_hop.sparql temp_tests -d data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_32.csv -dl data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_delta_32_50.csv -nf data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_nu_32_50.csv -r 10 > benchmarker/data/tri_hop_32_50.txt