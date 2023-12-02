"""Tests of functions in the manager module."""

import pandas as pd
import pyarrow as pa
import pytest

from choc_an_simulator.manager import (_prompt_member_options, _prompt_provider_directory_options,
                                       _prompt_provider_options, _prompt_report_options,
                                       add_member_record, add_provider_directory_record,
                                       add_provider_record, generate_unique_id, manager_menu,
                                       remove_member_record, remove_provider_directory_record,
                                       remove_provider_record, update_member_record,
                                       update_provider_directory_record, update_provider_record)
from choc_an_simulator.schemas import MEMBER_INFO, PROVIDER_DIRECTORY_INFO, USER_INFO

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
    """Parameterized test that manager_menu reaches the correct endpoints"""
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
    """Parameterized test that _prompt_member_options reaches the correct endpoints"""
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
    """Parameterized test that _prompt_provider_options reaches the correct endpoints"""
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
    """Parameterized test that _prompt_provider_directory_options reaches the correct endpoints"""
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
    """Parameterized test that _prompt_report_options reaches the correct endpoints"""
    _prompt_report_options()


class TestGenerateUniqueID:
    """Tests of the generate_unique_id function"""

    @pytest.mark.parametrize(
        "existing_ids,table_info",
        [
            # First valid ID
            ([1000000000], MEMBER_INFO),
            # Second to last valid ID
            ([9999999998], MEMBER_INFO),
            # Empty
            ([], MEMBER_INFO),
            # First valid ID
            ([1000000000], USER_INFO),
            # Second to last valid ID
            ([9999999998], USER_INFO),
            # Empty
            ([], USER_INFO),
            # First valid ID
            ([1000000000], PROVIDER_DIRECTORY_INFO),
            # Second to last valid ID
            ([9999999998], PROVIDER_DIRECTORY_INFO),
            # Empty
            ([], PROVIDER_DIRECTORY_INFO),
        ],
    )
    def test_generate_unique_id_valid(self, mocker, existing_ids, table_info):
        """Test generating a valid user ID"""
        mocker.patch(
            "choc_an_simulator.manager.load_records_from_file",
            return_value=pd.DataFrame({"id": existing_ids}),
        )
        # print(load_records_from_file(None))
        new_id = generate_unique_id(table_info)
        assert new_id == max(existing_ids, default=999999999) + 1

    @pytest.mark.parametrize(
        "table_info",
        [USER_INFO, MEMBER_INFO, PROVIDER_DIRECTORY_INFO],
    )
    def test_generate_unique_id_out_of_range(self, mocker, table_info):
        """Test generating a user ID that exceeds the max value"""
        mocker.patch(
            "choc_an_simulator.manager.load_records_from_file",
            return_value=pd.DataFrame({"id": [9999999999]}),
        )
        with pytest.raises(IndexError):
            _ = generate_unique_id(table_info)

    @pytest.mark.parametrize(
        "table_info",
        [USER_INFO, MEMBER_INFO, PROVIDER_DIRECTORY_INFO],
    )
    def test_generate_unique_id_nonnumeric_id(self, mocker, table_info):
        """Test generating a user ID that exceeds the max value"""
        mocker.patch(
            "choc_an_simulator.manager.load_records_from_file",
            return_value=pd.DataFrame({"id": ["hello"]}),
        )
        with pytest.raises(TypeError):
            _ = generate_unique_id(table_info)


