"""System tests of the manager module."""
import pytest
from choc_an_simulator.login import login_menu

MANAGER_LOGIN_SEQUENCE = ["333333333", "password"]


class MenuPaths:
    """Collection of menu numbers corresponding to each option."""

    MEMBER_REPORT = [4, 1]
    PROVIDER_REPORT = [4, 2]
    SUMMARY_REPORT = [4, 3]


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
    print(out)
    assert expected_output in out
