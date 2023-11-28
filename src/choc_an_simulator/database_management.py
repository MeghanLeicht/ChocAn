"""
Functions for database input/output operations in the ChocAn Simulator.

Includes capabilities to add, load, update, and remove records in database files, as well as
saving reports. The module works with Parquet and CSV file formats and ensures data integrity
and schema compatibility.
"""

import os
from datetime import date
from dateutil.tz import tzlocal
from typing import Optional, Dict, Any
from importlib.resources import files
import pandas as pd
import pyarrow as pa
from .schemas import TableInfo

# Directory where all parquet files are stored.
_PARQUET_DIR_ = str(files("choc_an_simulator") / "storage")
# Directory where report files are stored.
_REPORT_DIR_ = str(files("choc_an_simulator") / "reports")


def add_records_to_file(records: pd.DataFrame, table_info: TableInfo) -> None:
    """
    Add new records to an existing Parquet file based on the provided schema.

    Args-
        records (pd.DataFrame): New records to be added.
        table_info (TableInfo): Object containing schema and other table-related information.

    Raises-
        ValueError: Added records result in duplicate entries in the index column.
        pyarrow.ArrowInvalid: Mismatch between the DataFrame and the schema.
        pyarrow.ArrowIOError: I/O error occurs (e.g., file permissions, file lock).
        KeyError: Mismatch between schema & records, or schema & file's schema.
        TypeError: Unsupported type.
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
    except pa.ArrowIOError as err_io:
        raise err_io


def load_records_from_file(
    table_info: TableInfo,
    eq_cols: Optional[Dict[str, Any]] = None,
    lt_cols: Optional[Dict[str, Any]] = None,
    gt_cols: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Load records from a Parquet file, optionally applying filters for record selection.

    Args-
        table_info (TableInfo): Object with schema and table details.
        eq_cols (Optional[Dict[str, Any]]): Specifies columns and values for equality filtering.
        lt_cols (Optional[Dict[str, Any]]): Specifies columns and values for less-than filtering.
        gt_cols (Optional[Dict[str, Any]]): Specifies columns and values for greater-than filtering.

    Returns-
        pd.DataFrame:
            Records matching the specified filters, or all records if no filters are applied.

    Raises-
        KeyError: Mismatch between schema & records.
        pyarrow.ArrowTypeError: Type mismatch in the added records.
        pyarrow.ArrowInvalid: Schema-dataframe mismatch.
        pyarrow.ArrowIOError: I/O error occurs.
        TypeError: Unsupported type comparisons in filters.

    Examples-
        #Ex 1. Get all records, no filters:
        records = load_records_from_file(example_table_info)

        #Ex 2. Get all logs from the last month:
        records = load_records_from_file(
            table_info = example_table_info,
            gt_cols = {"date": datetime.now() - timedelta(days=31)}
        )

        #Ex 3. Get all records with ID = 1234
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

    # Apply filters
    if eq_cols is not None:
        for col, val in eq_cols.items():
            if col not in table_info.schema.names:
                raise KeyError(f"eq_cols name {col} not found in schema.")
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

    try:
        index = records[records[table_info.index_col()] == index].index.values[0]
    except IndexError:
        raise IndexError(f"Index {index} not found in {table_info.name}")

    for field_name, value in kwargs.items():
        try:
            table_info.check_field(value, field_name)
        except KeyError as err_key:
            raise err_key
        except TypeError as err_type:
            raise err_type
        except ArithmeticError as err_out_of_range:
            raise err_out_of_range
        records.loc[index, field_name] = value

    try:
        _overwrite_records_to_file_(records, table_info)
    except pa.ArrowIOError as err_io:
        raise err_io

    return records.loc[index]


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

    if index not in records[table_info.index_col()]:
        return False
    records = records[records[table_info.index_col()] != index]

    try:
        _overwrite_records_to_file_(records, table_info)
    except pa.ArrowIOError as err_io:
        raise err_io
    return True


def save_report(table: pd.DataFrame, file_name: str) -> str:
    """
    Save a DataFrame to a CSV file, converting dates and datetimes to local time strings.

    Args-
        table (pd.DataFrame): Data to be saved.
        file_name (str): Name of the file (without directory or extension) to save the report.

    Returns-
        str: Full path where the report was saved.

    Raises-
        IOError: Error while writing the report to the file.
    """
    dttm_fmt = "%m-%d-%Y %H:%M"
    date_fmt = "%m-%d-%Y"
    path = _convert_report_name_to_path_(file_name)
    for col_name, col_dtype in table.dtypes.items():
        # Convert all dates to strings
        if str(col_dtype) == "object":
            table[col_name] = table[col_name].apply(
                lambda val: val.strftime(date_fmt) if isinstance(val, date) else val
            )
        # Convert all timezone-aware datetimes to local time
        elif str(col_dtype).startswith("datetime64[ns, "):
            table[col_name] = (
                table[col_name].dt.tz_convert(tzlocal()).dt.strftime(dttm_fmt)
            )
    try:
        table.to_csv(path, index=False)
    except IOError as err_io:
        raise err_io

    return path


def _load_all_records_from_file_(table_info: TableInfo) -> pd.DataFrame:
    """
    Internal function to load all records from a Parquet file into a DataFrame.

    Args-
        table_info (TableInfo): Object with schema and table details.

    Returns-
        pd.DataFrame:
            DataFrame with all records from the file, or an empty DataFrame if no file was found.

    Raises-
        pyarrow.ArrowInvalid: File format is invalid.
        pyarrow.ArrowIOError: I/O error occurs.
        KeyError: File columns do not match schema.
    """
    path = _convert_parquet_name_to_path_(table_info.name)
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
        Internal function to overwrite a Parquet file with new records.

        Args-
            records (pd.DataFrame): Records to be written.
            table_info (TableInfo): Object with schema and table details.
    The
        Raises-
            KeyError: Mismatch between records and schema columns.
            TypeError: Incorrect types in records.
            ArithmeticError: Values in records outside specified limits in table_info.
            pyarrow.ArrowIOError: I/O error occurs.

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
        path = _convert_parquet_name_to_path_(table_info.name)
        records.to_parquet(path, schema=table_info.schema)
    except pa.ArrowIOError as err_io:
        raise err_io


def _convert_parquet_name_to_path_(name: str) -> str:
    """
    Internal function to convert a file name to a full path for Parquet files.

    Args-
        name (str): Base name of the file.

    Returns-
        str: Full path for the specified file name.

    """
    return os.path.join(_PARQUET_DIR_, name + ".pkt")


def _convert_report_name_to_path_(name: str) -> str:
    """
    Internal function to convert a file name to a full path for CSV files.

    Args-
        name (str): Base name of the file.

    Returns-
        str: Full path for the specified file name.

    """
    return os.path.join(_REPORT_DIR_, name + ".csv")
