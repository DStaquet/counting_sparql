from rdflib.plugins.sparql.parserutils import CompValue
from os.path import join, exists

from SQL_Constructor.base_constructor import get_table_name
from build_data import (
    readQueryFile,
)


def __addToDictList(
    curr_name: str,
    query: str,
    dictionary: dict[str, list[str]],
) -> dict[str, list[str]]:
    """Adds the part to the dictionary.

    Args:
        part (CompValue): The part to add.
        dictionary (dict): The dictionary to add the part to.
    """
    if curr_name in dictionary:
        dictionary[curr_name].append(query)
    else:
        dictionary[curr_name] = [query]
    return dictionary


def __addToDict(
    curr_name: str,
    query: str,
    dictionary: dict[str, str],
) -> dict[str, str]:
    """Adds the part to the dictionary.

    Args:
        part (CompValue): The part to add.
        dictionary (dict): The dictionary to add the part to.
    """
    dictionary[curr_name] = query
    return dictionary


def __combinDeltaAndNuDicts(
    delta_dict: dict[str, list[str]],
    nu_dict: dict[str, list[str]],
) -> dict[str, list[str]]:
    """Combines the delta and nu dictionaries.

    Args:
        delta_dict (dict): The delta dictionary.
        nu_dict (dict): The nu dictionary.

    Returns:
        dict: The combined dictionary.
    """
    new_dict = delta_dict.copy()
    for key in nu_dict:
        if key in new_dict:
            new_dict[key].extend(nu_dict[key])
        else:
            new_dict[key] = nu_dict[key]
    return new_dict


def __combineTwoDicts(
    dict1: dict[str, str], dict2: dict[str, str]
) -> dict[str, str]:
    """Combines two dictionaries.

    Args:
        dict1 (dict): The first dictionary.
        dict2 (dict): The second dictionary.

    Returns:
        dict: The combined dictionary.
    """
    return dict1 | dict2


def __getJoinOrNormalFile(query_file_name: str) -> str:
    """Get the join or normal file name.

    Args:
        query_file_name (str): The query file name.

    Returns:
        str: The join or normal file name.
    """
    if exists(query_file_name + "_join.sql"):
        return query_file_name + "_join.sql"
    else:
        return query_file_name + ".sql"


def constructDictFromTree(
    part: CompValue,
    query_input_dir: str,
    increm: bool = False,
) -> dict[str, str] | dict[str, list[str]]:
    """Constructs a dictionary from the tree.

    Args:
        part (CompValue): The given tree.

    Returns:
        dict: The dictionary constructed from the tree.
    """
    current_name = get_table_name(part)
    if not increm:
        current_file_name = (
            join(query_input_dir, current_name) + ".sql"
        )
    else:
        current_delta_file_name = __getJoinOrNormalFile(
            join(query_input_dir, "delta_" + current_name)
        )
        current_nu_file_name = __getJoinOrNormalFile(
            join(query_input_dir, "nu_" + current_name)
        )

    if part.name == "BGP":
        prev_dict: dict[str, str] | dict[str, list[str]] = (
            dict()
        )
    if "p" in part:
        prev_dict = constructDictFromTree(
            part.p, query_input_dir, increm
        )
    elif "p1" in part and "p2" in part:
        prev_dict1 = constructDictFromTree(
            part.p1, query_input_dir, increm
        )
        prev_dict2 = constructDictFromTree(
            part.p2, query_input_dir, increm
        )
        if not increm:
            prev_dict = __combineTwoDicts(
                prev_dict1, prev_dict2  # type: ignore
            )
        else:
            prev_dict = __combinDeltaAndNuDicts(
                prev_dict1, prev_dict2  # type: ignore
            )

    if not increm:
        curr_dict = __addToDict(
            current_name,
            readQueryFile(current_file_name),
            prev_dict,  # type: ignore
        )
    else:
        curr_dict = __addToDictList(
            current_name,
            readQueryFile(current_delta_file_name),
            prev_dict,  # type: ignore
        )
        curr_dict = __addToDictList(
            current_name,
            readQueryFile(current_nu_file_name),
            curr_dict,  # type: ignore
        )

    return curr_dict
