"""
Manager Sub-System.

The manager sub-system allows managers to manage member, provider, and provider directory records.
"""
from typing import Dict, Optional, Any, List, cast
from datetime import datetime, date
import pandas as pd
import pyarrow as pa
from pandas.api.types import is_numeric_dtype
from .database_management import (
    load_records_from_file,
    load_record,
    add_record_to_file,
    update_record,
    remove_record,
    update_record,
)
from .schemas import USER_INFO, MEMBER_INFO, PROVIDER_DIRECTORY_INFO, TableInfo
from .user_io import prompt_str, prompt_int, PColor, prompt_menu_options, prompt_date
from .report import (
    generate_member_report,
    generate_summary_report,
    generate_provider_report,
)


def manager_menu() -> None:
    """
    The Manager menu provides access to the following key functionalities.

    Add Member
    Update Member
    Remove Member
    Add Provider
    Update Provider
    Remove Provider
    Add Provider Directory
    Update Provider Directory
    Remove Provider Directory
    Generate Member Report
    Generate Provider Report
    Generate Summary Report
    """
    message = "Manger Terminal"
    choices = ["Member", "Provider", "Provider Directory", "Reports"]

    while True:
        match prompt_menu_options(message, choices):
            case (_, "Member"):
                _prompt_add_remove_update(MEMBER_INFO, "Member")
            case (_, "Provider"):
                _prompt_add_remove_update(USER_INFO, "Provider")
            case (_, "Provider Directory"):
                _prompt_add_remove_update(PROVIDER_DIRECTORY_INFO, "Provider Directory")
            case (_, "Reports"):
                _prompt_report_options()
            case None:
                return


def _prompt_add_remove_update(table_info: TableInfo, name) -> None:
    message = f"Edit {name} Records"
    choices = ["Add", "Update", "Remove"]
    while True:
        match prompt_menu_options(message, choices):
            case (_, "Add"):
                _prompt_add_to_table_info(table_info)
            case (_, "Update"):
                _prompt_update_table_info(table_info)
            case (_, "Remove"):
                _prompt_remove_from_table_info(table_info)
            case None:
                return


def _prompt_report_options() -> None:
    """
    Display report options menu to the manager.

    The report options menu provides access to the following key functionalities.
    Generate Member Report
    Generate Provider Report
    Generate Summary Report
    """
    message = "Reports Options"
    choices = ["Member", "Provider", "Summary"]

    while True:
        match prompt_menu_options(message, choices):
            case (_, "Member"):
                generate_member_report()
            case (_, "Provider"):
                generate_provider_report()
            case (_, "Summary"):
                generate_summary_report()
            case None:
                return


def _prompt_field(table_info: TableInfo, field_name: str) -> Optional[str | int | date]:
    """
    Prompt the user for a field from a table_info object.

    Args-
        table_info (TableInfo): Object to get type information from
        field_name (str): Name of field to prompt for

    Returns-
        the input, as a date, str, or int depending on the type from table_info

    Raises-
        ValueError: Field not found in table_info
    """
    field = next((field for field in table_info.schema.fields if field.name == field_name), None)
    if field is None:
        raise ValueError(f"Field {field_name} not found in schema {table_info.name}")
    char_limit = table_info.character_limits.get(field_name, None)
    num_limit = table_info.numeric_limits.get(field_name, None)
    match field.type:
        case pa.int64():
            response = prompt_int(field.name, char_limit, num_limit)
        case pa.date32():
            response = prompt_date(field.name, max_date=datetime.now().date())
        case _:
            response = prompt_str(field.name, char_limit)
    return response


def _prompt_table_info(
    table_info: TableInfo, blacklist: Optional[List[str]]
) -> Optional[Dict[str, Any]]:
    """
    Prompt the user for the fields in a table_info object.

    Args-
        table_info: Object to get field names, types & limits from.
        blacklist: Optional list of fields to omit from the prompt.

    Returns-
        A dictionary of name/response pairs, or none if the user exits.
    """
    result = {}
    blacklist = blacklist or []
    blacklist.append(table_info.index_col())
    for field in table_info.schema.fields:
        if field.name in blacklist:
            continue
        response = _prompt_field(table_info, field.name)
        if response is None:
            return None
        result[field.name] = response
    return result


