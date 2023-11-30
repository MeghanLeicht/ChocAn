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
from choc_an_simulator.schemas import (
    MEMBER_INFO,
    PROVIDER_DIRECTORY_INFO,
    SERVICE_LOG_INFO,
    USER_INFO,
)
from choc_an_simulator.user_io import PColor


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
                    (date, service_name, provider_name)
                    for date, service_name, provider_name, in x
                ]
            )
        )
        file_path = save_report(
            member_record, f"{member_record['Name'].iloc[0]}_{_current_date()}"
        )
        print(f"Member Report saved to {file_path}")


def generate_provider_report() -> None:
    """
    Generates a report of services rendered by a provider over the last 7 days.

    Generate a report for each provider who has rendered services to a ChocAn member.
    A 'date' filter will be added to 'gt_cols' to retrieve providers that have had services rendered
    in the last 7 days. Additionally, if the number of consultations is greater than 999, it will
    be set to 999. If the total fee is greater than 99999.99, it will be set to 99999.99. After a
    report is generated, the path to it is printed to the console.
    """
    gt_cols = {"service_date_utc": datetime.now() - timedelta(days=7)}
    service_log = None
    provider_directory = None
    member_info = None
    user_info = None
    service_log_cols = [
        "service_date_utc",
        "member_id",
        "provider_id",
        "service_id",
        "entry_datetime_utc",
    ]
    member_cols = ["member_id", "name"]
    user_cols = ["name", "id", "address", "city", "state", "zipcode"]
    provider_directory_cols = ["service_id", "price_cents", "price_dollars"]

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

    records = pd.merge(service_log, provider_directory, on="service_id")
    records = pd.merge(records, user_info, left_on="provider_id", right_on="id")
    records = pd.merge(records, member_info, on="member_id")
    records["Fee to be paid"] = records["price_dollars"] + records["price_cents"] / 100
    records = records.drop(columns=["id", "price_dollars", "price_cents"])

    for provider_id in records["provider_id"].unique():
        provider_record = records[records["provider_id"] == provider_id]
        current_provider = records["provider_id"] == provider_id
        # calculate_total_fee is broken out into a function to make it easier to mock for testing
        total_fee = calculate_total_fee(provider_record["Fee to be paid"])
        if total_fee < 99999.99:
            records.loc[current_provider, "Total fee for the week"] = total_fee
        else:
            records.loc[current_provider, "Total fee for the week"] = 99999.99

        # calculate_length_of_consultations is broken out into a function to make it easier to mock
        # for testing
        total_consultations = calculate_length_of_consultations(provider_record)
        if total_consultations < 999:
            records.loc[
                current_provider, "Total number of consultations with members"
            ] = total_consultations
        else:
            records.loc[
                current_provider, "Total number of consultations with members"
            ] = 999

    records = records.rename(
        columns={
            "name_x": "Provider Name",
            "provider_id": "Provider Number",
            "name_y": "Member Name",
            "member_id": "Member Number",
            "service_date_utc": "Date of Service",
            "entry_datetime_utc": "Date and Time Data Were Received by the Computer",
            "service_id": "Service Code",
        }
    )

    records = records[
        [
            "Provider Name",
            "Provider Number",
            "address",
            "city",
            "state",
            "zipcode",
            "Date of Service",
            "Date and Time Data Were Received by the Computer",
            "Member Name",
            "Member Number",
            "Service Code",
            "Fee to be paid",
            "Total number of consultations with members",
            "Total fee for the week",
        ]
    ]

    # For each provider save the report and print the path to the console
    for provider_id in records["Provider Number"].unique():
        provider_record = records[records["Provider Number"] == provider_id]
        file_path = save_report(
            provider_record,
            f"{provider_record['Provider Name'].iloc[0]}_{_current_date()}",
        )
        print(f"Provider Report saved to {file_path}")


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


def calculate_total_fee(providers_fees_df: pd.DataFrame) -> float:
    """Calculates the total fee for a provider."""
    return providers_fees_df.sum()


def calculate_length_of_consultations(providers_consultations_df: pd.DataFrame) -> int:
    """Calculates the total number of consultations for a provider."""
    return len(providers_consultations_df)
