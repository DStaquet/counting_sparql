import numpy as np


def build_table(
    rows: int, k_counts: int
) -> list[tuple[str, int]]:
    """Builds up a table of rows and k counts

    Args:
        rows (int): Amount of rows in the table
        k_counts (int): Average k counts

    Returns:
        list[tuple[int, int]]: Generated tuples togeter with k counts
    """
    from string import ascii_uppercase as au
    from itertools import combinations

    s = np.random.poisson(k_counts, rows)

    return_list: list[tuple[str, int]] = []

    k: int = 0
    combo_count: int = 1
    while k < rows:
        all_combinations = combinations(au, combo_count)
        for combo in all_combinations:
            return_list.append(("".join(combo), s[k]))
            k += 1
            if k == rows:
                break
        combo_count += 1

    return return_list


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Build a table"
    )

    parser.add_argument(
        "-r",
        "--rows",
        type=int,
        default=3,
        help="Number of rows in the table",
    )

    parser.add_argument(
        "-k",
        "--k_counts",
        type=int,
        default=25,
        help="Number of average k counts",
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        type=str,
        default="output.csv",
        help="Output file name",
    )

    parser.add_argument(
        "-p",
        "--print",
        action="store_true",
        help="Print the output",
        dest="print",
    )

    from save_to_file import save_table_to_file

    args = parser.parse_args()

    generated_k: list[tuple[str, int]] = build_table(
        args.rows, args.k_counts
    )

    if args.print:
        print(generated_k)

    if args.output != None:
        save_table_to_file(generated_k, args.output)