def _prompt_update_table_info(table_info: TableInfo, blacklist: Optional[List[str]] = None):
    """
    Prompt the user to update one field in a database

    Args-
        table_info (TableInfo): Info for the database being updated
        blacklist (Optional[List[str]]): Optional list of fields not to include as options
    """
    blacklist = blacklist or []
    blacklist.append(table_info.index_col())
    index_to_update = _prompt_field(table_info, table_info.index_col())
    if index_to_update is None:
        return
    index_to_update = cast(int, index_to_update)
    try:
        row_to_update = load_record(index_to_update, table_info)
    except pa.ArrowIOError as err_io:
        PColor.pfail(f"Unable to access records in {table_info.name}\n{err_io}")
        return
    except IndexError:
        PColor.pfail(f"Index {index_to_update} not found in {table_info.name}")
        return

    menu_options = [
        f"{name}: {val}" for name, val in row_to_update.items() if name not in blacklist
    ]
    selection = prompt_menu_options("Select field to update", menu_options)
    if selection is None:
        return
    selected_field = row_to_update.iloc[selection[0]]
    new_value = _prompt_field(table_info, selected_field)
    if new_value is None:
        return
    try:
        update_record(index_to_update, table_info, **{selected_field: new_value})
    except pa.ArrowIOError as err_io:
        PColor.pfail(f"Unable to access records in {table_info.name}\n{err_io}")
    else:
        PColor.pok("Records Updated.")


def _prompt_add_to_table_info(table_info: TableInfo, blacklist: Optional[List[str]] = None):
    """
    Prompt the user to add a record to a database

    Args-
        table_info (TableInfo): Info for the database being added to
        blacklist (Optional[List[str]]): Optional list of fields not to prompt for
    """
    blacklist = blacklist or []
    blacklist.append(table_info.index_col())
    try:
        new_id = generate_unique_id(table_info)
    except IndexError:
        PColor.pfail(f"Database {table_info.name} is full.")
        return
    except pa.ArrowIOError as err_io:
        PColor.pfail(f"Unable to access {table_info.name}\n{err_io}")
        return

    new_row = _prompt_table_info(table_info, blacklist)
    if new_row is None:
        return

    new_row[table_info.index_col()] = new_id

    try:
        add_record_to_file(new_row, table_info)
    except pa.ArrowIOError as err_io:
        PColor.pfail(f"Unable to access records in {table_info.name}\n{err_io}")
    else:
        PColor.pok("Record Added.")


def _prompt_remove_from_table_info(table_info: TableInfo):
    """
    Prompt the user to remove one row from a database

    Args-
        table_info (TableInfo): Info for the database being updated
    """
    index_to_update = _prompt_field(table_info, table_info.index_col())
    if index_to_update is None:
        return
    index_to_update = cast(int, index_to_update)
    try:
        if remove_record(index_to_update, table_info):
            PColor.pok("Record removed.")
        else:
            PColor.pfail("Record not found.")
    except pa.ArrowIOError as err_io:
        PColor.pfail(f"Unable to remove record from {table_info.name}\n{err_io}")


def generate_unique_id(table_info: TableInfo) -> int:
    """
    Generate a unique 9 digit ID. ID's increment by 1.

    Returns-
        int: The generated ID.

    Raises-
        IndexError: ID limit exceeded.
    """
    df = None
    try:
        df = load_records_from_file(table_info)
    except pa.ArrowIoError as err_io:
        raise err_io

    if df.empty:
        return 1000000000

    existing_ids = df.iloc[:, 0]
    if not is_numeric_dtype(existing_ids):
        raise TypeError("Only integers are allowed.")

    max_id = id.max()
    if max_id >= 9999999999:
        raise IndexError("User Limit Exceeded.")
    return max_id + 1
