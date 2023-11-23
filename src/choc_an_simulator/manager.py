"""
Manager Sub-System.

The manager sub-system allows managers to manage member, provider, and provider directory records.
"""
import pandas as pd
from pyarrow import ArrowIOError
from .database_management import load_records_from_file, add_records_to_file
from .schemas import USER_INFO
from .user_io import prompt_str, prompt_int, PColor


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
    raise NotImplementedError("manager_menu")


def add_member_record() -> None:
    """
    Manager is prompted to enter member information.

    The required member information: name, street address, city, state, zip code, and email address.
    The member number will be generated from _generate_member_id().

    This prompt repeats until the user chooses to exit.
    """
    raise NotImplementedError("add_member_record")


def update_member_record() -> None:
    """
    Prompt the user to update the member's information.

    Prompts the user for a member ID, then prompts for which field to change.
    This prompt repeats until the user chooses to exit.
    """
    raise NotImplementedError("update_member_record")


def remove_member_record() -> None:
    """
    Prompt the user to remove the member's information.

    Prompts the user for a member ID, then prompts for which field to remove.

    This prompt repeats until the user chooses to exit.
    """
    raise NotImplementedError("remove_member_record")


def _generate_user_id(id_prefix: int) -> int:
    """
    Generate a unique 11-digit user ID, with the given id_prefix as the leftmost digit.

    ID's increment by 1 with each new user.

    Args-
        id_prefix(int): The first digit of the user ID. Current supported prefixes:
            1: Provider
            2: Manager

    Returns-
        The generated ID

    Raises-
        IndexError: User ID limit exceeded.
    """
    assert 1 <= id_prefix <= 9, "ID prefix must be a single digit greater than 0."
    providers_df = load_records_from_file(USER_INFO)
    first_id = id_prefix * pow(10, USER_INFO.character_limits["id"].stop - 1)
    last_id = first_id + pow(10, USER_INFO.character_limits["id"].stop - 1)
    # Get all current ID's in the database with the given prefix
    ids_with_prefix = providers_df[
        (first_id <= providers_df["id"]) | (providers_df["id"] <= last_id)
    ]["id"]
    if ids_with_prefix.empty:
        return first_id
    new_user_id = ids_with_prefix.max() + 1

    if new_user_id >= (id_prefix + 1) * id_prefix * pow(
        10, USER_INFO.character_limits["id"].stop - 1
    ):
        raise IndexError(f"Maxumum users reached for ID prefix {id_prefix}")

    return new_user_id


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
        provider_id = _generate_user_id(1)
    except IndexError as err_index:
        raise err_index

    provider_df = pd.DataFrame(
        {
            "id": provider_id,
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
