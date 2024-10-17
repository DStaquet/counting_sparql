import numpy as np
from matplotlib import pyplot as plt


def compare_times_plot(
    cmp_arr_one: np.ndarray,
    cmp_arr_two: np.ndarray,
    name_one: str,
    name_two: str,
    bins: list,
    save_name: str | None = None,
) -> None:
    """Builds up a plot to compare the times of the times given in the array.

    Args:
        cmp_arr (np.ndarray): Array with the times to compare.
    """
    index = np.arange(len(bins))
    bar_width = 0.35
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
    if save_name is not None:
        plt.title(f"{name_one} vs {name_two} - {save_name}")
    else:
        plt.title(f"{name_one} vs {name_two}")
    plt.xticks(
        index + bar_width,
        bins,
    )
    plt.yscale("log")
    plt.xlabel("Data size")
    plt.ylabel("Time (ms)")
    plt.legend()
    if save_name is not None:
        plt.savefig(f"./plots/{save_name}.png")
    plt.savefig(f"./plots/{name_one}_vs_{name_two}.png")
    plt.clf()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Compare two arrays of times."
    )
    parser.add_argument(
        "file",
        type=str,
        help="File with the times to compare.",
    )

    args = parser.parse_args()
