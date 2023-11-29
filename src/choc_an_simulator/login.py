"""
Login Sub-System.

This module ensures secure access for providers and managers.
It includes functions for display the login menu, generating a secure password,
secure password verification, and user type authorization.
"""
from .user_io import prompt_int, PColor
import getpass


def login_menu() -> None:
    """
    Display the user login menu.

    This function prompts the user for their ID (manager ID or provider ID) and password.
    """
    user_verified = False
    try:
        while user_verified is False:
            try:
                user_id = prompt_int("User ID")
            except OSError:
                print()
                return
            
            hashed_password = generate_secure_password(
                getpass.getpass(prompt="Password: ")
            )

            user_verified = secure_password_verifiction(
                hashed_password[0], hashed_password[1]
            )
            if user_verified is False:
                print("Password is incorrect. Try again.")
    except KeyboardInterrupt:
        return None

    user_type_authorization(user_id)
    


def generate_secure_password(password: str) -> (bytes, str):
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


def user_type_authorization(user_id: int) -> None:
    """
    Determines the user type.

    If the user type = 0, then the user has manager authorization.
    If the user type = 1, then the user has provider authorization.
    """
    raise NotImplementedError("user_type_authorization")
