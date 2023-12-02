"""
Functions for database input/output operations in the ChocAn Simulator.

Includes capabilities to add, load, update, and remove records in database files, as well as
saving reports. The module works with Parquet and CSV file formats and ensures data integrity
and schema compatibility.
"""

from .load_records import load_records_from_file, load_record
from .edit_records import update_record, remove_record, add_record_to_file
from .reports import save_report

__all__ = [
    "load_records_from_file",
    "load_record",
    "update_record",
    "remove_record",
    "add_record_to_file",
    "save_report",
]
