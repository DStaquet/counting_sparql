import numpy as np


def build_table(
    rows: int,
    k_counts: int,
    combo_count: int = 1,
    triples_bool: bool = False,
) -> tuple[list[tuple[str, int]], int]:
    """Builds up a table of rows and k counts

    Args:
        rows (int): Amount of rows in the table
        k_counts (int): Average k counts

    Returns:
        list[tuple[int, int]]: Generated tuples togeter with k counts
    """
    from random import shuffle

    s = np.random.poisson(k_counts, rows)

    return_list: list[tuple[str, int]] = []

    if triples_bool:
        combo_list, combo_count = build_all_combos(
            rows, combo_count, triples_bool
        )
        object_combinations = combo_list.copy()
        shuffle(object_combinations)
        for index in range(0, len(combo_list)):
            return_list.append(
                (
                    combo_list[index]
                    + f'", "http://example.org/edges/link", "'
                    + "".join(object_combinations[index]),
                    s[index],
                )
            )
    else:
        combo_list, combo_count = build_all_combos(rows)

        for i in range(len(combo_list)):
            return_list.append((combo_list[i], s[i]))

    return return_list, combo_count


def build_all_combos(
    rows: int,
    combo_count: int = 1,
    triples_bool: bool = False,
) -> tuple[list[str], int]:
    """Builds all possible combinations of a table

    Args:
        rows (int): Amount of rows in the table
        combo_count (int, optional): How much letters are
            already in the identifier. Defaults to 1.

    Returns:
        tuple[list[str], int]: Gives back the list with the
            combinations and last known amount of letters
            in the identifier
    """
    from itertools import product
    from string import ascii_uppercase as au
    from random import shuffle

    k: int = 0
    # combo_count: int = 1
    return_list: list[str] = []
    while k < rows:
        all_combinations = product(au, repeat=combo_count)
        all_combinations = [
            f"http://example.org/{''.join(combo)}"
            for combo in all_combinations
        ]
        for combo in all_combinations:
            return_list.append("".join(combo))
            k += 1
            if k == rows:
                break
        combo_count += 1

    return return_list, combo_count


def build_all_combos_twice(rows: int) -> list[str]:
    """Builds all possible cominbations of the table for 2N rows"""
    combo_list, _ = build_all_combos(rows * 2)

    return combo_list


def build_big_S_table(
    N: int,
    k_counts: int,
    combo_count: int = 1,
    c: int = 10,
) -> list[tuple[str, int]]:
    """Builds a big S table

    Args:
        rows (int): Amount of rows in the table
        k_counts (int): Average k counts
        combo_count (int, optional): Amount of letters in the identifier. Defaults to 1.

    Returns:
        list[tuple[str, int]]: List of tuples with the identifier and k counts
    """
    s = np.random.poisson(int(k_counts * (1 / 10)), N * 2)

    combo_list = build_all_combos_twice(N)
    return_list: list[tuple[str, int]] = []

    s_start: int = int(N - N / c)
    s_end: int = int(N + N * ((c - 1) / c))

    flip: int = -1
    for index in range(s_start, s_end):
        if s[index] == 0:
            s[index] = 1
        return_list.append(
            (combo_list[index], s[index] * flip)
        )
        flip *= -1

    return return_list


def build_del_table_arr(
    del_arr: list[int],
    N: int,
    k_counts: int,
    combo_count: int = 2,
    input_list: list[tuple[str, int]] | None = None,
) -> list[list[tuple[str, int]]]:
    """Builds a deletion table

    Args:
        del_arr (list[int]): Deletion rows
        N (int): Amount of rows in the table
        k_counts (int): Average k counts
        combo_count (int, optional): Amount of letters in the identifier. Defaults to 2.

    Raises:
        ValueError: Deletion rows must be less than the rows in the table.

    Returns:
        list[list[tuple[str, int]]]: List of list of deletion tables
    """
    from random import sample

    combo_list, _ = build_all_combos(N)

    del_arr = [
        (
            int(float(i))
            if int(float(i)) >= 1
            else int(float(i) * N)
        )
        for i in del_arr
    ]

    del_tables: list[list[tuple[str, int]]] = []

    if input_list != None:
        input_list_first = [i[0] for i in input_list]

    for del_rows in del_arr:
        if del_rows > N:
            raise ValueError(
                f"Deletion rows must be less than or equal to {N}"
            )

        s = np.random.poisson(
            int(k_counts * (1 / 10)), del_rows
        )

        if input_list == None:
            del_table_sample: list[str] = sample(
                combo_list, del_rows
            )
            del_table = [
                (del_table_sample[i], -s[i])
                for i in range(del_rows)
            ]

            del_tables.append(del_table)

        else:
            del_table_sample: list[str] = sample(
                input_list_first, del_rows
            )
            del_table = [
                (del_table_sample[i], -s[i])
                for i in range(del_rows)
            ]

            del_tables.append(del_table)

    return del_tables


