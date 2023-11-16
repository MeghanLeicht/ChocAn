"""Tests of functions in the provider module."""
import pytest
from choc_an_simulator.provider import show_provider_menu


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
