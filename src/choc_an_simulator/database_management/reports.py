"""Functions for saving report files."""
from importlib.resources import files
import os
from datetime import date
from dateutil.tz import tzlocal
import pandas as pd

# Directory where report files are stored.
_REPORT_DIR_ = str(files("choc_an_simulator") / "reports")
# Format for datetime strings in the report file
DTTM_FMT = "%m-%d-%Y %H:%M"
# Format for date strings in the report file
DATE_FMT = "%m-%d-%Y"


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
    path = _convert_report_name_to_path_(file_name)
    table = _convert_datetimes_to_formatted_str(table)
    try:
        table.to_csv(path, index=False)
    except IOError as err_io:
        raise err_io

    return path


def _convert_datetimes_to_formatted_str(table: pd.DataFrame) -> pd.DataFrame:
    """
    Convert each date and datetime column to a column of formatted strings.

    Args-
        table (pd.DataFrame): Table to convert.

    Returns-
        pd.DataFrame: The converted table.

    """
    for col_name, col_dtype in table.dtypes.items():
        # Convert all dates to strings
        if str(col_dtype) == "object":
            table[col_name] = table[col_name].apply(
                lambda val: val.strftime(DATE_FMT) if isinstance(val, date) else val
            )
        # Convert all timezone-aware datetimes to local time
        elif str(col_dtype).startswith("datetime64[ns, "):
            table[col_name] = table[col_name].dt.tz_convert(tzlocal()).dt.strftime(DTTM_FMT)
    return table


def _convert_report_name_to_path_(name: str) -> str:
    """
    Internal function to convert a file name to a full path for CSV files.

    Args-
        name (str): Base name of the file.

    Returns-
        str: Full path for the specified file name.

    """
    return os.path.join(_REPORT_DIR_, name + ".csv")
