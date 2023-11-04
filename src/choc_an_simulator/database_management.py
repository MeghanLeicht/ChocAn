"""Functions related to database Input/Output."""
import os
from typing import Optional, Dict, Any
from importlib.resources import files
import pandas as pd
import pyarrow as pa

# The directory where all parquet files are stored
_PARQUET_DIR_ = str(files("choc_an_simulator") / "storage")


def add_records_to_file(name: str, records: pd.DataFrame, schema: pa.Schema) -> None:
    """
    Add records to a parquet file.

    Args-
        name: The name of the parquet file (no extension)
        records: The records to add to the file
        schema: The file's schema

    Raises-
        ValueError: Added entries cause duplicate entries in the first column
        pyarrow.ArrowInvalid: Mismatch between the dataframe and the schema.
        pyarrow.ArrowIOError: I/O-related error (e.g. permissions, file lock, etc.)
        KeyError: Mismatch between schema & records, or schema & file.

    """
    # Load file into memory
    try:
        existing_records = _load_all_records_from_file_(name, schema)
    except pa.ArrowInvalid as err_invalid:
        raise err_invalid
    except pa.ArrowIOError as err_io:
        raise err_io
    except KeyError as err_key:
        # Schema / file mismatch
        raise err_key

    # Check that index name is correct
    if schema.names[0] != records.columns[0]:
        raise KeyError("Mismatch between schema & records.")
    # Check that the addition will cause no duplicate indices
    if existing_records[schema.names[0]].isin(records[schema.names[0]]).any():
        raise ValueError("Added entries cause duplicates in the first column.")

    # Add the new data and save
    records = pd.concat([existing_records, records])
    try:
        _overwrite_records_to_file_(name, records, schema)
    except pa.ArrowInvalid as err_invalid:
        raise err_invalid
    except pa.ArrowIOError as err_io:
        raise err_io


