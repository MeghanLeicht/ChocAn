"""
Provider Sub-System.

This module facilitates interactions between healthcare providers and the ChocAn Data Center.
It encompasses functions for displaying menus, prompting for member IDs, recording service
billing entries, and managing provider directories. These functions collectively support
billing, service verification, and data retrieval processes in the ChocAn system.
"""
from choc_an_simulator.user_io import prompt_menu_options


def show_provider_menu() -> None:
    """
    Display the provider menu to the user.

    Present the provider with a range of menu options, allowing access to various functionalities
    of the Provider Component, like requesting the provider directory or recording service entries.
    """
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
    pass


def check_in_member() -> None:
    """
    Prompt for a member's ID and display their status.

    Initiates a prompt for the user to enter a member ID, which can be entered through a
    keycard reader or manually via the terminal. Then, displays either "Valid", "Suspended"
    or "Invalid"
    """
    raise NotImplementedError("check_in_member")


def display_member_information(member_id: int) -> None:
    """
    Fetch and display information about a member from the member database.

    The displayed data includes the member's name, ID, and status, aiding providers in
    verifying member eligibility and record accuracy.

    Args-
        member_id (int): ID of the member whose information is to be displayed.
    """
    pass


def record_service_billing_entry() -> None:
    """
    Record a billing entry for a service provided to a member.

    In this function, the provider enters details of the service rendered. It involves
    validating the member's status, collecting service details, and saving the information
    in the service logs.
    """
    pass


def request_provider_directory() -> None:
    """Save the provider directory to a CSV file, and display the path it was saved to."""
    pass
