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
        ValueError: Duplicate entries in the first column
    """
    existing_records = _load_all_records_from_file_(name, schema)
    if existing_records[schema.names[0]].isin(records[schema.names[0]]).any():
        raise ValueError("Duplicate entries found in the first column.")
    records = pd.concat([existing_records, records])
    _overwrite_records_to_file_(name, records, schema)


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
    records = _load_all_records_from_file_(name, schema)
    if eq_cols is not None:
        for col, val in eq_cols.items():
            assert col in schema.names, f"eq_cols name {col} not found in schema."
            records = records[records[col] == val]
    if lt_cols is not None:
        for col, val in lt_cols.items():
            assert col in schema.names, f"lt_cols name {col} not found in schema."
            records = records[records[col] < val]
    if gt_cols is not None:
        for col, val in gt_cols.items():
            assert col in schema.names, f"gt_cols name {col} not found in schema."
            records = records[records[col] > val]

    return records


def update_record(name: str, index: Any, schema: pa.Schema, **kwargs) -> pd.Series:
    """
    Update a single record in a database.

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
        KeyError: column name not found

    Examples-
        # Update the name of member 1234 to Martha
        updated_member = update_record("members",1234,member_schema, name = "Martha")

        # Update service #12 to be Zamboni Accident
        updated_service = update_record("services",12,service_schema, service_name = "Zamboni Attack")

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
    except IndexError as index_error:
        raise IndexError(f"Index {index} not found in {name}")
    for key, value in kwargs.items():
        if key not in schema.names:
            raise KeyError(f"Column {key} not found in {name}")
        records.loc[index, key] = value
    _overwrite_records_to_file_(name, records, schema)
    return records.loc[index]


def remove_record(name: str, index: Any, schema: pa.Schema) -> bool:
    """
    Update a single record in a database.

    Args-
        name: Name of the parquet database
        index: Value to match in the first column of the database. Row wit this index is removed.
        schema: Schema of the parquet database

    Returns-
        True: Row with matching index was removed
        False: Index was not found.

    Raises-
        IndexError: Index not found
        KeyError: column name not found

    Examples-
        # Remove member 1234

        if remove_record("members",1234,member_schema):
            print("Member 1234 Removed")
        else:
            print("Member 1234 Not Found.")
    """
    records = _load_all_records_from_file_(name, schema)
    index_col = schema.names[0]
    if index not in records[index_col]:
        return False
    records = records[records[index_col] != index]
    _overwrite_records_to_file_(name, records, schema)
    return True


def _convert_name_to_path_(name: str) -> str:
    """Convert a parquet file's name to a full path."""
    return os.path.join(_PARQUET_DIR_, name + ".pkt")


def _load_all_records_from_file_(name: str, schema: pa.Schema) -> pd.DataFrame:
    """
    Load an entire parquet file into a dataframe.

    Args-
        name: The name of the parquet file (no extension)
        schema: The file's schema
    Returns-
        All records in the file. If the file doesn't exist, returns an empty dataframe.
    """
    path = _convert_name_to_path_(name)
    if not os.path.exists(path):
        return pa.Table.from_pylist([], schema=schema).to_pandas()
    records = pd.read_parquet(path, schema=schema)
    return records


def _overwrite_records_to_file_(
    name: str, records: pd.DataFrame, schema: pa.Schema
) -> None:
    """
    Overwrite a parquet file with new records.

    Args-
        name: The name of the parquet file (no      ValueError: invalid pyproject.toml config: `project.requires-python`. extension)
        records: The records to write to file
        schema: The file's schema
    """
    records.to_parquet(_convert_name_to_path_(name), schema=schema)
