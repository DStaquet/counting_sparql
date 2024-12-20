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
    ```bash
    $ ./benchmark.sh
    ```
- In case this does not work, the commands in the shell script can be run manually.

For the BSBM experiment
-----------------------
- Set up the data
    - This script uses the data generated using the Berlin SPARQL Benchmark (BSBM) dataset. The source code to generate the data can be downloaded from the following link: https://sourceforge.net/projects/bsbmtools/
    1) The data is generated using the following commands:
        ```bash
        $ ./generate -pc 1000 -ud -tc 1000 -fn chain_1000 -ufn chain_update_1000 -s ttl  
        ```
    2) Put these datasets in the `bsbm_data/input/` directory
    3) After this run the following command to build up the data and run the queries:
        ```bash
        $ ./benchmark_bsbm.sh
        ```
- In case this does not work, the commands in the shell script can be run manually.

Results can afterwards be found in the `measurements/` directory.