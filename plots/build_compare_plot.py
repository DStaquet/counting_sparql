import numpy as np
from matplotlib import pyplot as plt


def compare_times_plot(
    cmp_arr_one: np.ndarray,
    cmp_arr_two: np.ndarray,
    name_one: str,
    name_two: str,
    bins: list,
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
    plt.title(f"{name_one} vs {name_two}")
    plt.xticks(
        index + bar_width,
        bins,
    )
    plt.xlabel("Data size")
    plt.ylabel("Time (s)")
    plt.legend()
    plt.savefig(f"./plots/{name_one}_vs_{name_two}.png")
    plt.clf()
