"""Tests of functions in the login module."""
import pytest

from choc_an_simulator.login import (
    login_menu,
    generate_secure_password,
    secure_password_verifiction,
    user_type_authorization,
)


def test_login_menu(mocker, capsys):
    """Test that a user tried to login with correct password."""
    mocker.patch(
       "choc_an_simulator.login.prompt_int",
       return_value="123456789" 
    )
    mocker.patch(
        "choc_an_simulator.login.getpass.getpass",
        return_value="thisisapassword"
    )
    mocker.patch(
        "choc_an_simulator.login.generate_secure_password",
        return_value=("salt123", "hashedpassword123")
        )
    mocker.patch(
        "choc_an_simulator.login.secure_password_verifiction",
        return_value=True
    )
    mocker.patch("choc_an_simulator.login.user_type_authorization")

    login_menu()


def test_login_menu_incorrect_password(mocker, capsys):
    """Test that a user tried to login with incorrect password."""
    mocker.patch(
       "choc_an_simulator.login.prompt_int",
       return_value="123456789" 
    )
    mocker.patch(
        "choc_an_simulator.login.getpass.getpass",
        return_value="thisisapassword"
    )
    mocker.patch(
        "choc_an_simulator.login.generate_secure_password",
        return_value=("salt123", "hashedpassword123")
        )
    mocker.patch(
        "choc_an_simulator.login.secure_password_verifiction",
        return_value=False
    )
    mocker.patch("choc_an_simulator.login.user_type_authorization")

    # KeyboardInterrupt after first attempt
    mocker.patch(
        "choc_an_simulator.login.secure_password_verifiction",
        side_effect=[False, KeyboardInterrupt],
    )

    login_menu()

    captured = capsys.readouterr()
    expected_output = "Password is incorrect. Try again."
    assert (
        expected_output in captured.out
    )


def test_login_menu_with_os_error(mocker, capsys):
    """Test login_menu function with save OS error"""
    mocker.patch(
       "choc_an_simulator.login.prompt_int",
       side_effect=OSError,
    )
    login_menu()
    assert(
        "There was an error with that user ID."
        in capsys.readouterr().out
    )



def test_generate_secure_password():
    """Verify that a secure password is generated."""
    with pytest.raises(NotImplementedError):
        generate_secure_password(password="thisisapassword")

def test_secure_password_verifiction():
    """Verify that correct password is entered."""
    with pytest.raises(NotImplementedError):
        secure_password_verifiction(salt='salt123', hashed_password='hashedpassword123')

def test_user_type_authorization():
    """Verify that user exists and corresponds to the correct user type."""
    with pytest.raises(NotImplementedError):
        user_type_authorization(user_id=123456789)