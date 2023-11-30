"""Tests of functions in the login module."""
import pytest

from choc_an_simulator.login import (
    login_menu,
    generate_secure_password,
    secure_password_verifiction,
    user_type_authorization,
)

CAS_LOG_PATH = "choc_an_simulator.login"


@pytest.mark.parametrize(
    "user_type,endpoint_func_name",
    [
        (0, f"{CAS_LOG_PATH}.manager_menu"),
        (1, f"{CAS_LOG_PATH}.show_provider_menu"),
    ],
)
def test_login_menu_correct_password(user_type, endpoint_func_name, mocker):
    """Test that a user tried to login with correct password."""
    mocker.patch(f"{CAS_LOG_PATH}.prompt_int", return_value=123456789)
    mocker.patch(f"{CAS_LOG_PATH}.getpass.getpass", return_value="thisisapassword")
    mocker.patch(
        f"{CAS_LOG_PATH}.generate_secure_password",
        return_value=("salt123", "hashedpassword123"),
    )
    mocker.patch(f"{CAS_LOG_PATH}.secure_password_verifiction", return_value=True)
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
        return_value=("salt123", "hashedpassword123"),
    )
    mocker.patch(f"{CAS_LOG_PATH}.secure_password_verifiction", return_value=False)
    mocker.patch(f"{CAS_LOG_PATH}.user_type_authorization", return_value=0)

    # KeyboardInterrupt after first attempt
    mocker.patch(
        f"{CAS_LOG_PATH}.getpass.getpass", side_effect=[False, KeyboardInterrupt]
    )

    login_menu()

    captured = capsys.readouterr()
    expected_output = "Password is incorrect. Try again."
    assert expected_output in captured.out


def test_generate_secure_password():
    """Verify that a secure password is generated."""
    with pytest.raises(NotImplementedError):
        generate_secure_password(password="thisisapassword")


def test_secure_password_verifiction():
    """Verify that correct password is entered."""
    with pytest.raises(NotImplementedError):
        secure_password_verifiction(
            user_id=123456789, salt="salt123", hashed_password="hashedpassword123"
        )


def test_user_type_authorization():
    """Verify that user exists and corresponds to the correct user type."""
    with pytest.raises(NotImplementedError):
        user_type_authorization(user_id=123456789)
