if __name__ == "__main__":
    import argparse
    from experiments import duckdb_conn
    from incremental_query_parser import readQueryFile
    from experiments.delta_bgp_join import (
        join_delta_rules_bgp,
    )

    """duckdb_conn = duckdb.connect(
        "./database/experiments_delta_bgp.db"
    )"""

    # Argument parser
    parser = argparse.ArgumentParser(
        description="build up the delta rules utilizing a join."
    )
    parser.add_argument(
        "query_str",
        type=str,
        help="the query file.",
    )
    parser.add_argument(
        "query_dir",
        type=str,
        help="the directory where the SQL queries are stored.",
    )
    args = parser.parse_args()

    read_query: str = readQueryFile(args.query_str)
    join_delta_rules_bgp(read_query)
