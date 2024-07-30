import kcount_tester
from eval_incremental import duckdb_conn

import os, sys


def test_build_data():
    hashseed = os.getenv("PYTHONHASHSEED")
    if not hashseed:
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(
            sys.executable, [sys.executable] + sys.argv
        )

    kcount_tester.build_data(
        "data/dataset100.ttl",
        "output",
        "Queries/berlin_benchmark/100/query3_benchmark/query3_99.sparql",
        duckdb_conn,
        "data/delete_product98.ttl",
        "data/insert_product105.ttl",
    )
    g_data = duckdb_conn.sql("SELECT * FROM G;").df()
    delta_g_data = duckdb_conn.sql(
        "SELECT * FROM delta_G where s = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer3/Product98';"
    ).df()
    assert not delta_g_data.empty
    delta_g_data = duckdb_conn.sql(
        "SELECT * FROM delta_G where s = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer3/Product105';"
    ).df()
    assert not delta_g_data.empty

    nu_g_data = duckdb_conn.sql(
        "SELECT * FROM nu_G WHERE s = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer3/Product98';"
    ).df()
    assert nu_g_data.empty
    nu_g_data = duckdb_conn.sql(
        "SELECT * FROM nu_G WHERE s = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer3/Product105';"
    ).df()
    assert not nu_g_data.empty
