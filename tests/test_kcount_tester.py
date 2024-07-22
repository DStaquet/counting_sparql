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
        "data/delete_product98.ttl",
        "output",
        "Queries/berlin_benchmark/100/query3_benchmark/query3_99.sparql",
        duckdb_conn,
    )
    g_data = duckdb_conn.sql("SELECT * FROM G;").df()
    delta_g_data = duckdb_conn.sql(
        "SELECT * FROM delta_G;"
    ).df()
    nu_g_data = duckdb_conn.sql("SELECT * FROM nu_G;").df()

    assert g_data.shape[0] != None
