"""System tests of the manager module."""
import pytest
from choc_an_simulator.login import login_menu
from choc_an_simulator.database_management import load_records_from_file
from choc_an_simulator.schemas import MEMBER_INFO, PROVIDER_DIRECTORY_INFO, USER_INFO

MANAGER_LOGIN = ["333333333", "password"]


class MenuPaths:
    """Collection of menu numbers corresponding to each option."""

    MEMBER_REPORT = MANAGER_LOGIN + [4, 1]
    PROVIDER_REPORT = MANAGER_LOGIN + [4, 2]
    SUMMARY_REPORT = MANAGER_LOGIN + [4, 3]

    ADD_MEMBER = MANAGER_LOGIN + [1, 1]
    ADD_PROVIDER = MANAGER_LOGIN + [2, 1]
    ADD_PROVIDER_DIRECTORY = MANAGER_LOGIN + [3, 1]


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
        (MenuPaths.ADD_MEMBER + ["A", "B", "C", "OR", "97221"], MEMBER_INFO),
        (MenuPaths.ADD_PROVIDER + ['A","B","C', "OR", "97221"], USER_INFO),
        (MenuPaths.ADD_PROVIDER_DIRECTORY + ["S", "10", "10"], PROVIDER_DIRECTORY_INFO),
    ],
)
@pytest.mark.usefixtures("mock_input_series", "save_example_info", "mock_report_dir")
def test_add_to_database(
    mock_input_series,
    save_example_info,
    capsys,
    table_info,
):
    """Test adding a new member, provider, and service."""
    df_before = load_records_from_file(table_info)
    with pytest.raises(StopIteration):
        login_menu()
    df_after = load_records_from_file(table_info)
    assert len(df_before) == len(df_after) - 1
