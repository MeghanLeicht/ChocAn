"""
Functions for generating administrative reports.

Member reports are generated for each member who has consulted with a ChocAn
providers within the last 7 days.

Provider reports are generated for each provider who has provided services to
ChocAn members within the last 7 days.

Summary reports are generated for all accounts payable this week
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
    Generates a report of services for a member over the last 7 days.

    Generate a report for each member who has consulted with a ChocAn provider.
    A 'date' filter will be added to 'gt_cols' to retrieve members that have
    had services provided to them in the last 7 days.The members are listed in
    the order of the service date. After a report is generated, the path to it
    is printed to the console.
    """
    gt_cols = {"service_date_utc": datetime.now() - timedelta(days=7)}
    service_log = None
    provider_directory = None
    member_info = None
    user_info = None
    service_log_cols = ["service_date_utc", "member_id", "provider_id", "service_id"]
    member_cols = ["member_id", "name", "address", "city", "state", "zipcode"]
    user_cols = ["name", "id"]
    provider_directory_cols = ["service_id", "service_name"]

    try:
        service_log = load_records_from_file(SERVICE_LOG_INFO, gt_cols=gt_cols)
        if service_log.empty:
            print("No records found within the last 7 days.")
            return
        service_log = service_log[service_log_cols]
        member_info = load_records_from_file(MEMBER_INFO, gt_cols=gt_cols)[member_cols]
        user_info = load_records_from_file(USER_INFO, gt_cols=gt_cols)[user_cols]
        provider_directory = load_records_from_file(PROVIDER_DIRECTORY_INFO)[
            provider_directory_cols
        ]
    except pa.ArrowIOError as err_io:
        PColor.pwarn(f"There was an issue accessing the database.\n\tError: {err_io}")
        return

    merged_dfs = pd.merge(service_log, provider_directory, on="service_id")
    merged_dfs = pd.merge(merged_dfs, user_info, left_on="provider_id", right_on="id")
    merged_dfs = pd.merge(merged_dfs, member_info, on="member_id")
    merged_dfs = merged_dfs.drop(columns="id")

    # Create a new column storing a list of tuples containing the service date, service name, and
    # provider name
    merged_dfs["Services"] = list(
        zip(
            merged_dfs["service_date_utc"],
            merged_dfs["service_name"],
            merged_dfs["name_x"],
        )
    )
    agg_dict = {"Services": list}
    # Group by member_id and aggregate the services column into a list
    records = merged_dfs.groupby("member_id").agg(agg_dict).reset_index()
    # Merge the original dataframe with the aggregated dataframe resulting in a new dataframe
    # replaced the 3 service columns with the aggregated services column and is grouped by member_id
    records = records.merge(
        merged_dfs[
            ["member_id", "name_y", "address", "city", "state", "zipcode"]
        ].drop_duplicates(),
        on="member_id",
        how="left",
    )
    records = records.rename(
        columns={
            "name_y": "Name",
            "member_id": "Member Number",
            "name_x": "Provider Name",
            "service_date_utc": "Service Date",
        }
    )
    records = records[
        ["Name", "Member Number", "address", "city", "state", "zipcode", "Services"]
    ]

    # For each member, sort the services by date and then save the report and print the path to
    # the console
    for member_id in records["Member Number"]:
        member_record = records[records["Member Number"] == member_id]
        # member_record["Services"] = member_record["Services"].apply(lambda x: sorted(x))
        member_record.loc[:, "Services"] = member_record.loc[:, "Services"].apply(
            lambda x: sorted(
                [
                    (datetime.date(date), service_name, provider_name)
                    for date, service_name, provider_name, in x
                ]
            )
        )
        file_path = save_report(
            member_record, f"{member_record['Name'].iloc[0]}_{_current_date()}"
        )
        print(f"Report saved to {file_path}")


def generate_provider_report() -> None:
    """
    Each provider who has billed ChocAn during that week receives a report.

    The fields of the report include:
    Provider name (25 characters).
    Provider number (9 digits).
    Provider street address (25 characters).
    Provider city (14 characters).
    Provider state (2 letters).
    Provider zip code (5 digits).
    For each service provided, the following details are required:
    Date of service (MM-DD-YYYY).
    Date and time data were received by the computer (MM-DD-YYYY
    HH:MM:SS).
    Member name (25 characters).
    Member number (9 digits).
    Service code (6 digits).
    Fee to be paid (up to $999.99).
    Total number of consultations with members (3 digits).
    Total fee for the week (up to $99,999.99)
    """
    raise NotImplementedError("generate_provider_report")


def generate_summary_report() -> None:
    """
    A summary report is given to the manager for accounts payable.

    The report lists every provider to be paid that week, the number of consultations each had, and
    his or her total fee for that week. Finally the total number of providers who
    provided services, the total number of consultations, and the overall fee total are
    printed.
    """
    raise NotImplementedError("generate_summary_report")


def _current_date() -> str:
    """Returns the current date in the format MM-DD-YYYY."""
    return datetime.now().strftime("%m-%d-%Y")
