"""Utilities related to parquet file storage and retrieval."""
from importlib.resources import files
import os

# Directory where all parquet files are stored.
_PARQUET_DIR_ = str(files("choc_an_simulator") / "storage")


def _convert_parquet_name_to_path_(name: str) -> str:
    """
    Internal function to convert a file name to a full path for Parquet files.

    Args-
        name (str): Base name of the file.

    Returns-
        str: Full path for the specified file name.

    """
    return os.path.join(_PARQUET_DIR_, name + ".pkt")
