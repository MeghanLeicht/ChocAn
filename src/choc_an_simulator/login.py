"""
Login Sub-System.

This module ensures secure access for providers and managers.
It includes functions for display the login menu, generating a secure password, secure password verification, and user type authorization.
"""
from .schemas import USER_INFO


def login_menu() -> None:
    """
    Display the user login menu.

    This function prompts the user for their ID (manager ID or provider ID) and password.
    """
    # use getpass.getpass() so the password is not typed on the screen.
    raise NotImplementedError("login_menu")


def generate_secure_password(password: str) -> (str, str):
    """
    Generates a secure user password.

    This function is used to hash/salt the user password.
    It returns the hash/salt password and the salt.
    """
    raise NotImplementedError("generate_secure_password")


def secure_password_verifiction(salt: str, hashed_password: str) -> bool:
    """
    Verifies the password entered by the user.

    Returns True or False if the password matches the database.
    """
    raise NotImplementedError("secure_password_verification")


def user_type_authorization() -> None:
    """
    Determines the user type based on the user ID.

    If the ID starts with a 0, then the user has manager authorization.
    If the ID starts with a 1, then the user has provider authorization.
    """
    raise NotImplementedError("user_type_authorization")