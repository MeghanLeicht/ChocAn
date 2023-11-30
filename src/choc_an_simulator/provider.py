"""
Provider Sub-System.

This module facilitates interactions between healthcare providers and the ChocAn Data Center.
It encompasses functions for displaying menus, prompting for member IDs, recording service
billing entries, and managing provider directories. These functions collectively support
billing, service verification, and data retrieval processes in the ChocAn system.
"""
from pyarrow import ArrowIOError
from .database_management import (
    load_records_from_file,
    save_report,
    add_records_to_file,
)
from datetime import datetime
from .schemas import PROVIDER_DIRECTORY_INFO, MEMBER_INFO, SERVICE_LOG_INFO, USER_INFO
from .user_io import prompt_menu_options, PColor, prompt_int, prompt_date, prompt_str
import pandas as pd


def show_provider_menu() -> None:
    """
    Display the provider menu to the user.

    Present the provider with a range of menu options, allowing access to various functionalities
    of the Provider Component, like requesting the provider directory or recording service entries.
    """
    user_exit = False
    while user_exit is False:
        match prompt_menu_options(
            "Provider Menu",
            ["Request Provider Directory", "Record a Service", "Member Check-In"],
        ):
            case (_, "Request Provider Directory"):
                request_provider_directory()
            case (_, "Record a Service"):
                record_service_billing_entry()
            case (_, "Member Check-In"):
                check_in_member()
            case None:
                user_exit = True


def check_in_member() -> None:
    """
    Prompt for a member's ID and display their status.

    Initiates a prompt for the user to enter a member ID, which can be entered through a
    keycard reader or manually via the terminal. Then, displays either "Valid", "Suspended"
    or "Invalid"
    """
    member_id = prompt_int(
        "Please enter Member ID", char_limit=MEMBER_INFO.character_limits["member_id"]
    )

    query_response = load_records_from_file(
        table_info=MEMBER_INFO, eq_cols={"member_id": member_id}
    )

    if query_response.empty:
        PColor.pfail("Invalid")
    elif query_response.at[0, "suspended"]:
        PColor.pwarn("Suspended")
    else:
        PColor.pok("Valid")


def display_member_information() -> None:
    """
    Prompt a member's id, then fetch and display information about a member from the database.

    The displayed data includes the member's name, ID, and status, aiding providers in
    verifying member eligibility and record accuracy.

    Args-
        member_id (int): ID of the member whose information is to be displayed.
    """
    raise NotImplementedError("display_member_information")


def record_service_billing_entry() -> None:
    """
    Record a billing entry for a service provided to a member.

    In this function, the provider enters details of the service rendered. It involves
    validating the member's status, collecting service details, and saving the information
    in the service logs.
    """
    members_df = load_records_from_file(MEMBER_INFO)
    providers_df = load_records_from_file(USER_INFO)

    # Prompt for member ID and validate
    member_id = prompt_int(
        "Enter member ID", char_limit=MEMBER_INFO.character_limits["member_id"]
    )
    if member_id not in members_df["member_id"].values:
        PColor.pfail("Invalid Member ID or Member Suspended")
        return None

    # Prompt for provider ID and validate
    provider_id = prompt_int(
        "Enter provider ID", char_limit=USER_INFO.character_limits["id"]
    )
    if provider_id not in providers_df["id"].values:
        PColor.pfail("Invalid Provider ID")
        return None

    # Prompt for service date
    service_date = prompt_date("Enter service date: ")
    if service_date is None:
        PColor.pfail("Invalid Date Format")
        return None

    # Get Service Code and validate
    service_code = prompt_int(
        "Enter service code",
        char_limit=PROVIDER_DIRECTORY_INFO.character_limits["service_id"],
    )
    services_df = load_records_from_file(PROVIDER_DIRECTORY_INFO)
    if service_code not in services_df["service_id"].values:
        PColor.pfail("Invalid Service Code")
        return None

    # Display the service name and confirm
    service_name = services_df[services_df["service_id"] == service_code][
        "service_name"
    ].iloc[0]
    PColor.pok(f"Service name: {service_name}")
    confirmation = prompt_str("Confirm service (yes/no)", char_limit=range(1, 4))
    if confirmation in ["y", "yes"]:
        PColor.pok("Service Confirmed")
    else:
        PColor.pfail("Service Not Confirmed")
        return None

    # Get Optional Comments
    comments = prompt_str(
        "Enter optional comments, or press Ctrl+C to skip", char_limit=range(1, 101)
    )

    # Create Record
    current_datetime = datetime.now()
    record = pd.DataFrame(
        {
            "entry_datetime_utc": [current_datetime],
            "service_date_utc": [service_date.strftime("%m-%d-%Y")],
            "provider_id": [provider_id],
            "member_id": [member_id],
            "service_id": [service_code],
            "comments": [comments],
        }
    )

    # Display Fee and Save to files
    try:
        fee = services_df[services_df["service_id"] == service_code][
            ["price_dollars", "price_cents"]
        ]
        PColor.pok(
            f"Service Fee: ${fee['price_dollars'].iloc[0]}.{fee['price_cents'].iloc[0]:02d}"
        )
        add_records_to_file(record, SERVICE_LOG_INFO)
        PColor.pok("Service Billing Entry Recorded Successfully")
    except ArrowIOError as e:
        print(f"An error occurred: {e}")


def request_provider_directory() -> None:
    """Save the provider directory to a CSV file, and display the path it was saved to."""
    try:
        provider_directory_df = load_records_from_file(PROVIDER_DIRECTORY_INFO)
    except ArrowIOError:
        PColor.pfail("There was an error loading the provider directory.")
        return
    try:
        provider_directory_report = save_report(
            provider_directory_df, "provider_directory"
        )
    except IOError:
        PColor.pfail("There was an error saving the provider directory report.")
        return
    print("Report saved to", provider_directory_report)
