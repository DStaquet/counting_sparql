from benchmarker.benchmark import run_benchmark
from benchmarker.mult_benchmark import run_chain_benchmark

from os.path import join


def findAllDeltas(
    delta_dir: str, format: str = "csv"
) -> list[tuple[str, str]] | list[str]:
    """Finds all delta files in the given directory.

    Args:
        delta_dir (str): The directory to search for delta files.

    Returns:
        list[str]: List of delta files.
    """
    if format == "csv":
        return sorted(
            [
                join(delta_dir, file)
                for file in os.listdir(delta_dir)
                if "delta" in file and format in file
            ],
            key=lambda x: x.split("delta_")[1].split(
                ".csv"
            )[0],
        )

    tup_list: list[tuple[str, str]] = list()
    ins_list: list[str] = list()
    del_list: list[str] = list()
    for file in os.listdir(delta_dir):
        if "insert" in file and format in file:
            ins_list.append(join(delta_dir, file))
        if "delete" in file and format in file:
            del_list.append(join(delta_dir, file))
    for ins in ins_list:
        for del_i in del_list:
            if (
                ins.split("insert_")[1]
                == del_i.split("delete_")[1]
            ):
                tup_list.append((ins, del_i))

    return sorted(
        tup_list,
        key=lambda x: x[0]
        .split("insert_")[1]
        .split(".csv")[0],
    )


def findAllNus(delta_dir: str, format="csv") -> list[str]:
    """Finds all nu files in the given directory.

    Args:
        delta_dir (str): The directory to search for nu files.

    Returns:
        list[str]: List of nu files.
    """
    return sorted(
        [
            join(delta_dir, file)
            for file in os.listdir(delta_dir)
            if "nu" in file and format in file
        ],
        key=lambda x: x.split("nu_")[1].split(".csv")[0],
    )


if __name__ == "__main__":
    import os, sys
    import argparse
    from duckdb import DuckDBPyConnection, connect

    from os.path import isdir, isfile

    from build_data import setup_query_files, build_data

    hashseed = os.getenv("PYTHONHASHSEED")
    if not hashseed:
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(
            sys.executable, [sys.executable] + sys.argv
        )

    # Argument parser
    parser = argparse.ArgumentParser(
        description="Module to run SPARQL queries for benchmark with incremental view maintenance on SQL queries.",
        prog="main.py",
        epilog="Query files first need to be set up with build_data.py, can also be passed through this module as flags.",
    )
    parser.add_argument(
        "query", help="The SPARQL query to run"
    )
    parser.add_argument(
        "query_files",
        help="The directory where the query files are stored/need to be stored",
    )
    parser.add_argument(
        "-d",
        "--data",
        help="The base graph data file to use",
        required=True,
    )
    parser.add_argument(
        "-dl",
        "--delta",
        help="The delta graph data file to use",
        required=True,
    )
    parser.add_argument(
        "-nf",
        "--nu_file",
        help="The nu file to use",
        required=True,
    )
    parser.add_argument(
        "-db",
        "--database",
        dest="db",
        help="The database to connect to",
        default=":memory:",
    )
    parser.add_argument(
        "-s",
        "--setup",
        action="store_true",
        default=False,
        help="Construct the SQL queries before running the benchmark",
    )
    parser.add_argument(
        "-r",
        "--runs",
        type=int,
        default=10,
        help="The number of runs to do",
    )
    parser.add_argument(
        "-m",
        "--multiple",
        action="store_true",
        default=False,
        help="Chain multiple deltas",
    )
    parser.add_argument(
        "-ocsv",
        "--output_csv",
        help="The output csv file",
        default="output.csv",
    )
    parser.add_argument(
        "-icsv",
        "--init_csv",
        help="Overwrite the given output csv file",
        action="store_true",
        default=False,
    )

    args = parser.parse_args()

    if args.setup:
        setup_query_files(args.query, args.query_files)

    # Connect to the database
    duckdb_conn = connect(args.db)

    """ # Build up the data
    build_data(
        args.query_files,
        args.query,
        duckdb_conn,
        args.data,
        delta_file=args.delta,
        nu_file=args.nu_file,
        csv=True,
    ) """

    if not args.multiple:
        if not isfile(args.delta) or not isfile(
            args.nu_file
        ):
            raise ValueError(
                "Delta and nu files should be files."
            )
        avg_scratch_time, avg_increm_time = run_benchmark(
            args.query,
            args.query_files,
            args.runs,
            duckdb_conn,
            args.db,
            args.data,
            args.nu_file,
            args.delta,
        )

    else:
        if not isdir(args.delta) or not isdir(args.nu_file):
            raise ValueError(
                "Delta and nu files should be directories."
            )
        delta_list = findAllDeltas(args.delta, format="csv")
        nu_list = findAllNus(args.nu_file, format="csv")
        print(delta_list, nu_list)
        if len(delta_list) != len(nu_list):
            raise ValueError(
                "Delta files and nu files don't match."
            )
        delta_and_nu_files = list(zip(delta_list, nu_list))

        avg_scratch_time, avg_increm_time = (
            run_chain_benchmark(
                args.query,
                args.query_files,
                args.runs,
                duckdb_conn,
                args.data,
                delta_and_nu_files,  # type: ignore
                format="csv",
            )
        )

    from os.path import dirname, exists, basename
    from os import makedirs

    if (
        not exists(dirname(args.output_csv))
        and dirname(args.output_csv) != ""
    ):
        makedirs(dirname(args.output_csv))

    if args.init_csv:
        with open(args.output_csv, "w") as f:
            f.write("File,Scratch,Incremental\n")
    with open(args.output_csv, "a") as f:
        if not args.multiple:
            curr_run_name = (
                basename(args.data)
                .split("_")[-1]
                .split(".")[0]
            )
        else:
            curr_run_name = (
                dirname(args.data)
                .split("/")[-1]
                .split("_")[0]
            )
        f.write(
            f"{basename(args.data).split('_')[-1].split('.')[0]},{avg_scratch_time},{avg_increm_time}\n"
        )
