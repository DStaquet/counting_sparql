import csv
from matplotlib import pyplot as plt


def build_up_plots(
    query_name: str,
    results_incr: dict[tuple[str, str], dict[str, float]],
    results_non_incr: dict[
        tuple[str, str], dict[str, float]
    ],
) -> None:
    """Builds up the plots for the given query.

    Args:
        query_name (str): query_name
        results_incr (dict): contains measurements
        results_non_incr (dict): contains measurements
    """
    for data_size in ["100", "1000", "5000"]:
        x_incr = []
        x_non_incr = []
        for delta_size in ["small", "medium", "large"]:
            x_incr.append(
                results_incr[(data_size, delta_size)][
                    query_name
                ]
            )
            x_non_incr.append(
                results_non_incr[(data_size, delta_size)][
                    query_name
                ]
            )
        plt.plot(x_incr, label="Incremental")
        plt.plot(x_non_incr, label="Non-incremental")
        plt.title(f"{query_name} - {data_size}")
        plt.xlabel("Delta size")
        plt.xticks([0, 1, 2], ["small", "medium", "large"])
        plt.ylabel("Time (s)")
        plt.legend()
        plt.savefig(f"./plots/{query_name}_{data_size}.png")
        plt.clf()


if __name__ == "__main__":
    # Dict with the results
    results_incr: dict[
        tuple[str, str], dict[str, float]
    ] = dict()
    results_non_incr: dict[
        tuple[str, str], dict[str, float]
    ] = dict()

    # Read the data
    with open("./measurements/results.csv", "r") as f:
        csvreader = csv.DictReader(f, delimiter=",")
        for line in csvreader:
            data_tuple = (
                line["Data size"],
                line["Delta size"],
            )
            if data_tuple not in results_incr:
                results_incr[data_tuple] = dict()
            if data_tuple not in results_non_incr:
                results_non_incr[data_tuple] = dict()
            # Queries
            for query in [
                "Query1",
                "Query2",
                "Query3",
                "Query4",
            ]:
                if line["Incremental"] == "True":
                    # Incremental results
                    if (
                        query
                        not in results_incr[data_tuple]
                    ):
                        results_incr[data_tuple][query] = (
                            float(line[query])
                        )
                    else:
                        results_incr[data_tuple][query] = (
                            float(line[query])
                            + results_incr[data_tuple][
                                query
                            ]
                        ) / 2

                else:
                    # Non-incremental results
                    if (
                        query
                        not in results_non_incr[data_tuple]
                    ):
                        results_non_incr[data_tuple][
                            query
                        ] = float(line[query])
                    else:
                        results_non_incr[data_tuple][
                            query
                        ] = (
                            float(line[query])
                            + results_non_incr[data_tuple][
                                query
                            ]
                        ) / 2

    for query in ["Query1", "Query2", "Query3", "Query4"]:
        build_up_plots(
            query, results_incr, results_non_incr
        )
