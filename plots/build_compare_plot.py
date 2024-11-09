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
) -> None:
    """Builds up a plot to compare the times of the times given in the array.

    Args:
        cmp_arr (np.ndarray): Array with the times to compare.
    """
    index = np.arange(len(bins))
    bar_width = 0.2
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
    if name_three is None and name_four is None:
        if save_name is not None:
            plt.title(
                f"{name_one} vs {name_two} - {save_name}"
            )
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
            plt.title(f"{name_one} vs {name_two}")
    plt.xticks(
        index + bar_width,
        bins,
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
    plt.xlabel("Data size")
    plt.ylabel("Time (ms)")
    plt.legend()
    if name_three is not None and name_four is not None:
        plt.savefig(
            f"./plots/{name_one}_vs_{name_two}_vs_{name_three}_vs_{name_four}.png"
        )
    else:
        plt.savefig(f"./plots/{name_one}_vs_{name_two}.png")
    if save_name is not None:
        plt.savefig(f"./plots/{save_name}.png")
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
