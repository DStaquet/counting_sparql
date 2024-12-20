Berlin SPARQL Benchmark (BSBM) data
====================================

Data generated through the SPARQL benchmark should be put here in a directory named `input`. The data can be generated using the Berlin SPARQL Benchmark (BSBM) dataset. The source code to generate the data can be downloaded from the following link: https://sourceforge.net/projects/bsbmtools/

To generate a 1000 product chain, the following commands can be used:
    ```
    $ ./generate -pc 1000 -ud -tc 1000 -fn chain_1000 -ufn chain_update_1000 -s ttl
    ```
Afterwards, the generated data should be put in the `bsbm_data/input/` directory.