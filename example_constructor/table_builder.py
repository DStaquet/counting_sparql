import numpy as np


def build_table(
    rows: int, k_counts: int, combo_count: int = 1
) -> tuple[list[tuple[str, int]], int]:
    """Builds up a table of rows and k counts

    Args:
        rows (int): Amount of rows in the table
        k_counts (int): Average k counts

    Returns:
        list[tuple[int, int]]: Generated tuples togeter with k counts
    """
    from string import ascii_uppercase as au
    from itertools import product

    s = np.random.poisson(k_counts, rows)

    return_list: list[tuple[str, int]] = []

    combo_list, combo_count = build_all_combos(rows)

    for i in range(len(combo_list)):
        return_list.append((combo_list[i], s[i]))

    """k: int = 0
    # combo_count: int = 1
    while k < rows:
        all_combinations = product(au, repeat=combo_count)
        for combo in all_combinations:
            return_list.append(("".join(combo), s[k]))
            k += 1
            if k == rows:
                break
        combo_count += 1"""

    return return_list, combo_count


def build_all_combos(
    rows: int, combo_count: int = 1
) -> tuple[list[str], int]:
    from itertools import product
    from string import ascii_uppercase as au

    k: int = 0
    # combo_count: int = 1
    return_list: list[str] = []
    while k < rows:
        all_combinations = product(au, repeat=combo_count)
        for combo in all_combinations:
            return_list.append("".join(combo))
            k += 1
            if k == rows:
                break
        combo_count += 1

    return return_list, combo_count


def build_all_combos_twice(rows: int) -> list[str]:
    from itertools import product
    from string import ascii_uppercase as au

    combo_list, combo_count = build_all_combos(rows * 2)

    return combo_list


def build_del_table_arr(
    del_arr: list[int],
    N: int,
    k_counts: int,
    combo_count: int = 2,
) -> list[list[tuple[str, int]]]:
    combo_list = build_all_combos_twice(N)

    del_arr = [
        (
            int(float(i))
            if int(float(i)) >= 1
            else int(float(i) * N)
        )
        for i in del_arr
    ]

    del_tables: list[list[tuple[str, int]]] = []

    for del_rows in del_arr:
        if del_rows > N:
            raise ValueError(
                f"Deletion rows must be less than or equal to {N}"
            )

        del_table = build_table(
            del_rows, int(k_counts * (1 / 10)), combo_count
        )[0]
        del_table = [(i[0], i[1] + 1) for i in del_table]

        del_tables.append(del_table)

    return del_tables


def build_insert_table_arr(
    insert_arr: list[int],
    N: int,
    k_counts: int,
    combo_count: int = 2,
) -> list[list[tuple[str, int]]]:
    insert_arr = [
        (
            int(float(i))
            if int(float(i)) >= 1
            else int(float(i) * N)
        )
        for i in insert_arr
    ]

    insert_tables: list[list[tuple[str, int]]] = []

    for ins_rows in insert_arr:
        if ins_rows > N:
            raise ValueError(
                f"Insertion rows must be less than or equal to {N}"
            )

        insert_table = build_table(
            ins_rows, int(k_counts * (1 / 10)), combo_count
        )[0]
        insert_table = [
            (i[0], i[1] + 1) for i in insert_table
        ]

        insert_tables.append(insert_table)

    return insert_tables


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

    parser.add_argument(
        "-i",
        "--insertion",
        nargs="+",
        type=str,
        help="Make a small insertion for the table with the amount of insertions",
        dest="insert",
    )

    parser.add_argument(
        "-d",
        "--deletion",
        nargs="+",
        type=str,
        help="Make a small deletion for the table with the amount of deletions",
        dest="delete",
    )

    parser.add_argument(
        "-if",
        "--insertion_file",
        nargs="+",
        type=str,
        help="File to save the insertion to",
        dest="insert_file",
    )

    from save_to_file import save_table_to_file

    args = parser.parse_args()

    generated_k, combo_count = build_table(
        args.rows, args.k_counts
    )

    if args.insert != None:
        generated_s_arr: list[list[tuple[str, int]]] = (
            build_insert_table_arr(
                args.insert,
                args.rows,
                args.k_counts,
                combo_count,
            )
        )

    if args.delete != None:
        generated_d_arr: list[list[tuple[str, int]]] = (
            build_del_table_arr(
                args.delete,
                args.rows,
                args.k_counts,
                combo_count,
            )
        )

    if args.print:
        print(generated_k)
        if args.insert != None:
            print(generated_s_arr)

    if args.output != None and type(generated_k) == list:
        save_table_to_file(generated_k, args.output)

    if args.insert_file != None and args.insert != None:
        if len(args.insert) != len(args.insert_file):
            raise ValueError(
                "Amount of insertions and files must be the same"
            )
        for i in range(len(args.insert)):
            save_table_to_file(
                generated_s_arr[i], args.insert_file[i]
            )
