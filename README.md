Incremental view maintenance for SPARQL through the counting algorithm
===============================================================

Prerequisites
-------------
- Following python packages are required to run the code:
    - rdflib
    - DuckDB
    - pandas

For the Tri hop experiment
--------------------------
- The user can run the following command for the tri-hop queries experiment:
    ```
    $ ./benchmark.sh
    ```
- In case this does not work, the commands in said script can be run manually.

For the BSBM experiment
-----------------------
- Set up the data
    - This script uses the data generated using the Berlin SPARQL Benchmark (BSBM) dataset. The source code to generate the data can be downloaded from the following link: https://sourceforge.net/projects/bsbmtools/
    1) The data is generated using the following commands:
        ```bash
        $ ./generate -pc 1000 -ud -tc 1000 -fn chain_1000 -ufn chain_update_1000 -s ttl  
        ```
    2) Put these datasets in the `data/` directory
    3) After this run the following command to generate the queries and delta updates
    ```
    python build_parameters.py
    ```
    4) The user is now able to run the experiment

How to run the experiment
-------------------------
- Run the following command to run the experiment:
    `python incremental_query_parser.py <path_to_output_file>`

The relevant queries are contained in the Queries/berlin_benchmark/ directory. When running the script with the above command, the given queries will execute, firstly with their incremental view maintenance approach and afterwards with the naive approach. The results will be written to the given output file.