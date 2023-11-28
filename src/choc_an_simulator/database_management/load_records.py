"""Functions for loading data from the database."""
from typing import Dict, Callable, Any, Optional
import operator
import pandas as pd
import pyarrow as pa
from ._parquet_utils import _convert_parquet_name_to_path_
from ..schemas import TableInfo


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
    records = _apply_filter(records, eq_cols, operator.eq, table_info)
    records = _apply_filter(records, lt_cols, operator.lt, table_info)
    records = _apply_filter(records, gt_cols, operator.gt, table_info)

    return records


def _apply_filter(
    records: pd.DataFrame,
    col_filters: Optional[Dict[str, Any]],
    operator: Callable,
    table_info: TableInfo,
) -> pd.DataFrame:
    """
    Apply a filter to the DataFrame based on the specified operator.

    Args-
        records (pd.DataFrame): The DataFrame to be filtered.
        col_filters (Dict[str, DB_FIELD_PYTYPE]): The columns and values for filtering.
        operator (Callable): The comparison operator (e.g., eq, lt, gt).
        table_info (TableInfo): Object with schema and table details.

    Returns-
        pd.DataFrame: Filtered DataFrame.
    """
    if col_filters is None:
        return records
    for col, val in col_filters.items():
        if col not in table_info.schema.names:
            raise KeyError(f"Column name {col} not found in schema.")
        try:
            records = records[operator(records[col], val)]
        except TypeError as err_type:
            raise TypeError(
                f"{err_type}: Operation {operator} on {col} with value {val} not supported."
            )
    return records


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
