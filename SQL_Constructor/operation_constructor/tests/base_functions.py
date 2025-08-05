"""Modules to import"""

import os
import sys

from rdflib.plugins.sparql.parserutils import CompValue


def reset_seed():
    """Resets the hashing seed to have deterministic results."""

    hashseed = os.getenv("PYTHONHASHSEED")
    if not hashseed:
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(
            sys.executable, [sys.executable] + sys.argv
        )


def all_type_leaves(
    part: CompValue, type_name: str
) -> list[CompValue]:
    """Gives a list of all BGP patterns in the query.

    Args:
        part (Compvalue): Current algebraic expression

    Returns:
        list[CompValue]: All BGP patterns in the query.
    """
    if (
        part.p == None
        and part.p1 == None
        and part.p2 == None
        and part.name == type_name
    ):
        return_list: list[CompValue] = [part]
    else:
        if part.name == type_name:
            return_list = [part]
        else:
            return_list = []
    if "p" in part:
        return return_list + all_type_leaves(
            part.p, type_name
        )
    elif "p1" in part and "p2" in part:
        return (
            return_list
            + all_type_leaves(part.p1, type_name)
            + all_type_leaves(part.p2, type_name)
        )
    else:
        return return_list
