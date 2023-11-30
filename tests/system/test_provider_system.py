"""Systems tests for the provider interface."""
import pytest
from choc_an_simulator.login import login_menu


class MenuNums:
    """Collection of menu numbers corresponding to each option."""

    REQUEST_DIRECTORY = 1
    RECORD_SERVICE = 2
    CHECK_IN = 3


PROVIDER_LOGIN_SEQUENCE = ["111111111", "password"]
REQUEST_DIRECTORY_SEQUENCE = PROVIDER_LOGIN_SEQUENCE + [1]
RECORD_SERVICE_SEQUENCE = PROVIDER_LOGIN_SEQUENCE + [2]
CHECK_IN_SEQUENCE = PROVIDER_LOGIN_SEQUENCE + [3]


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


@pytest.mark.parametrize(
    "input_strs,check_in_response",
    [
        (PROVIDER_LOGIN_SEQUENCE + [MenuNums.RECORD_SERVICE, "222222222"], "Valid"),
        (PROVIDER_LOGIN_SEQUENCE + [MenuNums.RECORD_SERVICE, "222222223"], "Suspended"),
        (PROVIDER_LOGIN_SEQUENCE + [MenuNums.RECORD_SERVICE, "222222224"], "Invalid"),
    ],
)
@pytest.mark.usefixtures("mock_input_series", "save_example_info")
def test_member_record_service(
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
