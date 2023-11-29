"""Tests of functions in the provider module."""
import pytest
from pandas import DataFrame, read_csv
import pyarrow as pa
import os
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
    mocker.patch("choc_an_simulator.provider.load_records_from_file", return_value=member_info)
    check_in_member()
    captured_out, _ = capsys.readouterr()
    assert captured_out == expected_out


def test_display_member_information():
    """Verify input validation & database lookups for display_member_information."""
    with pytest.raises(NotImplementedError):
        display_member_information()


def test_record_service_billing_entry():
    """Verify input validation & database lookups / additions for record_service_billing_entry."""
    with pytest.raises(NotImplementedError):
        record_service_billing_entry()


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
    assert "There was an error loading the provider directory." in capsys.readouterr().out


def test_request_provider_directory_with_save_io_error(mocker, capsys) -> None:
    """Test request_provider_directory function with save IO error"""
    mocker.patch(
        "choc_an_simulator.provider.save_report",
        side_effect=IOError,
    )
    request_provider_directory()
    assert "There was an error saving the provider directory report." in capsys.readouterr().out
