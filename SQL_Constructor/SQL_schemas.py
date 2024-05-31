from rdflib.plugins.sparql.parserutils import CompValue
from SQL_Constructor.SQL_Constructor import get_table_name


def project_schema(
    part: CompValue, schemas: dict[str, list[list[str]]]
) -> dict[str, list[list[str]]]:
    """Returns the schema associated with the current project part of the query

    Args:
        schemas (dict[str, list[list[str]]]): All schemas of the query

    Returns:
        dict[str, list[list[str]]]: Current calculation of the schemas
    """
    part_name: str = get_table_name(part)
    schemas[part_name] = list()
    for var_list in schemas[get_table_name(part.p)]:
        new_var_list: list[str] = list()
        for var in var_list:
            if var in part.PV:
                new_var_list.append(var)
        schemas[part_name].append(new_var_list)

    return schemas


def leftjoin_schema(
    part: CompValue, schemas: dict[str, list[list[str]]]
) -> dict[str, list[list[str]]]:
    """Returns the schema associated with the current leftjoin part of the query

    Args:
        schemas (dict[str, list[list[str]]]): All schemas of the query

    Returns:
        dict[str, list[list[str]]]: Current calculation of the schemas
    """
    left_part_name: str = get_table_name(part.p1)
    part_name: str = get_table_name(part)
    schemas[part_name] = list()
    for var_list in schemas[left_part_name]:
        new_list: list[str] = var_list.copy()
        if (
            part.p1._vars.intersection(part.p2._vars)
            != set()
        ):
            for var in part.p1._vars.intersection(
                part.p2._vars
            ):
                new_list.append(var)
        schemas[part_name].append(new_list)

    return schemas


def minus_schema(
    part: CompValue, schemas: dict[str, list[list[str]]]
) -> dict[str, list[list[str]]]:
    """Returns the schema associated with the current minus part of the query

    Args:
        schemas (dict[str, list[list[str]]]): All schemas of the query

    Returns:
        dict[str, list[list[str]]]: Current calculation of the schemas
    """
    part_name: str = get_table_name(part)
    schemas[part_name] = list()
    left_table_name: str = get_table_name(part.p1)
    right_table_name: str = get_table_name(part.p2)
    for var_list in schemas[left_table_name]:
        for var_list2 in schemas[right_table_name]:
            new_var_list2: list[str] = list()
            for var in var_list2:
                if var in part.p1._vars.intersection(
                    part.p2._vars
                ):
                    new_var_list2.append(var)
            schemas[part_name].append(
                var_list + new_var_list2
            )

    return schemas


def union_schema(
    part: CompValue, schemas: dict[str, list[list[str]]]
) -> dict[str, list[list[str]]]:
    """Constructs the schema for the union part of the query

    Args:
        part (CompValue): Current part of the query
        schemas (dict[str, list[list[str]]]): Current schemas of the query

    Returns:
        dict[str, list[list[str]]]: Schema for the union part of the query added to schemas
    """
    left_table_name: str = get_table_name(part.p1)
    right_table_name: str = get_table_name(part.p2)
    part_name: str = get_table_name(part)
    schemas[part_name] = list()
    for var_list in schemas[left_table_name]:
        schemas[part_name].append(var_list)
    for var_list in schemas[right_table_name]:
        schemas[part_name].append(var_list)

    return schemas


def bgp_schema(
    part: CompValue, schemas: dict[str, list[list[str]]]
) -> dict[str, list[list[str]]]:
    """Constructs the schemas associated with the BGP part of the query

    Args:
        part (CompValue): Current part of the query
        schemas (dict[str, list[list[str]]]): All schemas

    Returns:
        dict[str, list[list[str]]]: Returns all schemas with the BGP schema added
    """
    table_name: str = get_table_name(part)
    schemas[table_name] = list()
    schemas[table_name].append(list())
    for var in set(part._vars):
        if var not in schemas[table_name]:
            schemas[table_name][0].append(
                var
            )  # Uses 0 as BGP will always have one schema

    return schemas


def filter_schema(
    part: CompValue, schemas: dict[str, list[list[str]]]
) -> dict[str, list[list[str]]]:
    """Constructs the schemas associated with the filter part of the query.

    Args:
        part (CompValue): Current part of the query.
        schemas (dict[str, list[list[str]]]): All schemas yet constructed.

    Returns:
        dict[str, list[list[str]]]: All schemas including the filter schema.
    """
    part_name: str = get_table_name(part)
    schemas[part_name] = list()
    for var_list in schemas[get_table_name(part.p)]:
        schemas[part_name].append(var_list)

    return schemas


def build_schemas(
    part: CompValue, schemas: dict[str, list[list[str]]]
) -> dict[str, list[list[str]]]:
    """Builds the entire schema.

    Args:
        part (CompValue): Current part of the query.
        schemas (dict[str, list[list[str]]]): All schemas yet constructed.

    Returns:
        dict[str, list[list[str]]]: All schemas.
    """
    if "p" in part:
        schemas = build_schemas(part.p, schemas)
    elif "p1" in part and "p2" in part:
        schemas = build_schemas(part.p1, schemas)
        schemas = build_schemas(part.p2, schemas)
    if part.name == "BGP":
        schemas = bgp_schema(part, schemas)
    elif part.name == "Filter":
        schemas = filter_schema(part, schemas)
    elif part.name == "Project":
        schemas = project_schema(part, schemas)
    elif part.name == "LeftJoin":
        schemas = leftjoin_schema(part, schemas)
    elif part.name == "Minus":
        schemas = minus_schema(part, schemas)
    elif part.name == "Union":
        schemas = union_schema(part, schemas)

    return schemas
