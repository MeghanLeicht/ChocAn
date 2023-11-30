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
    "input_strs,check_in_response",
    [
        (CHECK_IN_SEQUENCE + ["222222222"], "Valid"),
        (CHECK_IN_SEQUENCE + ["222222223"], "Suspended"),
        (CHECK_IN_SEQUENCE + ["222222224"], "Invalid"),
    ],
)
@pytest.mark.usefixtures("mock_input_series", "save_example_info")
def test_member_check_in(
    mock_input_series,
    save_example_info,
    capsys,
    check_in_response,
):
    """Test a valid login by a provider, all member check-in responses."""
    with pytest.raises(StopIteration):
        login_menu()
    out = capsys.readouterr().out
    print(out)
    assert check_in_response in out
    assert "Provider Menu" in out
