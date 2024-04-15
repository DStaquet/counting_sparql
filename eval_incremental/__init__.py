import duckdb

duckdb_conn = duckdb.connect("./database/k_values.db")

VALUES: dict[str, bool] = {"INSERT_CHECK": False}
"""
Boolean to check if the values need to be inserted
"""
