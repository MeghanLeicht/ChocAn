"""
Login Sub-System.

This module ensures secure access for providers and managers.
It includes functions for display the login menu, generating a secure password,
secure password verification, and user type authorization.
"""
import bcrypt
import pyarrow as pa
from choc_an_simulator.database_management import load_records_from_file
from choc_an_simulator.schemas import USER_INFO
from .user_io import PColor, prompt_int
from .manager import manager_menu
from .provider import show_provider_menu
import getpass


def login_menu() -> None:
    """
    Display the user login menu.

    This function prompts the user for their ID (manager ID or provider ID) and password.
    """
    user_verified = False
    user_id = None

    while user_verified is False:
        user_id = prompt_int("User ID")

        if user_id is None:
            return None

        try:
            user_verified = secure_password_verification(
                user_id, getpass.getpass(prompt="Password: ")
            )
        except KeyboardInterrupt:
            return None

        if user_verified is False:
            print("Password is incorrect. Try again.")
            continue

    match user_type_authorization(user_id):
        case 0:
            manager_menu()
        case 1:
            show_provider_menu()
        case _:
            PColor.pwarn("User type not recognized.")


def generate_secure_password(password: str) -> (bytes, bytes):
    """
    Generates a secure user password.

    This function is used to hash/salt the user password.
    It returns the hash/salt password and the salt.

    Returns the number of bytes and str of the secure password.
    """
    password = password.encode()
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt)
    return hashed_password, salt


def secure_password_verification(user_id: int, password: str) -> bool:
    """
    Verifies the password entered by the user.

    Returns True or False if the password and user ID matches the database.
    """
    try:
        pw = load_records_from_file(USER_INFO, eq_cols={"id": user_id})
        if pw.empty:
            return False
        pw = pw["password_hash"].iloc[0]
    except pa.ArrowIOError as err_io:
        PColor.pwarn(f"There was an issue accessing the database.\n\tError: {err_io}")
        return False

    return bcrypt.checkpw(password.encode(), pw)


def user_type_authorization(user_id: int) -> int:
    """
    Determines the user type.

    If the user type = 0, then the user has manager authorization.
    If the user type = 1, then the user has provider authorization.

    Returns an integer of the user_type.
    """
    try:
        user_type = load_records_from_file(USER_INFO, eq_cols={"id": user_id})["type"]
    except pa.ArrowIOError as err_io:
        PColor.pwarn(f"There was an issue accessing the database.\n\tError: {err_io}")
        return False

    return user_type.iloc[0]