class TestAddMemberRecord:
    """Tests of the add_member_record function"""

    @pytest.mark.parametrize(
        "input_strs", [["Donald", "1234 NE Street st.", "Portland", "OR", "97212"]]
    )
    @pytest.mark.usefixtures("mock_input_series")
    def test_add_member_record_valid(self, mocker, mock_input_series):
        """Test of the add_member_record function with valid input"""
        mocker.patch("choc_an_simulator.manager.add_records_to_file", return_value=None)
        add_member_record()

    @pytest.mark.parametrize(
        "input_strs", [["Donald", "1234 NE Street st.", "Portland", "OR", "97212"]]
    )
    @pytest.mark.usefixtures("mock_input_series")
    def test_add_member_record_io_error(self, mocker, mock_input_series, capsys):
        """Test of the add_member_record function with an IO error"""
        mocker.patch(
            "choc_an_simulator.manager.add_records_to_file",
            side_effect=pa.ArrowIOError,
        )
        add_member_record()
        assert (
                "There was an issue accessing the database. Member was not added."
                in capsys.readouterr().out
        )

    @pytest.mark.usefixtures("mock_input_ctrl_c")
    def test_add_member_record_user_exit(self, mocker, mock_input_ctrl_c, capsys):
        """Test of the add_member_record function with user exit."""
        mock_add_records = mocker.patch("choc_an_simulator.manager.add_records_to_file")
        add_member_record()
        mock_add_records.assert_not_called()

    def test_add_member_record_bad_user_id(self, mocker, capsys):
        """
        Test of the add_member_record function when the system has reached the maximum
        number of members.
        """
        mocker.patch(
            "choc_an_simulator.manager.generate_unique_id",
            side_effect=IndexError,
        )
        add_member_record()
        assert "No new member added." in capsys.readouterr().out


@pytest.fixture
def test_member_info():
    return pd.DataFrame(
        {
            "member_id": [137002632, 989635272],
            "name": [
                "John Doe",
                "Jane Doe",
            ],
            "address": [
                "123 Main St",
                "456 Elm St",
            ],
            "city": [
                "Chicago",
                "New York",
            ],
            "state": ["IL", "NY"],
            "zipcode": [15603, 38322],
            "suspended": [False, False],
        }
    )


@pytest.fixture
def test_member_info_after_update():
    return pd.DataFrame(
        {
            "member_id": [137002632, 989635272],
            "name": [
                "John Doe",
                "Jane Doe",
            ],
            "address": [
                "123 Main St",
                "456 Elm St",
            ],
            "city": [
                "Chicago",
                "New York",
            ],
            "state": ["IL", "NY"],
            "zipcode": [86753, 38322],
            "suspended": [False, False],
        }
    )


class TestUpdateMemberRecord:
    """Test of the update_member_record function."""

    def test_update_member_load_io_error(self, mocker, capsys) -> None:
        """Test update_member_record function with load IO error."""
        mocker.patch(
            "choc_an_simulator.manager.load_records_from_file",
            side_effect=pa.ArrowIOError,
        )
        update_member_record()
        assert (
                "There was an error loading the member record." in capsys.readouterr().out
        )

    def test_update_member_record_user_exit(self, mocker):
        """Test of the update_member_record function with user exit."""
        mock_update_records = mocker.patch("choc_an_simulator.manager.prompt_int",
                                           return_value=None)
        assert update_member_record() is None

    def test_update_member_record_io_error(self, mocker, capsys):
        """Test of the update_member_record function with IO error."""
        mocker.patch(
            "choc_an_simulator.manager.load_records_from_file",
            side_effect=pa.ArrowIOError,
        )
        update_member_record()
        assert (
                "There was an error loading the member record." in capsys.readouterr().out
        )

    def test_update_member_record_empty_record_returned(self, mocker, capsys):
        """Test of the update_member_record function with empty record returned."""
        mocker.patch(
            "choc_an_simulator.manager.prompt_int",
            return_value=100000000,
        )
        mocker.patch(
            "choc_an_simulator.manager.load_records_from_file",
            return_value=pd.DataFrame(),
        )
        assert update_member_record() is None
        assert (
                "Warning: No matching member.\n" in capsys.readouterr().out
        )

    def test_update_member_record_valid(
            self,
            mocker,
            capsys,
            test_member_info,
            test_member_info_after_update
    ):
        """Test of the update_member_record function with valid input"""
        mocker.patch(
            "choc_an_simulator.manager.prompt_int",
            return_value=137002632,
        )
        mocker.patch(
            "choc_an_simulator.manager.load_records_from_file",
            return_value=test_member_info,
        )
        mocker.patch(
            "choc_an_simulator.manager.add_records_to_file",
            return_value=None,
        )
        mocker.patch(
            "choc_an_simulator.manager.prompt_menu_options",
            return_value=(5, "zipcode")
        )
        mocker.patch(
            "choc_an_simulator.manager.prompt_int",
            return_value=86753
        )
        mocker.patch(
            "choc_an_simulator.manager.update_record",
            return_value=test_member_info_after_update
        )
        assert update_member_record() is None
        captured = capsys.readouterr().out
        assert (
                "Member record updated." in captured
        )


