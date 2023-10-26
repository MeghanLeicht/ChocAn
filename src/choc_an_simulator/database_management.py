"""Functions related to database Input/Output."""
import os
from typing import Optional, Dict, Any
from importlib.resources import files
import pandas as pd
import pyarrow as pa
import choc_an_simulator

# The directory where all parquet files are stored
_PARQUET_DIR_ = str(files("choc_an_simulator") / "storage")


def add_records_to_file(
    name: str, records: pd.DataFrame, schema: pa.Schema
) -> pd.DataFrame:
    """
    Add records to a parquet file.

    Args-
        name: The name of the parquet file (no extension)
        records: The records to add to the file
        schema: The file's schema
    """
    existing_records = _load_all_records_from_file_(name, schema)
    records = pd.concat([existing_records, records])
    _overwrite_records_to_file_(name, records, schema)
    return records


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


if __name__ == "_main_":
    records = pd.DataFrame({"col_a": [1, 2, 3], "col_b": ["a", "b", "c"]})
    schema = pa.schema([pa.field("col_a", pa.int64()), pa.field("col_b", pa.string())])
    print(load_records_from_file("test", schema))
    add_records_to_file("test", records, schema)
