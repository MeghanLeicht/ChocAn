"""Tests of functions in the manager module."""

import pytest
import pandas as pd
import pyarrow as pa
from choc_an_simulator.manager import (
    _generate_user_id,
    _prompt_member_options,
    _prompt_provider_options,
    _prompt_provider_directory_options,
    _prompt_report_options,
    manager_menu,
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
    """Paramaterized test that manager_menu reaches the correct endpoints"""
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
):
    """Paramaterized test that _prompt_member_options reaches the correct endpoints"""
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
):
    """Paramaterized test that _prompt_provider_options reaches the correct endpoints"""
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
):
    """Paramaterized test that _prompt_provider_directory_options reaches the correct endpoints"""
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
):
    """Paramaterized test that _prompt_report_options reaches the correct endpoints"""
    _prompt_report_options()


class TestGenerateUserID:
    """Tests of the _generate_user_id function"""

    @pytest.mark.parametrize(
        "existing_ids",
        [
            # First valid ID
            [1000000000],
            # Second to last valid ID
            [9999999998],
            # Empty
            [],
        ],
    )
    def test_generate_user_id_valid(self, mocker, existing_ids):
        """Test generating a valid user ID"""
        mocker.patch(
            "choc_an_simulator.manager.load_records_from_file",
            return_value=pd.DataFrame({"id": existing_ids}),
        )
        # print(load_records_from_file(None))
        new_id = _generate_user_id()
        assert new_id == max(existing_ids, default=999999999) + 1

    def test_generate_user_id_out_of_range(self, mocker, capsys):
        """Test generating a user ID that exceeds the max value"""
        mocker.patch(
            "choc_an_simulator.manager.load_records_from_file",
            return_value=pd.DataFrame({"id": [9999999999]}),
        )
        with pytest.raises(IndexError):
            _ = _generate_user_id()


def test_add_member_record():
    """Test of the add_member_record function."""
    with pytest.raises(NotImplementedError):
        add_member_record()


def test_update_member_record():
    """Test of the update_member_record function."""
    with pytest.raises(NotImplementedError):
        update_member_record()


def test_remove_member_record():
    """Test of the remove_member_record function."""
    with pytest.raises(NotImplementedError):
        remove_member_record()


class TestAddProviderRecord:
    """Tests of the add_provider_record function"""

    @pytest.mark.parametrize(
        "input_strs", [["Donald", "1234 NE Street st.", "Portland", "OR", "97212"]]
    )
    @pytest.mark.usefixtures("mock_input_series")
    def test_add_provider_record_valid(self, mocker, mock_input_series):
        """Test of the add_provider_record function with valid input"""
        mocker.patch("choc_an_simulator.manager.add_records_to_file", return_value=None)
        add_provider_record()

    @pytest.mark.parametrize(
        "input_strs", [["Donald", "1234 NE Street st.", "Portland", "OR", "97212"]]
    )
    @pytest.mark.usefixtures("mock_input_series")
    def test_add_provider_record_io_error(self, mocker, mock_input_series, capsys):
        """Test of the add_provider_record function with an IO error"""
        mocker.patch(
            "choc_an_simulator.manager.add_records_to_file",
            side_effect=pa.ArrowIOError,
        )
        add_provider_record()
        assert (
            "There was an issue accessing the database. Provider was not added."
            in capsys.readouterr().out
        )

    @pytest.mark.usefixtures("mock_input_ctrl_c")
    def test_add_provider_record_user_exit(self, mocker, mock_input_ctrl_c, capsys):
        """Test of the add_provider_record function with user exit."""
        mock_add_records = mocker.patch("choc_an_simulator.manager.add_records_to_file")
        add_provider_record()
        mock_add_records.assert_not_called()

    def test_add_provider_record_bad_user_id(self, mocker, capsys):
        """
        Test of the add_provider_record function when the system has reached the maximum
        number of providers.
        """
        mocker.patch(
            "choc_an_simulator.manager._generate_user_id",
            side_effect=IndexError,
        )
        add_provider_record()
        assert "No new user added." in capsys.readouterr().out


def test_update_provider_record():
    """Test of the update_provider_record function."""
    with pytest.raises(NotImplementedError):
        update_provider_record()


def test_remove_provider_record():
    """Test of the remove_provider_record function."""
    with pytest.raises(NotImplementedError):
        remove_provider_record()


def test_add_provider_directory_record():
    """Test of the add_provider_directory_record function."""
    with pytest.raises(NotImplementedError):
        add_provider_directory_record()


def test_update_provider_directory_record():
    """Test of the update_provider_directory_record function."""
    with pytest.raises(NotImplementedError):
        update_provider_directory_record()


class TestRemoveProviderDirectoryRecord:
    """Test of the remove_provider_directory_record function."""

    def test_remove_provider_directory_io_error(self, mocker, capsys) -> None:
        """Test remove_provider_directory_record function with load IO error."""
        mocker.patch(
            "choc_an_simulator.manager.remove_record",
            side_effect=pa.ArrowIOError,
        )
        remove_provider_directory_record()
        assert "Service was not removed!" in capsys.readouterr().out


def test_generate_member_report():
    """Test of the generate_member_report function."""
    with pytest.raises(NotImplementedError):
        generate_member_report()


def test_generate_provider_report():
    """Test of the generate_provider_report function."""
    with pytest.raises(NotImplementedError):
        generate_provider_report()


def test_generate_summary_report():
    """Test of the generate_summary_report function."""
    with pytest.raises(NotImplementedError):
        generate_summary_report()