class TestRemoveMemberRecord:
    """Test of the remove_member_record function."""

    def test_remove_member_record(self, mocker, capsys) -> None:
        """Test remove_member_record successful."""
        member_id = 123456789
        mocker.patch("choc_an_simulator.manager.prompt_int", return_value=member_id)
        mocker.patch(
            "choc_an_simulator.manager.remove_record",
            return_value=True,
        )
        remove_member_record()
        captured = capsys.readouterr()
        expected_output = f"Member {member_id} Removed"
        assert expected_output in captured.out

    def test_remove_member_record_no_member_id(self, mocker, capsys) -> None:
        """Test remove_provider_record without member id."""
        mocker.patch("choc_an_simulator.manager.prompt_int", return_value=None)
        expected_output = remove_member_record()
        assert expected_output is None

    def test_remove_member_io_error(self, mocker, capsys) -> None:
        """Test remove_member_record function with load IO error."""
        member_id = 123456789
        mocker.patch("choc_an_simulator.manager.prompt_int", return_value=member_id)
        mocker.patch(
            "choc_an_simulator.manager.remove_record",
            side_effect=pa.ArrowIOError,
        )
        remove_member_record()
        assert (
            f"There was an error and member {member_id} was not removed!"
            in capsys.readouterr().out
        )


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
            "choc_an_simulator.manager.generate_unique_id",
            side_effect=IndexError,
        )
        add_provider_record()
        assert "No new user added." in capsys.readouterr().out


def test_update_provider_load_io_error(mocker, capsys) -> None:
    """Test update_provider_record function with load IO error."""
    mocker.patch("choc_an_simulator.manager.prompt_int", return_value=123456789)
    mocker.patch(
        "choc_an_simulator.manager.load_records_from_file",
        side_effect=pa.ArrowIOError,
    )
    update_provider_record()
    assert "There was an error loading the provider record." in capsys.readouterr().out


def test_update_provider_id_none(mocker):
    """Test that the user did not enter a provider_id."""
    mocker.patch("choc_an_simulator.manager.prompt_int", return_value=None)
    expected_output = update_provider_record()
    assert expected_output is None


def test_update_provider_selection_none(mocker):
    """Test that the selection is none."""
    mock_df = pd.DataFrame({"id": [123456789], "type": [1]})
    mocker.patch("choc_an_simulator.manager.prompt_int", return_value=123456789)
    mocker.patch(
        "choc_an_simulator.manager.load_records_from_file",
        return_value=mock_df,
    )
    mocker.patch(
        "pandas.DataFrame.iloc",
        return_value=pd.Series({"id": 123456789, "type": 1}, index=mock_df.columns),
    )
    mocker.patch("choc_an_simulator.manager.prompt_menu_options", return_value=None)
    expected_ouput = update_provider_record()
    assert expected_ouput is None


