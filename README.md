Incremental view maintenance for SPARQL through the counting algorithm
===============================================================

Prerequisites
-------------
- The requirements needed are written in the `requirements.txt` file. To install the requirements, the user can run one of the following commands:
    ```bash
    $ pip install -r requirements.txt
    ```
    or
    ```bash
    $ python3 -m pip install -r requirements.txt
    ```
- Note: This is also done in the `benchmark.sh` and `benchmark_bsbm.sh` scripts, so it is not required to run this yourself.

If desired, create a virtual environment to install the requirements.

For the Tri hop experiment
--------------------------
- The user can run the following command for the tri-hop queries experiment:
    ```bash
    $ ./benchmark.sh
    ```
- In case this does not work, the commands in the shell script can be run manually.

Note: Make sure you are allowed to run the shell script. If not, run the following command:
    ```
    $ chmod +x benchmark.sh
    ```

For the BSBM experiment
-----------------------
- Set up the data
    - This script uses the data generated using the Berlin SPARQL Benchmark (BSBM) dataset. The source code to generate the data can be downloaded from the following link: https://sourceforge.net/projects/bsbmtools/
    1) The data is generated using the following commands:
        ```bash
        $ ./generate -pc 1000 -ud -tc 1000 -fn chain_1000 -ufn chain_update_1000 -s ttl  
        ```
    2) Put the two datasets `chain_1000.ttl` and `chain_update_1000.nt` in the `bsbm_data/input_data/` directory
    3) After this run the following command to build up the data and run the queries:
        ```bash
        $ ./benchmark_bsbm.sh
        ```
- In case this does not work, the commands in the shell script can be run manually.

Note: Make sure you are allowed to run the shell script. If not, run the following command:
    ```
    $ chmod +x benchmark.sh
    ```

Results can afterwards be found in the `measurements/` directory.