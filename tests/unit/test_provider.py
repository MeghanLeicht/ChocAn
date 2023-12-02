"""Tests of functions in the provider module."""
import pytest
import pandas as pd
from pandas import DataFrame, read_csv
import pyarrow as pa
import os
from datetime import datetime
from choc_an_simulator.provider import (
    show_provider_menu,
    check_in_member,
    display_member_information,
    record_service_billing_entry,
    request_provider_directory,
)
from definitions import PROVIDER_DIR_CSV
from choc_an_simulator.provider import (
    SERVICE_LOG_INFO,
    PROVIDER_DIRECTORY_INFO,
    MEMBER_INFO,
    USER_INFO,
)
from pyarrow import ArrowIOError

CAS_PVDR_PATH = "choc_an_simulator.provider"


@pytest.mark.parametrize(
    "option_text,endpoint_func_name",
    [
        ("Request Provider Directory", f"{CAS_PVDR_PATH}.request_provider_directory"),
        ("Record a Service", f"{CAS_PVDR_PATH}.record_service_billing_entry"),
        ("Member Check-In", f"{CAS_PVDR_PATH}.check_in_member"),
    ],
)
@pytest.mark.usefixtures("assert_menu_endpoint")
def test_show_provider_menu(
    assert_menu_endpoint,
):
    """Paramaterized test that show_provider_menu reaches the correct endpoints"""
    show_provider_menu()


@pytest.mark.parametrize(
    "member_info,member_id,expected_out",
    [
        # Valid Member
        (
            DataFrame(
                {
                    "member_id": [123456789],
                    "name": ["Name"],
                    "address": ["Street"],
                    "city": ["Portland"],
                    "state": ["OR"],
                    "zipcode": [97211],
                    "suspended": [False],
                }
            ),
            123456789,
            "\033[92mValid\033[0m\n",
        ),
        # Suspended Member
        (
            DataFrame(
                {
                    "member_id": [123456789],
                    "name": ["Name"],
                    "address": ["Street"],
                    "city": ["Portland"],
                    "state": ["OR"],
                    "zipcode": [97211],
                    "suspended": [True],
                }
            ),
            123456789,
            "\033[93mSuspended\033[0m\n",
        ),
        # Invalid Member
        (DataFrame(), 123456789, "\033[91mInvalid\033[0m\n"),
    ],
)
def test_check_in_member(member_info, member_id, expected_out, capsys, mocker):
    """Tests the check_in_member function."""
    mocker.patch("choc_an_simulator.provider.prompt_int", return_value=member_id)
    mocker.patch(
        "choc_an_simulator.provider.load_records_from_file", return_value=member_info
    )
    check_in_member()
    captured_out, _ = capsys.readouterr()
    assert captured_out == expected_out


def test_display_member_information():
    """Verify input validation & database lookups for display_member_information."""
    with pytest.raises(NotImplementedError):
        display_member_information()


