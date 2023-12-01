"""
Login Sub-System.

This module ensures secure access for providers and managers.
It includes functions for display the login menu, generating a secure password,
secure password verification, and user type authorization.
"""
import bcrypt

from choc_an_simulator.database_management import load_records_from_file
from choc_an_simulator.schemas import USER_INFO


def login_menu() -> None:
    """
    Display the user login menu.

    This function prompts the user for their ID (manager ID or provider ID) and password.
    """
    # use getpass.getpass() so the password is not typed on the screen.
    raise NotImplementedError("login_menu")


def generate_secure_password(password: str) -> (bytes, bytes):
    """
    Generates a secure user password.

    This function is used to hash/salt the user password.
    It returns the hash/salt password and the salt.
    """
    password = password.encode()
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt)
    return hashed_password, salt


def secure_password_verification(user_id: int, password: str) -> bool:
    """
    Verifies the password entered by the user.

    Returns True or False if the password matches the database.
    """
    pw = load_records_from_file(USER_INFO, eq_cols={"id": user_id})["password_hash"]
    return bcrypt.checkpw(pw, password.encode())


def user_type_authorization() -> None:
    """
    Determines the user type.

    If the user type = 0, then the user has manager authorization.
    If the user type = 1, then the user has provider authorization.
    """
    raise NotImplementedError("user_type_authorization")
