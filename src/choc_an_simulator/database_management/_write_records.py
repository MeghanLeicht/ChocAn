"""Functions for writing records to a database file."""
import pandas as pd
import pyarrow as pa
from ._parquet_utils import _convert_parquet_name_to_path_
from ..schemas import TableInfo


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
