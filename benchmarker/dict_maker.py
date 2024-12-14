from rdflib.plugins.sparql.parserutils import CompValue
from os.path import join

from SQL_Constructor.base_constructor import get_table_name
from build_data import (
    readQueryFile,
)


def __addToDict(
    curr_name: str,
    query: str,
    dictionary: dict[str, str],
) -> dict:
    """Adds the part to the dictionary.

    Args:
        part (CompValue): The part to add.
        dictionary (dict): The dictionary to add the part to.
    """
    dictionary[curr_name] = query
    return dictionary


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


def constructDictFromTree(
    part: CompValue, query_input_dir: str
) -> dict[str, str]:
    """Constructs a dictionary from the tree.

    Args:
        part (CompValue): The given tree.

    Returns:
        dict: The dictionary constructed from the tree.
    """
    current_name = get_table_name(part)
    current_file_name = (
        join(query_input_dir, current_name) + ".sql"
    )

    if part.name == "BGP":
        prev_dict: dict[str, str] = dict()
    if "p" in part:
        prev_dict = constructDictFromTree(
            part.p, query_input_dir
        )
    elif "p1" in part and "p2" in part:
        prev_dict1 = constructDictFromTree(
            part.p1, query_input_dir
        )
        prev_dict2 = constructDictFromTree(
            part.p2, query_input_dir
        )
        prev_dict = __combineTwoDicts(
            prev_dict1, prev_dict2
        )

    curr_dict = __addToDict(
        current_name,
        readQueryFile(current_file_name),
        prev_dict,
    )

    return curr_dict
