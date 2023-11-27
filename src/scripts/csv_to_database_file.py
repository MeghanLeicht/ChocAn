"""
A developer-side utility for adding CSV records to a table object.

example usage:
# Add example services to the provider directory.
cd src/scripts
python3 csv_to_database_file.py example_provider_directory.csv provider_directory

"""


import pandas as pd
import sys
from choc_an_simulator.database_management import add_records_to_file
from choc_an_simulator.schemas import (
    TableInfo,
    PROVIDER_DIRECTORY_INFO,
    MEMBER_INFO,
    USER_INFO,
    SERVICE_LOG_INFO,
)


def match_name_to_table_info(name: str) -> TableInfo:
    """
    Match a name to a table_info object.

    Args-
        name (str): Name to match. Matches the "name" field of a TableInfo object.
    Returns-
        TableInfo: The matching object
    Raises-
        ValueError: No match found
    """
    for table_info in [
        PROVIDER_DIRECTORY_INFO,
        MEMBER_INFO,
        USER_INFO,
        SERVICE_LOG_INFO,
    ]:
        if name == table_info.name:
            return table_info
    raise ValueError(f"Name {name} does not match any table_info object.")


def add_csv_to_database(csv_path: str, table_name: str) -> None:
    """
    Add a csv file to a table.

    Args-
        csv_path (str): Path to csv file
        table_name (str): Name of table to add to. Matches the "name" field of a TableInfo object.
    """
    table_info = match_name_to_table_info(table_name)
    records = pd.read_csv(csv_path)
    add_records_to_file(records, table_info)


def main():
    """Add csv rows to a table, based on command line arguments."""
    args = sys.argv
    if len(args) != 3:
        print(
            "Arguments not recognized. Correct usage: "
            f"\n\tpython3 {args[0]} csv_path table_name"
        )
    add_csv_to_database(args[1], args[2])
    print(f"CSV records successfully added to {args[2]}", file=sys.stderr)


if __name__ == "__main__":
    main()