def test_update_provider_zip(mocker, capsys):
    """Test if field to update is zipcode."""
    mock_df = pd.DataFrame({"id": [123456789], "type": [1]})
    mocker.patch("choc_an_simulator.manager.prompt_int", return_value=123456789)
    mocker.patch(
        "choc_an_simulator.manager.load_records_from_file",
        return_value=mock_df,
    )
    mocker.patch(
        "pandas.DataFrame.iloc",
        return_value=pd.Series({"id": 123456789, "type": 1}, index=mock_df.columns),
    )
    mocker.patch(
        "choc_an_simulator.manager.prompt_menu_options", return_value=(6, "zipcode")
    )
    mocker.patch("choc_an_simulator.manager.prompt_int", return_value=12345)
    mocker.patch(
        "choc_an_simulator.manager.update_record",
        return_value=mock_df,
    )
    update_provider_record()


def test_update_provider_record_fail(mocker, capsys):
    mock_df = pd.DataFrame({"id": [123456789], "type": [1]})
    mocker.patch("choc_an_simulator.manager.prompt_int", return_value=123456789)
    mocker.patch(
        "choc_an_simulator.manager.load_records_from_file",
        return_value=mock_df,
    )
    mocker.patch(
        "pandas.DataFrame.iloc",
        return_value=pd.Series({"id": 123456789, "type": 1}, index=mock_df.columns),
    )
    mocker.patch(
        "choc_an_simulator.manager.prompt_menu_options", return_value=(2, "name")
    )
    mocker.patch("choc_an_simulator.manager.prompt_str", return_value="newname")
    mocker.patch(
        "choc_an_simulator.manager.update_record",
        side_effect=pa.ArrowIOError,
    )
    update_provider_record()
    assert "There was an error updating the provider record." in capsys.readouterr().out


class TestRemoveProviderRecord:
    """Test of the remove_member_record function."""

    def test_remove_provider_record(self, mocker, capsys) -> None:
        """Test remove_provider_record successful."""
        provider_id = 123456789
        mocker.patch("choc_an_simulator.manager.prompt_int", return_value=provider_id)
        mocker.patch(
            "choc_an_simulator.manager.remove_record",
            return_value=True,
        )
        remove_provider_record()
        captured = capsys.readouterr()
        expected_output = f"Provider {provider_id} Removed"
        assert expected_output in captured.out

    def test_remove_provider_record_no_provider_id(self, mocker, capsys) -> None:
        """Test remove_provider_record without provider id."""
        mocker.patch("choc_an_simulator.manager.prompt_int", return_value=None)
        expected_output = remove_provider_record()
        assert expected_output is None

    def test_remove_provider_io_error(self, mocker, capsys) -> None:
        """Test remove_provider_record function with load IO error."""
        provider_id = 123456789
        mocker.patch("choc_an_simulator.manager.prompt_int", return_value=provider_id)
        mocker.patch(
            "choc_an_simulator.manager.remove_record",
            side_effect=pa.ArrowIOError,
        )
        remove_provider_record()
        assert (
            f"There was an error and provider {provider_id} was not removed!"
            in capsys.readouterr().out
        )

    # @pytest.mark.parametrize(
    #     "providers_id, expected_output1, is_record_removed",
    #     [
    #         (900000000, "Provider 900000000 Removed", True),
    #         (900000001, "Provider 900000001 Not Found.", False),
    #     ],
    # )
    # def test_remove_provider_record(
    #     self, mocker, providers_id, expected_output1, is_record_removed, capsys
    # ) -> None:
    #     """Test remove_provider_record function with valid input."""
    #     mocker.patch("choc_an_simulator.manager.prompt_int", return_value=providers_id)
    #     mocker.patch(
    #         "choc_an_simulator.manager.remove_record",
    #         return_value=is_record_removed,
    #     )
    #     remove_provider_record()
    #     assert expected_output1 in capsys.readouterr().out


class TestAddProviderDirectoryRecord:
    """Tests for the add_provider_directory_record function"""

    def test_add_provider_directory_record_id(self, mocker, capsys):
        """
        Test of the add_provider_directory_record function when the system has reached the maximum
        number of services.
        """
        mocker.patch(
            "choc_an_simulator.manager.generate_unique_id",
            side_effect=IndexError,
        )
        add_provider_directory_record()
        assert (
            "The maximum number of services has been reached. No new services added."
            in capsys.readouterr().out
        )


