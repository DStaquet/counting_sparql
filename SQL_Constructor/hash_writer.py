from SQL_Constructor.operation_constructor.join_constructor import (
    join_schemas,
)
from SQL_Constructor.operation_constructor.leftjoin_constructor import (
    leftjoin_schemas,
)
from SQL_Constructor.operation_constructor.project_constructor import (
    project_schemas,
)

from rdflib.plugins.sparql.parserutils import CompValue


from os.path import join

from SQL_Constructor.operation_constructor.union_constructor import (
    union_schemas,
)
from SQL_Constructor.table_constructor import (
    __encode_table_name,
)

import json


def serialize_to_json(part: CompValue | list[set]) -> str:
    """Serialize to JSON

    Args:
        part (CompValue): Part to serialize

    Returns:
        str: Serialized part
    """

    def set_default(obj):
        if isinstance(obj, set):
            return list(obj)
        return obj

    return json.dumps(
        part,
        default=set_default,
        indent=4,
    )


def write_hash_schemas(
    part: CompValue,
    output_dir: str,
    schemas1: list[set],
    schemas2: list[set] | None = None,
) -> list[set]:
    """Generates data in the hash_value.json for the schemas.

    Args:
        part (CompValue): Current part of the query
        output_dir (str): Directory to write the hash_values.json file
        schemas (list[set]): List of already calculated schemas
            lower in the parse tree

    Returns:
        list[set]: The schema list to return
    """
    match part.name:
        case "Filter":
            with open(
                join(output_dir, "hash_values.json"), "a"
            ) as hash_file:
                hash_file.write(
                    '"schema_'
                    + __encode_table_name(part)
                    + '": '
                )
                hash_file.write(serialize_to_json(schemas1))
                hash_file.write(",\n")
                return schemas1
        case "Project":
            with open(
                join(output_dir, "hash_values.json"), "a"
            ) as hash_file:
                project_schema = project_schemas(
                    part, schemas1
                )
                hash_file.write(
                    '"schema_'
                    + __encode_table_name(part)
                    + '": '
                )
                hash_file.write(
                    serialize_to_json(project_schema)
                )
                hash_file.write(",\n")
                return schemas1
        case "LeftJoin":
            with open(
                join(output_dir, "hash_values.json"), "a"
            ) as hash_file:
                if schemas2 is None:
                    raise ValueError(
                        "Schemas2 cannot be None for a left join"
                    )
                leftjoin_schema = leftjoin_schemas(
                    schemas1, schemas2
                )
                hash_file.write(
                    '"schema_'
                    + __encode_table_name(part)
                    + '": '
                )
                hash_file.write(
                    serialize_to_json(leftjoin_schema)
                )
                hash_file.write(",\n")
                return leftjoin_schema
        case "Join":
            with open(
                join(output_dir, "hash_values.json"), "a"
            ) as hash_file:
                if schemas2 is None:
                    raise ValueError(
                        "Schemas2 cannot be None for a join"
                    )
                join_schema = join_schemas(
                    schemas1, schemas2
                )
                hash_file.write(
                    '"schema_'
                    + __encode_table_name(part)
                    + '": '
                )
                hash_file.write(
                    serialize_to_json(join_schema)
                )
                hash_file.write(",\n")
                return join_schema
        case "Minus":
            with open(
                join(output_dir, "hash_values.json"), "a"
            ) as hash_file:
                hash_file.write(
                    '"schema_'
                    + __encode_table_name(part)
                    + '": '
                )
                hash_file.write(serialize_to_json(schemas1))
                hash_file.write(",\n")
                return schemas1
        case "Union":
            with open(
                join(output_dir, "hash_values.json"), "a"
            ) as hash_file:
                if schemas2 is None:
                    raise ValueError(
                        "Schemas2 cannot be None for a union"
                    )
                union_schema = union_schemas(
                    schemas1, schemas2
                )
                hash_file.write(
                    '"schema_'
                    + __encode_table_name(part)
                    + '": '
                )
                hash_file.write(
                    serialize_to_json(union_schema)
                )
                hash_file.write(",\n")
                return union_schema
        case "SelectQuery":
            with open(
                join(output_dir, "hash_values.json"), "a"
            ) as hash_file:
                hash_file.write(
                    '"schema_'
                    + __encode_table_name(part)
                    + '": '
                )
                hash_file.write(serialize_to_json(schemas1))
                hash_file.write(",\n")
                return schemas1

    raise NotImplementedError(
        "Part name not supported for writing hash schemas"
    )


def setup_hash_values(
    part: CompValue, output_dir: str
) -> list[set]:
    """Constructs a hash value info file for the query.

    Args:
        part (CompValue): Part of the query
    """
    hash_value: str = __encode_table_name(part)
    with open(
        join(output_dir, "hash_values.json"), "a"
    ) as hash_file:
        json_part: str = serialize_to_json(part)
        hash_file.write(
            '"' + hash_value + '": ' + json_part
        )
        hash_file.write("\n")
        if any(key in part for key in ["p", "p1", "p2"]):
            hash_file.write(",\n")

        # Add schemas to the hash file
        if part.name == "BGP":
            schema_name = __encode_table_name(part)
            hash_file.write(
                ',\n"schema_' + schema_name + '": '
            )
            hash_file.write(serialize_to_json(part._vars))
            hash_file.write("\n")
            hash_file.write(",\n")

            return [part._vars]

    if "p" in part:
        schemas1 = setup_hash_values(part.p, output_dir)
        schemas2 = None
    elif "p1" in part and "p2" in part:
        schemas1 = setup_hash_values(part.p1, output_dir)
        hash_file = open(
            join(output_dir, "hash_values.json"), "a"
        )
        hash_file.write(",\n")
        hash_file.close()
        schemas2 = setup_hash_values(part.p2, output_dir)

    # BGP cannot have come to this part of the function
    return write_hash_schemas(
        part, output_dir, schemas1, schemas2
    )
