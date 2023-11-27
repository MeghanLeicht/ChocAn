"""
Manager Sub-System.

The manager sub-system allows managers to manage member, provider, and provider directory records.
"""
import pandas as pd
from pyarrow import ArrowIOError
from pandas.api.types import is_numeric_dtype
from .database_management import (
    load_records_from_file,
    add_records_to_file,
    update_record,
)
from .schemas import USER_INFO, MEMBER_INFO, TableInfo
from .user_io import prompt_str, prompt_int, PColor

from choc_an_simulator.user_io import prompt_menu_options


def manager_menu() -> None:
    """
    The Manager menu provides access to the following key functionalities.

    Add Member
    Update Member
    Remove Member
    Add Provider
    Update Provider
    Remove Provider
    Add Provider Directory
    Update Provider Directory
    Remove Provider Directory
    Generate Member Report
    Generate Provider Report
    Generate Summary Report
    """
    raise NotImplementedError


def add_member_record() -> None:
    """
    Manager is prompted to enter member information.

    Member information: member id, name, street address, city, state, zip code, and suspended.
    The member number will be generated from _generate_user_id().
    """
    try:
        member_id = _generate_user_id(MEMBER_INFO)
    except IndexError:
        PColor.pfail(
            "The maximum number of members has been reached. No new member added."
        )
        return

    member_df = pd.DataFrame(
        {
            "member_id": member_id,
            "name": prompt_str("Name", MEMBER_INFO.character_limits["name"]),
            "address": prompt_str("Address", MEMBER_INFO.character_limits["address"]),
            "city": prompt_str("City", MEMBER_INFO.character_limits["city"]),
            "state": prompt_str("State", MEMBER_INFO.character_limits["state"]),
            "zipcode": prompt_int("Zipcode", MEMBER_INFO.character_limits["zipcode"]),
            "suspended": False,
        },
        index=[0],
    )
    if member_df.isna().values.any():
        return
    try:
        add_records_to_file(member_df, MEMBER_INFO)
    except ArrowIOError:
        PColor.pwarn("There was an issue accessing the database. Member was not added.")
        return
    PColor.pok(f"Member #{member_id} Added.")


def update_member_record() -> None:
    """
    Prompt the user to update the member's information.

    Prompts the user for a member ID, then prompts for which field to change.
    This prompt repeats until the user chooses to exit.
    """
    # prompt member ID
    # use load_records to get that member's info
    # display the info
    # use prompt_menu to ask which field to update
    # use prompt_str to get new value
    member_id = prompt_int("Member ID")
    member_record = load_records_from_file(
        MEMBER_INFO, eq_cols={"member_id": member_id}
    )
    if member_record.empty:
        # errror: no records found
        pass
    member_record = member_record.iloc[0]

    print("Here are the member's current values")
    options = []
    for field in member_record.index.values[1:]:
        options.append(f"{field}: {member_record[field]}")
    selection = prompt_menu_options("Choose field to change", options)
    if selection is None:
        return
    field_to_update = selection[1]
    if field_to_update == "zipcode":
        new_value = prompt_int(f"New value for {field_to_update}")
    else:
        new_value = prompt_str(f"New value for {field_to_update}")

    update_record(member_id, MEMBER_INFO, **{field_to_update: new_value})


def remove_member_record() -> None:
    """
    Prompt the user to remove the member's information.

    Prompts the user for a member ID, then prompts for which field to remove.
    """
    raise NotImplementedError("remove_member_record")


def _generate_user_id(table_info: TableInfo) -> int:
    """
    Generate a unique 9 digit ID. ID's increment by 1.

    Returns-
        int: The generated ID.

    Raises-
        IndexError: ID limit exceeded.
    """
    df = load_records_from_file(table_info)
    if df.empty:
        return 1000000000

    id = df.iloc[:, 0]
    if not is_numeric_dtype(id):
        raise TypeError("Only integers are allowed.")

    max_id = id.max()
    if max_id >= 9999999999:
        raise IndexError("User Limit Exceeded.")
    return max_id + 1


def add_provider_record() -> None:
    """
    Manager is prompted to enter provider information.

    Provider information: name, street address, city, state, zip code, and email address.
    Provider number is generated from _generate_provider_id.

    This prompt repeats until the user chooses to exit.

    Raises-
        IndexError: Maximum number of providers exceeded
    """
    try:
        provider_id = _generate_user_id(USER_INFO)
    except IndexError:
        PColor.pfail("The maximum number of users has been reached. No new user added.")
        return

    provider_df = pd.DataFrame(
        {
            "id": provider_id,
            "type": 1,
            "name": prompt_str("Name", USER_INFO.character_limits["name"]),
            "address": prompt_str("Address", USER_INFO.character_limits["address"]),
            "city": prompt_str("City", USER_INFO.character_limits["city"]),
            "state": prompt_str("State", USER_INFO.character_limits["state"]),
            "zipcode": prompt_int("Zipcode", USER_INFO.character_limits["zipcode"]),
            "password_hash": bytes(0),
        },
        index=[0],
    )
    if provider_df.isna().values.any():
        return
    try:
        add_records_to_file(provider_df, USER_INFO)
    except ArrowIOError:
        PColor.pwarn(
            "There was an issue accessing the database. Provider was not added."
        )
        return
    # value / type errors are impossible due to checks during prompting.
    PColor.pok(f"Provider #{provider_id} Added.")


def update_provider_record() -> None:
    """
    Prompt the user to update the provider's information.

    Prompts the user for a provider ID, then prompts for which field to change.
    This prompt repeats until the user chooses to exit.
    """
    raise NotImplementedError("update_provider_record")


def remove_provider_record() -> None:
    """
    Prompt the user to remove the provider's information.

    Prompts the user for a provider ID, then prompts for which field to remove.
    This prompt repeats until the user chooses to exit.
    """
    raise NotImplementedError("remove_provider_record")


def add_provider_directory_record() -> None:
    """
    Manager is prompted to enter service information.

    This is the service information: service_id, service_name, price_dollars, and price_cents.

    This prompt repeats until the user chooses to exit.
    """
    raise NotImplementedError("add_provider_directory_record")


def update_provider_directory_record() -> None:
    """
    The manager is prompted for a service id to update, and a lookup is performed.

    This prompt repeats until the user chooses to exit.
    """
    raise NotImplementedError("update_provider_directory_record")


def remove_provider_directory_record() -> None:
    """
    Manager is prompted for a service id to be removed, and a lookup is performed.

    This prompt repeats until the user chooses to exit.
    """
    raise NotImplementedError("remove_provider_directory_record")


def generate_member_report() -> None:
    """
    Each member who has consulted a ChocAn provider during that week receives a list of services.

    This information will be sorted in order of service date.

    The report, which is also sent as an e-mail attachment, includes:
    Member name (25 characters).
    Member number (9 digits).
    Member street address (25 characters).
    Member city (14 characters).
    Member state (2 letters).
    Member zip code (5 digits).
    For each service provided, the following details are required:
    Date of service (MM-DD-YYYY).
    Provider name (25 characters).
    Service name (20 characters).
    """
    raise NotImplementedError("generate_member_report")


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