# class TestUpdateProviderDirectoryRecord:
def test_update_provider_directory_load_io_error(mocker, capsys) -> None:
    """Test update_provider_directory_record function with load IO error."""
    mocker.patch("choc_an_simulator.manager.prompt_int", return_value=123456)
    mocker.patch(
        "choc_an_simulator.manager.load_records_from_file",
        side_effect=pa.ArrowIOError,
    )
    update_provider_directory_record()
    assert "There was an error loading the service record." in capsys.readouterr().out


def test_update_provider_directory_id_none(mocker):
    """Test that the user did not enter a service_id."""
    mocker.patch("choc_an_simulator.manager.prompt_int", return_value=None)
    expected_output = update_provider_directory_record()
    assert expected_output is None


def test_update_provider_directory_selection_none(mocker):
    """Test that the selection is none."""
    mock_df = pd.DataFrame({"service_id": [123456], "service_name": ["name 0"]})
    mocker.patch("choc_an_simulator.manager.prompt_int", return_value=123456)
    mocker.patch(
        "choc_an_simulator.manager.load_records_from_file",
        return_value=mock_df,
    )
    mocker.patch(
        "pandas.DataFrame.iloc",
        return_value=pd.Series(
            {"service_id": 123456, "service_name": "name 0"}, index=mock_df.columns
        ),
    )
    mocker.patch("choc_an_simulator.manager.prompt_menu_options", return_value=None)
    expected_ouput = update_provider_directory_record()
    assert expected_ouput is None


def test_update_provider_directory_record_fail(mocker, capsys):
    mock_df = pd.DataFrame({"service_id": [123456], "service_name": ["name 0"]})
    mocker.patch("choc_an_simulator.manager.prompt_int", return_value=123456)
    mocker.patch(
        "choc_an_simulator.manager.load_records_from_file",
        return_value=mock_df,
    )
    mocker.patch(
        "pandas.DataFrame.iloc",
        return_value=pd.Series(
            {"service_id": 123456, "service_name": "name 0"}, index=mock_df.columns
        ),
    )
    mocker.patch(
        "choc_an_simulator.manager.prompt_menu_options",
        return_value=(1, "service_name"),
    )
    mocker.patch("choc_an_simulator.manager.prompt_str", return_value="newname")
    mocker.patch(
        "choc_an_simulator.manager.update_record",
        side_effect=pa.ArrowIOError,
    )
    update_provider_directory_record()
    assert "There was an error updating the service record." in capsys.readouterr().out


class TestRemoveProviderDirectoryRecord:
    """Test of the remove_provider_directory_record function."""

    def test_remove_provider_directory_record(self, mocker, capsys) -> None:
        """Test remove_provider_directory_record successful."""
        service_id = 123456
        mocker.patch("choc_an_simulator.manager.prompt_int", return_value=service_id)
        mocker.patch(
            "choc_an_simulator.manager.remove_record",
            return_value=True,
        )
        remove_provider_directory_record()

        captured = capsys.readouterr()
        expected_output = f"Service {service_id} Removed\n"
        assert expected_output in captured.out

    def test_remove_provider_directory_no_service_id(self, mocker, capsys) -> None:
        """Test remove_provider_directory_record without service id."""
        mocker.patch("choc_an_simulator.manager.prompt_int", return_value=None)
        excepted_output = remove_provider_directory_record()
        assert excepted_output is None

    def test_remove_provider_directory_io_error(self, mocker, capsys) -> None:
        """Test remove_provider_directory_record function with load IO error."""
        service_id = 123456
        mocker.patch("choc_an_simulator.manager.prompt_int", return_value=service_id)
        mocker.patch(
            "choc_an_simulator.manager.remove_record",
            side_effect=pa.ArrowIOError,
        )
        remove_provider_directory_record()

        assert (
            f"There as an error and service {service_id} was not removed!"
            in capsys.readouterr().out
        )
