"""
Functions for generating reports.
"""

from datetime import datetime, timedelta

import pandas as pd
import pyarrow as pa

from choc_an_simulator.database_management.load_records import load_records_from_file
from choc_an_simulator.database_management.reports import save_report
from choc_an_simulator.user_io import PColor
from choc_an_simulator.schemas import (
    MEMBER_INFO,
    PROVIDER_DIRECTORY_INFO,
    SERVICE_LOG_INFO,
    USER_INFO,
)


def generate_member_report() -> None:
    """
    Generate a report for each member who has consulted with a ChocAn provider.
    A 'date' filter will be added to 'gt_cols' to retrieve members that have
    had services provided to them in the last 7 days.The members are listed in
    the order of the service date. After a report is generated, the path to it
    is printed to the consoles.
    """
    gt_cols = {"service_date_utc": datetime.now() - timedelta(days=7)}
    service_log_cols = ["service_date_utc", "member_id", "provider_id", "service_id"]
    member_cols = ["member_id", "name", "address", "city", "state", "zipcode"]
    user_cols = ["name", "id"]
    provider_dir_cols = ["service_name", "service_id"]
    try:
        service_log = load_records_from_file(SERVICE_LOG_INFO, gt_cols=gt_cols)[service_log_cols]
        if service_log.empty:  # Return immediately if empty - no need to load the other data.
            print("No records found within the last 7 days.")
            return
        member_info = load_records_from_file(MEMBER_INFO)[member_cols]
        user_info = load_records_from_file(USER_INFO)[user_cols]
        provder_directory = load_records_from_file(PROVIDER_DIRECTORY_INFO)[provider_dir_cols]
    except pa.ArrowIOError as err_io:
        PColor.pwarn(f"There was an issue accessing the database.\n\tError: {err_io}")
        return

    records = pd.merge(service_log, provder_directory, on="service_id")
    records = pd.merge(records, user_info, left_on="provider_id", right_on="id")
    records = pd.merge(records, member_info, on="member_id")
    records = records.drop(columns="id")

    records = records.rename(
        columns={
            "name_y": "Name",
            "member_id": "Member Number",
            "name_x": "Provider Name",
            "service_date_utc": "Service Date (Local Time)",
        }
    )
    for member_id in records["Member Number"].unique():
        member_records = records[records["Member Number"] == member_id]
        member_name = member_records["Name"].iloc[0]
        file_path = save_report(member_records, f"{member_name}_{_current_date()}")
        print(f"Report saved to {file_path}")


def _current_date() -> str:
    """
    Returns the current date in the format MM-DD-YYYY.
    """
    return datetime.now().strftime("%m-%d-%Y")
