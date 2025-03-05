import numpy as np
from matplotlib import pyplot as plt


def compare_times_plot(
    cmp_arr_one: np.ndarray,
    cmp_arr_two: np.ndarray,
    name_one: str,
    name_two: str,
    bins: list,
    save_name: str | None = None,
    cmp_arr_three: np.ndarray | None = None,
    name_three: str | None = None,
    cmp_arr_four: np.ndarray | None = None,
    name_four: str | None = None,
    log: bool = False,
    fontsize_curr: int = 14,
) -> None:
    """Builds up a plot to compare the times of the times given in the array.

    Args:
        cmp_arr (np.ndarray): Array with the times to compare.
    """
    plt.figure(figsize=(8, 5))
    index = np.arange(len(bins))
    bar_width = 0.4
    plt.bar(
        index,
        cmp_arr_one,
        width=bar_width,
        label=name_one,
    )
    plt.bar(
        index + bar_width,
        cmp_arr_two,
        width=bar_width,
        label=name_two,
    )
    """ if name_three is None and name_four is None:
        if save_name is not None:
            plt.title(f"{save_name}")
        else:
            plt.title(f"{name_one} vs {name_two}")
    elif name_three is not None and name_four is None:
        if save_name is not None:
            plt.title(
                f"{name_one} vs {name_two} vs {name_three} - {save_name}"
            )
        else:
            plt.title(f"{name_one} vs {name_two}")
    elif name_three is not None and name_four is not None:
        if save_name is not None:
            plt.title(
                f"{name_one} vs {name_two} vs {name_three} vs {name_four} - {save_name}"
            )
        else:
            plt.title(f"{name_one} vs {name_two}") """
    plt.xticks(
        index + bar_width,
        bins,
        fontsize=fontsize_curr,
    )
    if cmp_arr_three is not None:
        if name_three is None:
            raise ValueError(
                "Name three is None whilst cmp_arr_three is not."
            )
        plt.bar(
            index + bar_width * 2,
            cmp_arr_three,
            width=bar_width,
            label=name_three,
        )
    if cmp_arr_four is not None:
        if name_four is None:
            raise ValueError(
                "Name four is None whilst cmp_arr_four is not."
            )
        plt.bar(
            index + bar_width * 3,
            cmp_arr_four,
            width=bar_width,
            label=name_four,
        )
    if log:
        plt.yscale("log")
    plt.ylabel("Time (ms)", fontsize=fontsize_curr)
    plt.yticks(fontsize=fontsize_curr)
    plt.legend(fontsize=fontsize_curr)
    if name_three is not None and name_four is not None:
        plt.savefig(
            f"./plots/{name_one}_vs_{name_two}_vs_{name_three}_vs_{name_four}.png"
        )
    else:
        plt.savefig(f"./plots/{name_one}_vs_{name_two}.png")
    if save_name is not None:
        plt.savefig(
            f"./plots/{save_name}.png",
        )
    plt.clf()


def compare_plot_from_dict(
    inp_dict: dict[str, dict[str, float]],
    save_name: str | None = None,
) -> None:
    """Builds up a plot to compare the times of the times given in the dictionary.

    Args:
        inp_dict (dict[str, dict[str, float]]): Dictionary with the times to compare.
    """
    cmp_arr_one = []
    cmp_arr_two = []
    bins = []
    already_seen_keys = []
    for key in inp_dict:
        curr_key: str = key.split("_")[0]
        to_add_key = curr_key
        if curr_key in already_seen_keys:
            curr_key = (
                curr_key
                + "_"
                + str(already_seen_keys.count(curr_key))
            )
        print(f"Key: {key}, curr_key: {curr_key}")
        already_seen_keys.append(to_add_key)
        bins.append(curr_key)
        cmp_arr_one.append(inp_dict[key]["incremental"])
        cmp_arr_two.append(inp_dict[key]["scratch"])
    compare_times_plot(
        np.array(cmp_arr_one),
        np.array(cmp_arr_two),
        "Incremental",
        "Scratch",
        bins,
        save_name=save_name,
    )


if __name__ == "__main__":
    import argparse
    from csv import DictReader as reader

    parser = argparse.ArgumentParser(
        description="Compare two arrays of times."
    )
    parser.add_argument(
        "file",
        type=str,
        help="File with the times to compare.",
    )
    parser.add_argument(
        "-l",
        "--log",
        action="store_true",
        default=False,
        help="Use log scale on the y-axis.",
    )

    args = parser.parse_args()

    scratch_times = []
    increm_times = []
    compare_buckets = []
    with open(args.file, "r") as f:
        csv_reader = reader(f)
        for row in csv_reader:
            scratch_times.append(float(row["Scratch"]))
            increm_times.append(float(row["Incremental"]))
            compare_buckets.append("p=" + row["File"])

    compare_times_plot(
        np.array(increm_times),
        np.array(scratch_times),
        "Incremental",
        "Scratch",
        compare_buckets,
        save_name="Tri hop",
        log=args.log,
    )
