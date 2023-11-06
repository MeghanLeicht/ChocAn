"""Functions related to database Input/Output."""
import os
from typing import Optional, Dict, Any
from importlib.resources import files
import pandas as pd
import pyarrow as pa
from .schemas import TableInfo

# The directory where all parquet files are stored
_PARQUET_DIR_ = str(files("choc_an_simulator") / "storage")


def add_records_to_file(records: pd.DataFrame, table_info: TableInfo) -> None:
    """
    Add records to a parquet file.

    Args-
        records: The records to add to the file
        table_info: Information for the table being added to

    Raises-
        ValueError: Added entries cause duplicate entries in the first column
        pyarrow.ArrowInvalid: Mismatch between the dataframe and the schema.
        pyarrow.ArrowIOError: I/O-related error (e.g. permissions, file lock, etc.)
        KeyError: Mismatch between schema & records, or schema & file.

    """
    # Load file into memory
    try:
        existing_records = _load_all_records_from_file_(table_info)
    except pa.ArrowInvalid as err_invalid:
        raise err_invalid
    except pa.ArrowIOError as err_io:
        raise err_io

    # Check for compatibility with the schema
    try:
        table_info.check_dataframe(records)
    except KeyError as err_mismatch:
        raise err_mismatch
    except TypeError as err_type:
        raise err_type
    except ArithmeticError as err_limit:
        raise err_limit
    # Check that the addition will cause no duplicate indices
    if (
        existing_records[table_info.index_col()]
        .isin(records[table_info.index_col()])
        .any()
    ):
        raise ValueError("Added entries cause duplicates in the first column.")

    # Add the new data and save
    records = pd.concat([existing_records, records])
    try:
        _overwrite_records_to_file_(records, table_info)
    except pa.ArrowInvalid as err_invalid:
        raise err_invalid
    except pa.ArrowIOError as err_io:
        raise err_io


