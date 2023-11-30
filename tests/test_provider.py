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

@pytest.mark.parametrize("provider_id, user_input, expected_output", [
    (123123123, ["yes", "Test comment"], "Service Billing Entry Recorded Successfully"),
    (111111111, ["yes", "Test comment"], "Invalid Provider ID"),
    (123123123, ["no", "Test comment"], "Service Not Confirmed"),
    (123123123, ["yes", "Test comment"], "Service Confirmed"),
    (123123123, ["yes", "Test comment"], "Service Fee: $100.50")
])
def test_record_service_billing(mocker, capsys, provider_id, user_input, expected_output):
    """Test record service billing with all possible inputs"""
    dataframes_to_return = [
        pd.DataFrame({"provider_id": [provider_id]}),
        pd.DataFrame({
            "service_id": [555555],
            "service_name": ["Test service"],
            "price_dollars": [100],
            "price_cents": [50],
        })
    ]

    def side_effect(*args, **kwargs):
        return dataframes_to_return.pop(0)

    mocker.patch("choc_an_simulator.provider.add_records_to_file")
    mocker.patch("choc_an_simulator.provider.prompt_str", side_effect=user_input)
    mocker.patch("choc_an_simulator.provider.prompt_int", side_effect=[123123123, 555555])
    mocker.patch(
        "choc_an_simulator.provider.prompt_date",
        return_value=datetime.strptime("11-26-2023", "%m-%d-%Y"),
    )
    mocker.patch("choc_an_simulator.provider.load_records_from_file", side_effect=side_effect)

    record_service_billing_entry(1233456789)

    captured = capsys.readouterr()
    assert expected_output in captured.out

def test_request_provider_directory(mocker, capsys) -> None:
    """Verify correct file creation for request_provider_directory and output of filepath"""
    expected_save_path = "src/choc_an_simulator/reports/provider_directory.csv"
    mock_df = DataFrame({"service_id": [0, 1], "service_name": ["name 0", "name 1"]})

    mocker.patch(
        "choc_an_simulator.provider.load_records_from_file",
        return_value=mock_df,
    )

    request_provider_directory()

    assert os.path.exists(expected_save_path)

    captured = capsys.readouterr()
    expected_output = expected_save_path + "\n"
    assert (
        expected_output in captured.out
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
