"""
Provider Sub-System.

This module facilitates interactions between healthcare providers and the ChocAn Data Center.
It encompasses functions for displaying menus, prompting for member IDs, recording service
billing entries, and managing provider directories. These functions collectively support
billing, service verification, and data retrieval processes in the ChocAn system.
"""
# from .schemas import MEMBER_INFO
from .schemas import SERVICE_LOG_INFO, PROVIDER_DIRECTORY_INFO
from .database_management import add_records_to_file, load_records_from_file
from .user_io import PColor, prompt_date, prompt_str, prompt_int
from datetime import datetime
import pandas as pd
from choc_an_simulator.user_io import prompt_menu_options


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
    raise NotImplementedError("check_in_member")


def display_member_information() -> None:
    """
    Prompt a member's id, then fetch and display information about a member from the database.

    The displayed data includes the member's name, ID, and status, aiding providers in
    verifying member eligibility and record accuracy.

    Args-
        member_id (int): ID of the member whose information is to be displayed.
    """
    raise NotImplementedError("display_member_information")


def record_service_billing_entry(member_id: int) -> None:
    """
    Record a billing entry for a service provided to a member.

    In this function, the provider enters details of the service rendered. It involves
    validating the member's status, collecting service details, and saving the information
    in the service logs.

    Args-
        member_id (int): The member's unique nine-digit ID.

    Returns-
        None
    """
    providers_df = load_records_from_file(SERVICE_LOG_INFO)

    # Prompt for provider ID
    provider_id = prompt_int(
        "Enter provider ID",
        char_limit=SERVICE_LOG_INFO.character_limits["provider_id"],
        numeric_limit=range(100000000, 1000000000),
    )  # 9 digits provider ID

    # Validate provider
    if provider_id not in providers_df["provider_id"].values:
        PColor.pfail("Invalid Provider ID")
        return None

    # Prompt for service date
    service_date = prompt_date("Enter service date: ")
    if service_date is None:
        PColor.pfail("Invalid Service Date")
        return None

    # Get Service Code
    service_code = prompt_int(
        "Enter service code",
        char_limit=PROVIDER_DIRECTORY_INFO.character_limits["service_id"],
        numeric_limit=range(100000, 1000000),
    )  # 6 digits service code
    services_df = load_records_from_file(PROVIDER_DIRECTORY_INFO)
    if service_code not in services_df["service_id"].values:
        PColor.pfail("Invalid Service Code")
        return None

    # Display the service name and confirm
    service_name = services_df[services_df["service_id"] == service_code][
        "service_name"
    ].iloc[0]
    PColor.pok(f"Service name: {service_name}")
    confirmation = prompt_str("Confirm service (yes/no): ").strip().lower()
    if confirmation in ["y", "yes"]:
        PColor.pok("Service Confirmed")
    else:
        PColor.pfail("Service Not Confirmed")
        return None

    # Get Optional Comments
    comments = prompt_str(
        "Enter comments (optional): ", char_limit=range(1, 101)
    )  # max of 100 characters for comments

    # Create Record
    current_datetime = datetime.now().strftime("%m-%d-%Y %H:%M:%S")
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

    # Display Fee and Record for Verification

    fee = services_df[services_df["service_id"] == service_code][
        ["price_dollars", "price_cents"]
    ]
    PColor.pok(
        f"Service Fee: ${fee['price_dollars'].iloc[0]}.{fee['price_cents'].iloc[0]:02d}"
    )

    # Save Record for Reporting
    add_records_to_file(record, SERVICE_LOG_INFO)
    PColor.pok("Service Billing Entry Recorded Successfully")


def request_provider_directory() -> None:
    """Save the provider directory to a CSV file, and display the path it was saved to."""
    raise NotImplementedError("request_provider_directory")


if __name__ == "__main__":
    record_service_billing_entry(123456789)
