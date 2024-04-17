Incremental view maintenance in counting algorithm through SPARQL
===============================================================

Prerequisites
-------------
- Following python packages are required to run the code:
    - rdflib
    - DuckDB
    - pandas

- Set up the data
    - This script uses the data generated using the Berlin SPARQL Benchmark (BSBM) dataset. The source code to generate the data can be downloaded from the following link: https://sourceforge.net/projects/bsbmtools/
    1) The data is generated using the following commands:
        ```bash
        $ ./generate -pc 100 -s ttl -fn dataset100
        $ ./generate -pc 1000 -s ttl -fn dataset1000
        $ ./generate -pc 5000 -s ttl -fn dataset5000
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