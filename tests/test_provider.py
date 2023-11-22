"""Tests of functions in the provider module."""
import pytest
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


def test_request_provider_directory() -> None:
    """Verify correct file creation for request_provider_directory."""
    with pytest.raises(NotImplementedError):
        request_provider_directory()
