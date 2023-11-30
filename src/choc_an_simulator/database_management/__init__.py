"""
Functions for database input/output operations in the ChocAn Simulator.

Includes capabilities to add, load, update, and remove records in database files, as well as
saving reports. The module works with Parquet and CSV file formats and ensures data integrity
and schema compatibility.
"""

from .load_records import load_records_from_file
from .edit_records import update_record, remove_record, add_records_to_file
from .reports import save_report

__all__ = [
    "load_records_from_file",
    "update_record",
    "remove_record",
    "add_records_to_file",
    "save_report",
]
