"""Tests of functions in the provider module."""
import pytest
import pandas as pd
import pyarrow as pa
import os
from choc_an_simulator.provider import (
    show_provider_menu,
    check_in_member,
    display_member_information,
    record_service_billing_entry,
    request_provider_directory,
)


@pytest.mark.parametrize(
    "option_text,endpoint_func_name",
    [
        (
            "Request Provider Directory",
            "choc_an_simulator.provider.request_provider_directory",
        ),
        ("Record a Service", "choc_an_simulator.provider.record_service_billing_entry"),
        ("Member Check-In", "choc_an_simulator.provider.check_in_member"),
    ],
)
@pytest.mark.usefixtures("assert_menu_endpoint")
def test_show_provider_menu(
    assert_menu_endpoint,
    endpoint_func_name: str,
    option_text: str,
):
    """Paramaterized test that show_provider_menu reaches the correct endpoints"""
    show_provider_menu()


def test_check_in_member():
    """Verify input validation & database lookups for check_in_member."""
    with pytest.raises(NotImplementedError):
        check_in_member()


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
    mock_df = pd.DataFrame({"service_id": [0, 1], "service_name": ["name 0", "name 1"]})

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

    saved_df = pd.read_csv(expected_save_path)
    assert saved_df.equals(mock_df)
    os.remove(expected_save_path)


def test_request_provider_directory_with_io_error(mocker, capsys) -> None:
    """Test request_provider_directory function with IO error"""
    mocker.patch(
        "choc_an_simulator.provider.load_records_from_file",
        side_effect=pa.ArrowIOError,
    )
    request_provider_directory()
    assert (
        "There was an error loading the provider directory." in capsys.readouterr().out
    )