def load_records_from_file(
    name: str,
    schema: pa.Schema,
    eq_cols: Optional[Dict[str, Any]] = None,
    lt_cols: Optional[Dict[str, Any]] = None,
    gt_cols: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Load and filter records from a file.

    Args-
        name: The name of the parquet file (no extension)
        schema: The file's schema
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
        records = load_records_from_file("example", example_schema)

        # Get all logs from the last month:
        records = load_records_from_file(
            name = "example",
            schema = example_schema,
            gt_cols = {"date": datetime.now() - timedelta(days=31)}
        )

        # Get all records with ID = 1234
        records = load_records_from_file(
            name = "example",
            schema = example_schema,
            eq_cols = {"ID" : 1234}
        )
    """
    try:
        records = _load_all_records_from_file_(name, schema)
    except pa.ArrowInvalid as err_invalid:
        raise err_invalid
    except pa.ArrowIOError as err_io:
        raise err_io
    except KeyError as err_key:
        raise err_key

    if eq_cols is not None:
        for col, val in eq_cols.items():
            if col not in schema.names:
                raise KeyError("eq_cols name {col} not found in schema.")
            try:
                records = records[records[col] == val]
            except TypeError as err_type:
                raise TypeError(f"{err_type}: {col} == {val} not supported.")
    if lt_cols is not None:
        for col, val in lt_cols.items():
            if col not in schema.names:
                raise KeyError(f"lt_cols name {col} not found in schema.")
            try:
                records = records[records[col] < val]
            except TypeError as err_type:
                raise TypeError(f"{err_type}: {col} < {val} not supported.")
    if gt_cols is not None:
        for col, val in gt_cols.items():
            if col not in schema.names:
                raise KeyError(f"gt_cols name {col} not found in schema.")
            try:
                records = records[records[col] > val]
            except TypeError as err_type:
                raise TypeError(
                    f"{err_type}: {col} > records = records[records[col] > val]{val} not supported."
                )

    return records


def update_record(name: str, index: Any, schema: pa.Schema, **kwargs) -> pd.Series:
    """
    Update a single record in a database file.

    Args-
        name: Name of the parquet database
        index: Value to match in the first column of the database
        schema: Schema of the parquet database
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

        # Update service #12 to be Zamboni Accident
        updated_service = update_record("services",12,service_schema, service_name = "Bad eyeballs")

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
    records = _load_all_records_from_file_(name, schema)

    index_col = schema.names[0]
    try:
        index = records[records[index_col] == index].index.values[0]
    except IndexError:
        raise IndexError(f"Index {index} not found in {name}")

    for key, value in kwargs.items():
        if key not in schema.names:
            raise KeyError(f"Column {key} not found in {name}")
        records.loc[index, key] = value

    try:
        _overwrite_records_to_file_(name, records, schema)
    except pa.ArrowInvalid as err_type:
        raise err_type
    except pa.ArrowIOError as err_io:
        raise err_io

    return records.loc[index]


def remove_record(name: str, index: Any, schema: pa.Schema) -> bool:
    """
    Remove a single record from a database file.

    Args-
        name: Name of the parquet database
        index: Value to match in the first column of the database. Row wit this index is removed.
        schema: Schema of the parquet database

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
        records = _load_all_records_from_file_(name, schema)
    except pa.ArrowInvalid as err_invalid:
        raise err_invalid
    except pa.ArrowIOError as err_io:
        raise err_io
    except KeyError as err_key:
        raise err_key

    index_col = schema.names[0]
    if index not in records[index_col]:
        return False
    records = records[records[index_col] != index]

    try:
        _overwrite_records_to_file_(name, records, schema)
    except pa.ArrowIOError as err_io:
        raise err_io
    return True


def _load_all_records_from_file_(name: str, schema: pa.Schema) -> pd.DataFrame:
    """
    Load an entire parquet file into a dataframe.

    If no file is found, returns an empty dataframe with the given schema.

    Args-
        name: The name of the parquet file (no extension)
        schema: The file's schema
    Returns-
        All records in the file, or none if no file found.
    Raises-
        pyarrow.ArrowInvalid: File format is invalid
        pyarrow.ArrowIOError: I/O-related error (e.g. permissions, file lock, etc.)
        KeyError: File columns do not match schema
    """
    path = _convert_name_to_path_(name)
    try:
        records = pd.read_parquet(path)
    except FileNotFoundError:
        return pa.Table.from_pylist([], schema=schema).to_pandas()
    except (pa.ArrowInvalid, pa.ArrowIOError) as err_arrow:
        raise err_arrow

    if _check_schema_columns_(schema, records) is False:
        raise KeyError("File columns do not match schema")

    return records


def _overwrite_records_to_file_(
    name: str, records: pd.DataFrame, schema: pa.Schema
) -> None:
    """
    Overwrite a parquet file with new records.

    Args-
        name: The name of the parquet file (without the .pkt extension).
        records: The records to write to file.
        schema: The file's schema.
    Raises-
        pyarrow.ArrowInvalid: Type mismatch between dataframe and schema.
        pyarrow.ArrowIOError: I/O-related error (e.g. permissions, file lock, etc.).
        KeyError: Mismatch between records and schema.

    """
    if _check_schema_columns_(schema, records) is False:
        raise KeyError("Record columns don't match schema.")

    try:
        records.to_parquet(_convert_name_to_path_(name), schema=schema)
    except pa.ArrowInvalid as err_invalid:
        raise err_invalid
    except pa.ArrowIOError as err_io:
        raise err_io


def _convert_name_to_path_(name: str) -> str:
    """Convert a parquet file's name to a full path."""
    return os.path.join(_PARQUET_DIR_, name + ".pkt")


def _check_schema_columns_(schema: pa.Schema, dataframe: pd.DataFrame) -> bool:
    """Check that a dataframe and a schema have the same column names."""
    return set(schema.names) == set(dataframe.columns)