@pytest.mark.parametrize(
    "member_id, provider_id, user_input, service_code, expected_output, raise_error_at, raise_add_records_error",
    [
        (
            111111111,
            222222222,
            ["Yes", "Test comment"],
            555555,
            "Service Billing Entry Recorded Successfully",
            None,
            False,
        ),
        (
            111111111,
            111111111,
            ["yes", "Test comment"],
            555555,
            "Invalid Provider ID",
            None,
            False,
        ),
        (
            111111111,
            222222222,
            ["No", "Test comment"],
            555555,
            "Service Not Confirmed",
            None,
            False,
        ),
        (
            111111111,
            222222222,
            ["yes", "Test comment"],
            555555,
            "Service Confirmed",
            None,
            False,
        ),
        (
            111111111,
            222222222,
            ["yes", "Test comment"],
            555555,
            "Service Fee: $100.50",
            None,
            False,
        ),
        (
            111111111,
            222222222,
            ["yes", "Test comment"],
            999999,
            "Invalid Service Code",
            None,
            False,
        ),
        (
            222222222,
            222222222,
            ["yes", "Test comment"],
            555555,
            "Invalid Member ID or Member Suspended",
            None,
            False,
        ),
        (
            111111111,
            222222222,
            ["yes", "Test comment"],
            555555,
            "Failed to load member information from the file",
            "members",
            False,
        ),
        (
            111111111,
            222222222,
            ["yes", "Test comment"],
            555555,
            "Failed to load user information from the file",
            "providers",
            False,
        ),
        (
            111111111,
            222222222,
            ["yes", "Test comment"],
            555555,
            "Failed to load provider directory information from the file",
            "services",
            False,
        ),
        (
            111111111,
            222222222,
            ["yes", "Test comment"],
            555555,
            "Failed to add service log information to the file",
            "log",
            True,
        ),
        (
            111111111,
            222222222,
            ["Yes", None],
            555555,
            "Service Billing Entry Recorded Successfully",
            None,
            False,
        ),
        (
            111111111,
            222222222,
            [None, "Test comment"],
            555555,
            "Service Not Confirmed",
            None,
            False,
        ),
    ],
)
def test_record_service_billing(
    mocker,
    capsys,
    member_id,
    provider_id,
    user_input,
    service_code,
    expected_output,
    raise_error_at,
    raise_add_records_error,
):
    """
    Test the record_service_billing_entry function with a range of inputs and scenarios.

    This includes testing normal operation as well as error handling for failed data loading and saving.

    Args:
        mocker: Pytest fixture for mocking dependencies.
        capsys: Pytest fixture for capturing stdout and stderr.
        member_id, provider_id, user_input, service_code: Input parameters for the test.
        expected_output: The expected output string to verify correct function behavior.
        raise_error_at: Specifies at which point to simulate a data loading error.
        raise_add_records_error: Boolean indicating whether to simulate an error in data saving.
    """
    # Predefined dataframes to return for successful data loading operations
    dataframes_to_return = [
        # Member information dataframe
        pd.DataFrame({"member_id": [member_id]}),
        # Provider information dataframe
        pd.DataFrame({"id": [provider_id]}),
        # Service information dataframe
        pd.DataFrame(
            {
                "service_id": [555555],
                "service_name": ["Test service"],
                "price_dollars": [100],
                "price_cents": [50],
            }
        ),
    ]

    # Simulate data loading errors based on the raise_error_at parameter
    def dataframes_side_effect(*args, **kwargs):
        if raise_error_at == "members" and args[0] == MEMBER_INFO:
            raise ArrowIOError("Failed to load member information from the file")
        elif raise_error_at == "providers" and args[0] == USER_INFO:
            raise ArrowIOError("Failed to load user information from the file")
        elif raise_error_at == "services" and args[0] == PROVIDER_DIRECTORY_INFO:
            raise ArrowIOError(
                "Failed to load provider directory information from the file"
            )
        elif raise_error_at == "log" and args[0] == SERVICE_LOG_INFO:
            raise ArrowIOError("Failed to add service log information to the file")
        return dataframes_to_return.pop(0)

    # Mock the add_records_to_file function to simulate errors in data saving if required
    if raise_add_records_error:
        mocker.patch(
            "choc_an_simulator.provider.add_records_to_file",
            side_effect=ArrowIOError(
                "Failed to add service log information to the file"
            ),
        )
    else:
        mocker.patch("choc_an_simulator.provider.add_records_to_file")

    # Mocking user inputs and the function that loads data from files
    mocker.patch("choc_an_simulator.provider.prompt_str", side_effect=user_input)
    mocker.patch(
        "choc_an_simulator.provider.prompt_int",
        side_effect=[111111111, 222222222, service_code],
    )
    mocker.patch(
        "choc_an_simulator.provider.prompt_date",
        return_value=datetime.strptime("11-26-2023", "%m-%d-%Y"),
    )
    mocker.patch(
        "choc_an_simulator.provider.load_records_from_file",
        side_effect=dataframes_side_effect,
    )

    record_service_billing_entry()

    # Capture the stdout and stderr
    captured = capsys.readouterr()
    captured_output = captured.out

    # Check for the expected output
    assert expected_output in captured_output


def test_request_provider_directory(mocker, capsys) -> None:
    """Verify correct file creation for request_provider_directory and output of filepath"""
    expected_save_path = PROVIDER_DIR_CSV

    mock_df = DataFrame({"service_id": [0, 1], "service_name": ["name 0", "name 1"]})

    mocker.patch(
        "choc_an_simulator.provider.load_records_from_file",
        return_value=mock_df,
    )

    request_provider_directory()

    assert os.path.exists(expected_save_path)

    captured = capsys.readouterr()
    expected_output = expected_save_path + "\n"
    assert expected_output in captured.out.replace(
        os.path.sep, "/"
    ), f"file path not found in captured output: {captured.out}"

    saved_df = read_csv(expected_save_path)
    assert saved_df.equals(mock_df)
    os.remove(expected_save_path)


def test_request_provider_directory_with_load_io_error(mocker, capsys) -> None:
    """Test request_provider_directory function with load IO error"""
    mocker.patch(
        "choc_an_simulator.provider.load_records_from_file",
        side_effect=pa.ArrowIOError,
    )
    request_provider_directory()
    assert (
        "There was an error loading the provider directory." in capsys.readouterr().out
    )


def test_request_provider_directory_with_save_io_error(mocker, capsys) -> None:
    """Test request_provider_directory function with save IO error"""
    mocker.patch(
        "choc_an_simulator.provider.save_report",
        side_effect=IOError,
    )
    request_provider_directory()
    assert (
        "There was an error saving the provider directory report."
        in capsys.readouterr().out
    )