def build_insert_table_arr(
    insert_arr: list[int],
    N: int,
    k_counts: int,
    combo_count: int = 2,
) -> list[list[tuple[str, int]]]:
    """Builds the insertion table

    Args:
        insert_arr (list[int]): Insertion rows
        N (int): Amount of rows in the original table
        k_counts (int): Average k counts
        combo_count (int, optional): Amount of letters in the identifier. Defaults to 2.

    Raises:
        ValueError: Insertion rows must be less than the rows in the table.

    Returns:
        list[list[tuple[str, int]]]: List of list of insertion tables
    """
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
        help="Number of rows in the table. Default is 3",
    )

    parser.add_argument(
        "-k",
        "--k_counts",
        type=int,
        default=25,
        help="Number of average k counts. Default is 25",
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        type=str,
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

    parser.add_argument(
        "-df",
        "--deletion_file",
        nargs="+",
        type=str,
        help="File to save the deletion to",
        dest="delete_file",
    )

    parser.add_argument(
        "-c",
        nargs="+",
        type=int,
        help="Overlapping modifier for big datasets",
        dest="c",
    )

    parser.add_argument(
        "-oS",
        "--output_big_S",
        nargs="+",
        type=str,
        help="Output file name for big S",
        dest="output_big_S",
    )
    parser.add_argument(
        "-t",
        "--triples",
        action="store_true",
        help="Make triples",
    )

    from save_to_file import (
        save_table_to_file,
        replace_string_in_file,
    )

    args = parser.parse_args()

    generated_k, combo_count = build_table(
        args.rows, args.k_counts, triples_bool=args.triples
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
        if args.triples:
            generated_d_arr: list[list[tuple[str, int]]] = (
                build_del_table_arr(
                    args.delete,
                    args.rows,
                    args.k_counts,
                    combo_count,
                    generated_k,
                )
            )
        else:
            generated_d_arr: list[list[tuple[str, int]]] = (
                build_del_table_arr(
                    args.delete,
                    args.rows,
                    args.k_counts,
                    combo_count,
                )
            )

    if args.c != None:
        for index in range(0, len(args.c)):
            generated_big_S = build_big_S_table(
                args.rows,
                args.k_counts,
                combo_count,
                args.c[index],
            )
            if args.output_big_S != None:
                if len(args.c) != len(args.output_big_S):
                    raise ValueError(
                        "Amount of big S and output files must be the same"
                    )
                save_table_to_file(
                    generated_big_S,
                    args.output_big_S[index],
                )

    if args.print:
        print(generated_k)
        if args.insert != None:
            print(generated_s_arr)
        if args.delete != None:
            print(generated_d_arr)
        if args.c != None:
            print(generated_big_S)

    if args.output != None and type(generated_k) == list:
        if args.triples:
            save_table_to_file(
                generated_k,
                args.output,
                ["s", "p", "o", "k_count"],
            )
            replace_string_in_file(args.output, '""', '"')
        else:
            save_table_to_file(
                generated_k,
                args.output,
            )

    if args.insert_file != None and args.insert != None:
        if len(args.insert) != len(args.insert_file):
            raise ValueError(
                "Amount of insertions and files must be the same"
            )
        for i in range(len(args.insert)):
            save_table_to_file(
                generated_s_arr[i], args.insert_file[i]
            )

    if args.delete_file != None and args.delete != None:
        if len(args.delete) != len(args.delete_file):
            raise ValueError(
                "Amount of deletions and files must be the same"
            )
        for i in range(len(args.delete)):
            if args.triples:
                save_table_to_file(
                    generated_d_arr[i],
                    args.delete_file[i],
                    ["s", "p", "o", "k_count"],
                )
                replace_string_in_file(
                    args.delete_file[i], '""', '"'
                )
            else:
                save_table_to_file(
                    generated_d_arr[i], args.delete_file[i]
                )
