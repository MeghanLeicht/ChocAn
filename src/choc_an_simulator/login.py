"""
Login Sub-System.

This module ensures secure access for providers and managers.
It includes functions for display the login menu, generating a secure password,
secure password verification, and user type authorization.
"""
import bcrypt

from choc_an_simulator.database_management import load_records_from_file
from choc_an_simulator.schemas import USER_INFO
from .user_io import prompt_int
from .manager import manager_menu
from .provider import show_provider_menu
import getpass


def login_menu() -> None:
    """
    Display the user login menu.

    This function prompts the user for their ID (manager ID or provider ID) and password.
    """
    user_verified = False

    while user_verified is False:
        user_id = prompt_int("User ID")

        if user_id is None:
            return None

        try:
            hashed_password = generate_secure_password(
                getpass.getpass(prompt="Password: ")
            )
        except KeyboardInterrupt:
            return None

        user_verified = secure_password_verifiction(user_id, hashed_password)

        if user_verified is False:
            print("Password is incorrect. Try again.")

    match user_type_authorization(user_id):
        case 0:
            manager_menu()
        case 1:
            show_provider_menu()


def generate_secure_password(password: str) -> str:
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


def secure_password_verifiction(user_id: int, password: str) -> bool:
    """
    Verifies the password entered by the user.

    Returns True or False if the password and user ID matches the database.
    """
    pw = load_records_from_file(USER_INFO, eq_cols={"id": user_id})["password_hash"]
    return bcrypt.checkpw(pw, password.encode())


def user_type_authorization(user_id: int) -> int:
    """
    Determines the user type.

    If the user type = 0, then the user has manager authorization.
    If the user type = 1, then the user has provider authorization.

    Returns an integer of the user_type.
    """
    raise NotImplementedError("user_type_authorization")