def load_records_from_file(
    table_info: TableInfo,
    eq_cols: Optional[Dict[str, Any]] = None,
    lt_cols: Optional[Dict[str, Any]] = None,
    gt_cols: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Load and filter records from a file.

    Args-
        table_info: Information for the table being loaded from
        eq_cols: column name / value pairs that the returned records must be equal to.
        lt_cols: column name / value pairs that the returned records must be less than.
        gt_cols: column name / value pairs that the returned records must be greater than.

    Returns-
        All matching records. If the file doesn't exist, returns an empty dataframe.

    Raises-
        KeyError: Mismatch between schema & records.
        pyarrow.ArrowTypeError: Type mismatch between schema & added records.
        pyarrow.ArrowInvalid: Mismatch between the dataframe and the schema.
        pyarrow.ArrowIOError: I/O-related error (e.g. permissions, file lock, etc.)
        TypeError: Unsupported type comparison with filter

    Examples-
        # Get all records, no filters:
        records = load_records_from_file(example_table_info)

        # Get all logs from the last month:
        records = load_records_from_file(
            table_info = example_table_info,
            gt_cols = {"date": datetime.now() - timedelta(days=31)}
        )

        # Get all records with ID = 1234
        records = load_records_from_file(
            table_info = example_table_info,
            eq_cols = {"ID" : 1234}
        )
    """
    try:
        records = _load_all_records_from_file_(table_info)
    except pa.ArrowInvalid as err_invalid:
        raise err_invalid
    except pa.ArrowIOError as err_io:
        raise err_io
    except KeyError as err_key:
        raise err_key

    if eq_cols is not None:
        for col, val in eq_cols.items():
            if col not in table_info.schema.names:
                raise KeyError("eq_cols name {col} not found in schema.")
            try:
                records = records[records[col] == val]
            except TypeError as err_type:
                raise TypeError(f"{err_type}: {col} == {val} not supported.")
    if lt_cols is not None:
        for col, val in lt_cols.items():
            if col not in table_info.schema.names:
                raise KeyError(f"lt_cols name {col} not found in schema.")
            try:
                records = records[records[col] < val]
            except TypeError as err_type:
                raise TypeError(f"{err_type}: {col} < {val} not supported.")
    if gt_cols is not None:
        for col, val in gt_cols.items():
            if col not in table_info.schema.names:
                raise KeyError(f"gt_cols name {col} not found in schema.")
            try:
                records = records[records[col] > val]
            except TypeError as err_type:
                raise TypeError(
                    f"{err_type}: {col} > records = records[records[col] > val]{val} not supported."
                )

    return records


def update_record(index: Any, table_info: TableInfo, **kwargs) -> pd.Series:
    """
    Update a single record in a database file.

    Args-
        index: Value to match in the first column of the database
        table_info: Information for the table to update
        **kwargs: Key/value pairs to change

    Returns-
        The matching row with updated values

    Raises-
        AssertionError: No key/value pairs given
        IndexError: Index not found
        KeyError: Mismatch between dataframe & schema, or kwargs & schema
        pyarrow.ArrowInvalid: Type mismatch between the updated table and the schema.
        pyarrow.ArrowIOError: I/O-related error (e.g. permissions, file lock, etc.)

    Examples-
        # Update the name of member 1234 to Martha
        updated_member = update_record("members",1234,member_schema, name = "Martha")

        # Update service #12 to be Broken Leg
        updated_service = update_record("services",12,service_schema, service_name = "Broken leg")

        # Update address info for provider 2023
        updated_provider = update_record(
            "providers",
            2023,
            provider_schema,
            address_line_1 = "1600 Pennsylvania Avenue, NW",
            address_line_2 = "Unit 2",
            zipcode = 97212
        )
    """
    assert len(kwargs) > 0, "Must provide at least one key/value pair to update"
    try:
        records = _load_all_records_from_file_(table_info)
    except pa.ArrowInvalid as err_invalid:
        raise err_invalid
    except pa.ArrowIOError as err_io:
        raise err_io
    except KeyError as err_key:
        raise err_key

    try:
        index = records[records[table_info.index_col()] == index].index.values[0]
    except IndexError:
        raise IndexError(f"Index {index} not found in {table_info.name}")

    for key, value in kwargs.items():
        if key not in table_info.schema.names:
            raise KeyError(f"Column {key} not found in {table_info.name}")
        records.loc[index, key] = value

    try:
        _overwrite_records_to_file_(records, table_info)
    except pa.ArrowInvalid as err_type:
        raise err_type
    except pa.ArrowIOError as err_io:
        raise err_io

    return records.loc[index]


def remove_record(index: Any, table_info: TableInfo) -> bool:
    """
    Remove a single record from a database file.

    Args-
        index: Value to match in the first column of the database. Row wit this index is removed.
        table_info: Information for the table to remove from

    Returns-
        True: Row with matching index was removed
        False: Index was not found.

    Raises-
        KeyError: Mismatch between dataframe and schema
        pyarrow.ArrowInvalid: Invalid file format
        pyarrow.ArrowIOError: I/O-related error (e.g. permissions, file lock, etc.)

    Examples-
        # Remove member 1234

        if remove_record("members",1234,member_schema):
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
    except KeyError as err_key:
        raise err_key

    if index not in records[table_info.index_col()]:
        return False
    records = records[records[table_info.index_col()] != index]

    try:
        _overwrite_records_to_file_(records, table_info)
    except pa.ArrowIOError as err_io:
        raise err_io
    return True


def _load_all_records_from_file_(table_info: TableInfo) -> pd.DataFrame:
    """
    Load an entire parquet file into a dataframe.

    If no file is found, returns an empty dataframe with the given schema.

    Args-
        table_info: Information for the table to load from
    Returns-
        All records in the file, or none if no file found.
    Raises-
        pyarrow.ArrowInvalid: File format is invalid
        pyarrow.ArrowIOError: I/O-related error (e.g. permissions, file lock, etc.)
        KeyError: File columns do not match schema
    """
    path = _convert_name_to_path_(table_info.name)
    try:
        records = pd.read_parquet(path)
    except FileNotFoundError:
        return pa.Table.from_pylist([], schema=table_info.schema).to_pandas()
    except (pa.ArrowInvalid, pa.ArrowIOError) as err_arrow:
        raise err_arrow

    try:
        table_info.check_dataframe(records)
    except KeyError as err_mismatch:
        raise err_mismatch
    return records


def _overwrite_records_to_file_(records: pd.DataFrame, table_info: TableInfo) -> None:
    """
    Overwrite a parquet file with new records.

    Args-
        records: The records to write to file.
        table_info: Information for the table to overwrite
    Raises-
        KeyError: Records & schema have mismatched columns
        TypeError: Records have incorrect types
        ArithmeticError: Records contain values outside of the table_info's limits
        pyarrow.ArrowInvalid: Type mismatch between dataframe and schema.
        pyarrow.ArrowIOError: I/O-related error (e.g. permissions, file lock, etc.).

    """
    try:
        table_info.check_dataframe(records)
    except KeyError as err_mismatch:
        raise err_mismatch
    except TypeError as err_type:
        raise err_type
    except ArithmeticError as err_limit:
        raise err_limit

    try:
        path = _convert_name_to_path_(table_info.name)
        records.to_parquet(path, schema=table_info.schema)
    except pa.ArrowInvalid as err_invalid:
        raise err_invalid
    except pa.ArrowIOError as err_io:
        raise err_io


def _convert_name_to_path_(name: str) -> str:
    """Convert a parquet file's name to a full path."""
    return os.path.join(_PARQUET_DIR_, name + ".pkt")
