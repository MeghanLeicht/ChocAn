"""Tests of functions in the manager module."""
import pytest
from choc_an_simulator.manager import (
    manager_menu,
    _prompt_member_options,
    _prompt_provider_options,
    _prompt_provider_directory_options,
    _prompt_report_options,
    add_member_record,
    update_member_record,
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

CAS_MGR_PATH = "choc_an_simulator.manager"


@pytest.mark.parametrize(
    "option_text,endpoint_func_name",
    [
        ("Member", f"{CAS_MGR_PATH}._prompt_member_options"),
        ("Provider", f"{CAS_MGR_PATH}._prompt_provider_options"),
        ("Provider Directory", f"{CAS_MGR_PATH}._prompt_provider_directory_options"),
        ("Reports", f"{CAS_MGR_PATH}._prompt_report_options"),
    ],
)
@pytest.mark.usefixtures("assert_menu_endpoint")
def test_manager_menu(
    assert_menu_endpoint,
):
    manager_menu()


@pytest.mark.parametrize(
    "option_text,endpoint_func_name",
    [
        ("Add", f"{CAS_MGR_PATH}.add_member_record"),
        ("Update", f"{CAS_MGR_PATH}.update_member_record"),
        ("Remove", f"{CAS_MGR_PATH}.remove_member_record"),
    ],
)
@pytest.mark.usefixtures("assert_menu_endpoint")
def test_prompt_member_options(
    assert_menu_endpoint,
    endpoint_func_name: str,
    option_text: str,
):
    _prompt_member_options()


@pytest.mark.parametrize(
    "option_text,endpoint_func_name",
    [
        ("Add", f"{CAS_MGR_PATH}.add_provider_record"),
        ("Update", f"{CAS_MGR_PATH}.update_provider_record"),
        ("Remove", f"{CAS_MGR_PATH}.remove_provider_record"),
    ],
)
@pytest.mark.usefixtures("assert_menu_endpoint")
def test_prompt_provider_options(
    assert_menu_endpoint,
    endpoint_func_name: str,
    option_text: str,
):
    _prompt_provider_options()


@pytest.mark.parametrize(
    "option_text,endpoint_func_name",
    [
        ("Add", f"{CAS_MGR_PATH}.add_provider_directory_record"),
        ("Update", f"{CAS_MGR_PATH}.update_provider_directory_record"),
        ("Remove", f"{CAS_MGR_PATH}.remove_provider_directory_record"),
    ],
)
@pytest.mark.usefixtures("assert_menu_endpoint")
def test_prompt_provider_directory_options(
    assert_menu_endpoint,
    endpoint_func_name: str,
    option_text: str,
):
    _prompt_provider_directory_options()


@pytest.mark.parametrize(
    "option_text,endpoint_func_name",
    [
        ("Member", f"{CAS_MGR_PATH}.generate_member_report"),
        ("Provider", f"{CAS_MGR_PATH}.generate_provider_report"),
        ("Summary", f"{CAS_MGR_PATH}.generate_summary_report"),
    ],
)
@pytest.mark.usefixtures("assert_menu_endpoint")
def test_prompt_report_options(
    assert_menu_endpoint,
    endpoint_func_name: str,
    option_text: str,
):
    _prompt_report_options()


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


def test_update_member_record():
    with pytest.raises(NotImplementedError):
        update_member_record()


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
