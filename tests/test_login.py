"""Tests of functions in the login module."""
from unittest.mock import patch

import pandas as pd
import pyarrow as pa
import pytest
from pyarrow import ArrowIOError

from choc_an_simulator.login import (
    generate_secure_password,
    login_menu,
    secure_password_verification,
    user_type_authorization,
)

CAS_LOG_PATH = "choc_an_simulator.login"


def mocked_user_and_hashed_pass(*args, **kwargs):
    """Fixture for user_id and hashed password."""
    df = pd.DataFrame(
        {
            "id": [940672921, 265608022],
            "type": [0, 1],  # 0 = manager, 1 = provider
            "name": [
                "Case Hall",
                "Regina George",
            ],
            "address": [
                "123 Main St",
                "456 Elm St",
            ],
            "city": [
                "Chicago",
                "New York",
            ],
            "state": ["IL", "NY"],
            "zipcode": [15603, 38322],
            "password_hash": pa.array(
                [
                    b"$2b$12$KFBJWHWo.cDZSL5yepRCIuQEBj1pdnOicNsfmL.Y/t3D9I0gdwmj6",  # password1
                    b"$2b$12$1ySuCH7I8OqOGS2T9O6/VeuCHqV3a.esMLK3JT.BPwOM/SOXrWG3m",
                    # Th1s1sTh3m0stS3cur3!
                ],
                type=pa.binary(),
            ),
        }
    )

    return df[df["id"] == kwargs["eq_cols"]["id"]]


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


def test_login_menu_correct_password_unknown_user_type(mocker, capsys):
    """Test that a user tried to log in with correct password."""
    expected = "\x1b[93mUser type not recognized.\x1b[0m\n"
    mocker.patch(f"{CAS_LOG_PATH}.prompt_int", return_value=123456789)
    mocker.patch(f"{CAS_LOG_PATH}.getpass.getpass", return_value="thisisapassword")
    mocker.patch(
        f"{CAS_LOG_PATH}.generate_secure_password",
        return_value=("hashedpassword123"),
    )
    mocker.patch(f"{CAS_LOG_PATH}.secure_password_verification", return_value=True)
    mocker.patch(f"{CAS_LOG_PATH}.user_type_authorization", return_value=5)

    login_menu()

    captured = capsys.readouterr()
    assert captured.out == expected


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


@pytest.mark.parametrize(
    "user_id, password",
    [
        (940672921, "password1"),
        (265608022, "Th1s1sTh3m0stS3cur3!"),
    ],
)
@patch(
    "choc_an_simulator.login.load_records_from_file",
    side_effect=mocked_user_and_hashed_pass,
)
def test_secure_password_verification(mock_load_records_from_file, user_id, password):
    """Verify that correct password is entered."""
    verified_user = secure_password_verification(user_id=user_id, password=password)

    assert verified_user is True


@patch("choc_an_simulator.login.load_records_from_file", return_value=pd.DataFrame())
def test_secure_password_verification_no_user(mock_load_records_from_file):
    """password verification fails if user does not exist."""
    verified_user = secure_password_verification(
        user_id=123456789, password="password1"
    )

    assert verified_user is False


@patch("choc_an_simulator.login.load_records_from_file", side_effect=ArrowIOError)
def test_secure_password_verification_db_error(mock_load_records_from_file, capsys):
    """Verify db error is printed to console."""
    expected = "\033[93mThere was an issue accessing the database.\n\tError: \x1b[0m\n"
    secure_password_verification(user_id=123456789, password="password1")
    captured = capsys.readouterr()
    assert captured.out == expected


@pytest.mark.parametrize(
    "user_id, expected_type",
    [
        (940672921, 0),
        (265608022, 1),
    ],
)
@patch(
    "choc_an_simulator.login.load_records_from_file",
    side_effect=mocked_user_and_hashed_pass,
)
def test_user_type_authorization(mock_load_records_from_file, user_id, expected_type):
    """Verify that user exists and corresponds to the correct user type."""
    returned_user_type = user_type_authorization(user_id=user_id)
    assert returned_user_type.__eq__(expected_type)


@patch("choc_an_simulator.login.load_records_from_file", side_effect=ArrowIOError)
def test_user_type_authorization_db_error(mock_load_records_from_file, capsys):
    """Verify db error is printed to console."""
    expected = "\033[93mThere was an issue accessing the database.\n\tError: \x1b[0m\n"
    user_type_authorization(user_id=123456789)
    captured = capsys.readouterr()
    assert captured.out == expected
