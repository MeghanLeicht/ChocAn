"""Tests of functions in the manager module."""
import pytest
from choc_an_simulator.manager import (
    manager_menu,
    add_member_record,
    remove_member_record,
    add_provider_record,
    update_provider_record,
    remove_provider_record,
    add_provider_directory_record,
    update_provider_directory_record,
    remove_provider_directory_record,
    generate_member_report,
    generate_provider_report,
    generate_summary_report,
)


@pytest.mark.parametrize(
    "option_text,endpoint_func_name",
    [
        ("Member", "choc_an_simulator.manager._prompt_member_options"),
        # ("Provider"),
        # ("Provider Directory"),
        # ("Reports"),
    ],
)
@pytest.mark.usefixtures("assert_menu_endpoint")
def test_manager_menu(assert_menu_endpoint):
    manager_menu()


"""
        @pytest.mark.parametrize(
            "option_text,endpoint_func_name",
            [
                ("Add", "choc_an_simulator.manager.add_member_record"),
                ("Update", "choc_an_simulator.manager.update_member_record"),
                ("Remove", "choc_an_simulator.manager.remove_member_record"),
            ],
        )
        def test_member_option(
            assert_menu_endpoint,
            endpoint_func_name: str,
            option_text: str,
        ):
            manager_menu()

    elif menu_option == "Provider":

        @pytest.mark.parametrize(
            "option_text,endpoint_func_name",
            [
                ("Add", "choc_an_simulator.manager.add_provider_record"),
                ("Update", "choc_an_simulator.manager.update_provider_record"),
                ("Remove", "choc_an_simulator.manager.remove_provider_record"),
            ],
        )
        @pytest.mark.usefixtures("assert_menu_endpoint")
        def test_provider_option(
            assert_menu_endpoint,
            endpoint_func_name: str,
            option_text: str,
        ):
            manager_menu()

    elif menu_option == "Provider Directory":

        @pytest.mark.parametrize(
            "option_text,endpoint_func_name",
            [
                ("Add", "choc_an_simulator.manager.add_provider_directory_record"),
                (
                    "Update",
                    "choc_an_simulator.manager.update_provider_directory_record",
                ),
                (
                    "Remove",
                    "choc_an_simulator.manager.remove_provider_directory_record",
                ),
            ],
        )
        @pytest.mark.usefixtures("assert_menu_endpoint")
        def test_provider_directory_option(
            assert_menu_endpoint,
            endpoint_func_name: str,
            option_text: str,
        ):
            manager_menu()

    elif menu_option == "Reports":

        @pytest.mark.parametrize(
            "option_text,endpoint_func_name",
            [
                ("Member", "choc_an_simulator.manager.generate_member_report"),
                ("Provider", "choc_an_simulator.manager.generate_provider_report"),
                ("Summary", "choc_an_simulator.manager.generate_summary_report"),
            ],
        )
        @pytest.mark.usefixtures("assert_menu_endpoint")
        def test_reports_option(
            assert_menu_endpoint,
            endpoint_func_name: str,
            option_text: str,
        ):
            manager_menu()
"""


def test_add_member_record():
    with pytest.raises(NotImplementedError):
        add_member_record()


def test_remove_member_record():
    with pytest.raises(NotImplementedError):
        remove_member_record()


def test_add_provider_record():
    with pytest.raises(NotImplementedError):
        add_provider_record()


def test_update_provider_record():
    with pytest.raises(NotImplementedError):
        update_provider_record()


def test_remove_provider_record():
    with pytest.raises(NotImplementedError):
        remove_provider_record()


def test_add_provider_directory_record():
    with pytest.raises(NotImplementedError):
        add_provider_directory_record()


def test_update_provider_directory_record():
    with pytest.raises(NotImplementedError):
        update_provider_directory_record()


def test_remove_provider_directory_record():
    with pytest.raises(NotImplementedError):
        remove_provider_directory_record()


def test_generate_member_report():
    with pytest.raises(NotImplementedError):
        generate_member_report()


def test_generate_provider_report():
    with pytest.raises(NotImplementedError):
        generate_provider_report()


def test_generate_summary_report():
    with pytest.raises(NotImplementedError):
        generate_summary_report()
