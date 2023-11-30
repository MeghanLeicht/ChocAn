"""Functions for adding to, updating, or removing from the database."""
from typing import Any, Dict, Optional, cast
import pandas as pd
import pyarrow as pa
from .load_records import _load_all_records_from_file_
from ._write_records import _overwrite_records_to_file_
from ..schemas import TableInfo


def add_records_to_file(records: pd.DataFrame, table_info: TableInfo) -> None:
    """
    Add new records to an existing Parquet file based on the provided schema.

    Args-
        records (pd.DataFrame): New records to be added.
        table_info (TableInfo): Object containing schema and other table-related information.

    Raises-
        pyarrow.ArrowInvalid: Mismatch between the DataFrame and the schema.
        pyarrow.ArrowIOError: I/O error occurs (e.g., file permissions, file lock).
        ValueError: Added records result in duplicate entries in the index column.
        KeyError: Mismatch between schema & records.
        TypeError: Type mismatch between schema & records.
        ArithmeticError: Value exceeds a character or numeric limit set by table_info

    """
    # Load file into memory
    try:
        existing_records = _load_all_records_from_file_(table_info)
    except pa.ArrowInvalid as err_invalid:
        raise err_invalid
    except pa.ArrowIOError as err_io:
        raise err_io

    # Check for compatibility with the schema.
    table_info.check_dataframe(records)

    # Check that the addition will cause no duplicate indices
    if _any_duplicate_values(existing_records.iloc[:, 0], records.iloc[:, 0]):
        raise ValueError("Added entries cause duplicates in the first column.")

    # Add the new data and save
    records = pd.concat([existing_records, records])
    try:
        _overwrite_records_to_file_(records, table_info)
    except pa.ArrowIOError as err_io:
        raise err_io


def update_record(index: Any, table_info: TableInfo, **kwargs) -> pd.Series:
    """
    Update a specific record in a database file based on the provided index and changes.

    Args-
        index (Any): Index value of the record to update.
        table_info (TableInfo): Object with schema and table details.
        **kwargs: Key-value pairs representing the fields to update and their new values.

    Returns-
        pd.Series: Updated record.

    Raises-
        AssertionError: No key-value pairs provided for update.
        IndexError: Specified index not found in the database.
        KeyError: Mismatch between provided fields & schema.
        pyarrow.ArrowInvalid: Type mismatch with the schema after update.
        pyarrow.ArrowIOError: I/O error occurs.

    Examples-
        # Update the name of member 1234 to Martha
        updated_member = update_record(1234,MEMBER_INFO, name = "Martha")

        # Update service #12 to be Broken Leg
        updated_service = update_record(12, SERVICE_INFO, service_name = "Broken leg")

        # Update address info for provider 2023
        updated_provider = update_record(
            2023,
            PROVIDER_INFO,
            address_line_1 = "1600 Pennsylvania Avenue, NW",
            address_line_2 = "Unit 2",
            zipcode = 97212The
        )
    """
    assert len(kwargs) > 0, "Must provide at least one key/value pair to update"
    try:
        records = _load_all_records_from_file_(table_info)
    except pa.ArrowInvalid as err_invalid:
        raise err_invalid
    except pa.ArrowIOError as err_io:
        raise err_io

    records = _validate_and_update_fields(records, index, kwargs, table_info)

    try:
        _overwrite_records_to_file_(records, table_info)
    except pa.ArrowIOError as err_io:
        raise err_io

    return cast(pd.Series, _get_row_by_index(records, index))


def remove_record(index: Any, table_info: TableInfo) -> bool:
    """
    Remove a record from a database file based on the provided index.

    Args-
        index (Any): Index value of the record to be removed.
        table_info (TableInfo): Object with schema and table details.

    Returns-
        bool: True if the record is successfully removed, False if the index is not found.

    Raises-
        pyarrow.ArrowInvalid: Invalid file format.
        pyarrow.ArrowIOError: I/O error occurs.

    Examples-
        #Ex 1. Remove member 1234
        if remove_record(1234,MEMBER_SCHEMA):
            print("Member 1234 Removed")
        else:
            print("Member 1234 Not Found.")
    """
    try:
        records = _load_all_records_from_file_(table_info)
    except pa.ArrowInvalid as err_invalid:
        raise err_invalid
    except pa.ArrowIOError as err_io:
        raise err_io

    num_records_before = len(records)
    records = records[records[table_info.index_col()] != index]
    # If records are the same size after removing the index, index did not exist.
    if len(records) == num_records_before:
        return False

    try:
        _overwrite_records_to_file_(records, table_info)
    except pa.ArrowIOError as err_io:
        raise err_io
    return True


def _any_duplicate_values(col_a: pd.Series, col_b: pd.Series) -> bool:
    """Check if two series contain any duplicate values."""
    return col_a.isin(col_b).any()


def _get_row_by_index(records: pd.DataFrame, index: Any) -> Optional[pd.Series]:
    """
    Get a row by matching an index to the first column.

    Args-
        records (pd.DataFrame): Records to search for index
        index (Any): The index to search the first column for

    Returns-
        pd.Series: The matching row
        None: No matching row found.
    """
    rows = records.loc[records.iloc[:, 0] == index]
    if rows.empty:
        return None
    return rows.iloc[0]


def _validate_and_update_fields(
    records: pd.DataFrame,
    index: int,
    field_updates: Dict[str, Any],
    table_info: TableInfo,
) -> pd.DataFrame:
    """
    Validates and updates specified fields in a record of a DataFrame.

    This function iterates over each field to be updated, validates the value against
    the schema defined in 'table_info', and applies the update to the record at the
    specified index in the DataFrame.

    Args-
        records (pd.DataFrame): The DataFrame containing the records.
        index (int): The index of the record in the DataFrame to be updated.
        field_updates (Dict[str, Any]): A dictionary containing field names as keys and
                                        the corresponding new values as values.
        table_info (TableInfo): An object containing the schema information and other
                                details about the table.

    Returns-
        pd.DataFrame: The updated records.

    Raises-
        KeyError: If a field name in 'field_updates' does not exist in the table schema.
        TypeError: If the type of a value in 'field_updates' does not match the expected
                   type defined in the table schema.
        ArithmeticError: If a value in 'field_updates' falls outside the acceptable range
                         defined for that field in the table schema.
        IndexError: The index was not found.
    """
    row = _get_row_by_index(records, index)
    if row is None:
        raise IndexError("Index not found.")
    for field_name, updated_value in field_updates.items():
        _validate_and_update_field(row, field_name, updated_value, table_info)
    return records


def _validate_and_update_field(
    row: pd.Series,
    field_name: str,
    updated_value: Any,
    table_info: TableInfo,
) -> pd.Series:
    """
    Check that a field is valid, and then write it to its location in a dataframe.

    Args-
        row (pd.Series): Row containing the data to change.
        field_name (str): Field within row to change.
        updated_value (Any): Value to set.
        table_info (TableInfo): Validation information for the row.

    Raises-
        KeyError: Field is not in row.
        TypeError: Type of updated_value is incorrect.
        ArithmeticError: updated_value is out of numeric or character range.

    Returns-
        pd.Series: row with updated field.
    """
    try:
        table_info.check_field(updated_value, field_name)
    except KeyError as err_key:
        raise err_key
    except TypeError as err_type:
        raise err_type
    except ArithmeticError as err_out_of_range:
        raise err_out_of_range
    row[field_name] = updated_value
    return row
