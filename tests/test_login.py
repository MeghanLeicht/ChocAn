"""Tests of functions in the login module."""
from unittest.mock import patch
import pandas as pd
import pytest

from choc_an_simulator.login import (
    login_menu,
    generate_secure_password,
    secure_password_verification,
    user_type_authorization,
)

CAS_LOG_PATH = "choc_an_simulator.login"


@pytest.fixture
def mocked_user_and_hashed_pass():
    """Fixture for user_id and hashed password."""
    return pd.DataFrame(
        {
            "id": [123456789],
            "password_hash": [
                b'$2b$12$UizpVkSudADHFkX.ZiIS4O.rgNLmyjh9JCx9mr0l57SMIzMMMQ1qe'
            ]
        }
    )


@pytest.mark.parametrize(
    "user_type,endpoint_func_name",
    [
        (0, f"{CAS_LOG_PATH}.manager_menu"),
        (1, f"{CAS_LOG_PATH}.show_provider_menu"),
    ],
)
def test_login_menu_correct_password(user_type, endpoint_func_name, mocker):
    """Test that a user tried to log in with correct password."""
    mocker.patch(f"{CAS_LOG_PATH}.prompt_int", return_value=123456789)
    mocker.patch(f"{CAS_LOG_PATH}.getpass.getpass", return_value="thisisapassword")
    mocker.patch(
        f"{CAS_LOG_PATH}.generate_secure_password",
        return_value=("hashedpassword123"),
    )
    mocker.patch(f"{CAS_LOG_PATH}.secure_password_verification", return_value=True)
    mocker.patch(f"{CAS_LOG_PATH}.user_type_authorization", return_value=user_type)

    expected = mocker.patch(f"{endpoint_func_name}")

    login_menu()

    expected.assert_called()


def test_login_menu_incorrect_password(mocker, capsys):
    """Test that a user tried to login with incorrect password."""
    mocker.patch(f"{CAS_LOG_PATH}.prompt_int", return_value=123456789)
    mocker.patch(f"{CAS_LOG_PATH}.getpass.getpass", return_value="thisisapassword")
    mocker.patch(
        f"{CAS_LOG_PATH}.generate_secure_password",
        return_value=("hashedpassword123"),
    )
    mocker.patch(f"{CAS_LOG_PATH}.secure_password_verification", return_value=False)
    mocker.patch(f"{CAS_LOG_PATH}.user_type_authorization", return_value=0)

    # KeyboardInterrupt after first attempt
    mocker.patch(
        f"{CAS_LOG_PATH}.getpass.getpass", side_effect=[False, KeyboardInterrupt]
    )

    login_menu()

    captured = capsys.readouterr()
    expected_output = "Password is incorrect. Try again."
    assert expected_output in captured.out


def test_login_menu_user_id_none(mocker, capsys):
    """Test that the user did not enter a user_id"""
    mocker.patch(f"{CAS_LOG_PATH}.prompt_int", return_value=None)

    expected_ouput = login_menu()

    assert expected_ouput is None


def test_generate_secure_password():
    """Verify that a secure password is generated."""
    generate_secure_password(password="thisisapassword")


@patch("choc_an_simulator.login.load_records_from_file")
def test_secure_password_verification(mock_load_records_from_file, mocked_user_and_hashed_pass):
    """Verify that correct password is entered."""
    mock_load_records_from_file.return_value = mocked_user_and_hashed_pass
    secure_password_verification(
        user_id=123456789, password="hashedpassword123"
    )


@patch("choc_an_simulator.login.load_records_from_file", return_value=0)
def test_user_type_authorization():
    """Verify that user exists and corresponds to the correct user type."""
    user_type_authorization(user_id=123456789)
