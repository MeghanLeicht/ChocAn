"""System tests of the manager module."""
import pytest
from choc_an_simulator.login import login_menu
from choc_an_simulator.database_management import load_records_from_file
from choc_an_simulator.schemas import MEMBER_INFO, PROVIDER_DIRECTORY_INFO, USER_INFO

MANAGER_LOGIN = ["333333333"]


class MenuPaths:
    """Collection of menu numbers corresponding to each option."""

    MEMBER_REPORT = MANAGER_LOGIN + [4, 1]
    PROVIDER_REPORT = MANAGER_LOGIN + [4, 2]
    SUMMARY_REPORT = MANAGER_LOGIN + [4, 3]

    ADD_MEMBER = MANAGER_LOGIN + [1, 1]
    ADD_PROVIDER = MANAGER_LOGIN + [2, 1]
    ADD_PROVIDER_DIRECTORY = MANAGER_LOGIN + [3, 1]

    UPDATE_MEMBER = MANAGER_LOGIN + [1, 2]
    UPDATE_PROVIDER = MANAGER_LOGIN + [2, 2]
    UPDATE_PROVIDER_DIRECTORY = MANAGER_LOGIN + [3, 2]

    REMOVE_MEMBER = MANAGER_LOGIN + [1, 3]
    REMOVE_PROVIDER = MANAGER_LOGIN + [2, 3]
    REMOVE_PROVIDER_DIRECTORY = MANAGER_LOGIN + [3, 3]


@pytest.fixture
def mock_password_auth(mocker):
    """Mock the password entry / authorization process. """
    mocker.patch("choc_an_simulator.login.getpass.getpass", return_value=None)
    mocker.patch("choc_an_simulator.login.generate_secure_password", return_value=[None, None])
    mocker.patch("choc_an_simulator.login.secure_password_verifiction", return_value=True)
    mocker.patch("choc_an_simulator.login.user_type_authorization", return_value=0)
    yield


@pytest.mark.parametrize(
    "input_strs,expected_output",
    [
        (MenuPaths.MEMBER_REPORT, "Member Report"),
        (MenuPaths.PROVIDER_REPORT, "Provider Report"),
        (MenuPaths.SUMMARY_REPORT, "Summary Report"),
    ],
)
@pytest.mark.usefixtures("mock_input_series", "save_example_info", "mock_report_dir")
def test_member_reports(
    mock_input_series,
    save_example_info,
    mock_password_auth,
    capsys,
    expected_output,
):
    """Test a valid login by a provider, all member check-in responses."""

    with pytest.raises(StopIteration):
        login_menu()
    out = capsys.readouterr().out
    assert expected_output in out


@pytest.mark.parametrize(
    "input_strs,table_info",
    [
        (MenuPaths.ADD_MEMBER + ["Name", "Addr", "City", "OR", "97221"], MEMBER_INFO),
        (MenuPaths.ADD_PROVIDER + ["Name", "Addr", "City", "OR", "97221"], USER_INFO),
        (MenuPaths.ADD_PROVIDER_DIRECTORY + ["S", "10", "10"], PROVIDER_DIRECTORY_INFO),
    ],
)
@pytest.mark.usefixtures("mock_input_series", "save_example_info", "mock_report_dir")
def test_add_to_database(
    mock_input_series,
    save_example_info,
    mock_password_auth,
    table_info,
):
    """Test adding a new member, provider, and service."""
    df_before = load_records_from_file(table_info)
    login_menu()
    df_after = load_records_from_file(table_info)
    assert len(df_before) == len(df_after) - 1


@pytest.mark.parametrize(
    "input_strs,table_info",
    [
        (MenuPaths.REMOVE_MEMBER + ["222222222"], MEMBER_INFO),
        (MenuPaths.REMOVE_PROVIDER + ["111111111"], USER_INFO),
        (
            MenuPaths.REMOVE_PROVIDER_DIRECTORY + ["S", "10", "10"],
            PROVIDER_DIRECTORY_INFO,
        ),
    ],
)
@pytest.mark.usefixtures("mock_input_series", "save_example_info", "mock_report_dir")
def test_remove_from_database(
    mock_input_series,
    save_example_info,
    mock_password_auth,
    table_info,
):
    """Test removing a new member, provider, and service."""
    df_before = load_records_from_file(table_info)
    login_menu()
    df_after = load_records_from_file(table_info)
    assert len(df_before) == len(df_after) + 1


@pytest.mark.parametrize(
    "input_strs,table_info",
    [
        (MenuPaths.UPDATE_MEMBER + [1, 222222222, "Newname"], MEMBER_INFO),
        (MenuPaths.UPDATE_PROVIDER + [1, 111111111, "Newname"], USER_INFO),
        (
            MenuPaths.UPDATE_PROVIDER_DIRECTORY + [1, 100001, "Newname"],
            PROVIDER_DIRECTORY_INFO,
        ),
    ],
)
@pytest.mark.usefixtures("mock_input_series", "save_example_info", "mock_report_dir")
def test_update_in_database(
    mock_input_series,
    save_example_info,
    mock_password_auth,
    table_info,
):
    """Test removing a new member, provider, and service."""
    login_menu()
    df_after = load_records_from_file(table_info)
    assert df_after.iloc[0, 1] == "Newname"
