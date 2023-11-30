"""Systems tests for the provider interface."""
import pytest
from choc_an_simulator.login import login_menu
from choc_an_simulator.database_management import load_records_from_file
from choc_an_simulator.schemas import PROVIDER_DIRECTORY_INFO

PROVIDER_LOGIN_SEQUENCE = ["111111111", "password"]


class MenuNums:
    """Collection of menu numbers corresponding to each option."""

    REQUEST_DIRECTORY = PROVIDER_LOGIN_SEQUENCE + [1]
    RECORD_SERVICE = PROVIDER_LOGIN_SEQUENCE + [2]
    CHECK_IN = PROVIDER_LOGIN_SEQUENCE + [3]


@pytest.mark.parametrize(
    "input_strs,check_in_response",
    [
        (MenuNums.CHECK_IN + ["222222222"], "Valid"),
        (MenuNums.CHECK_IN + ["222222223"], "Suspended"),
        (MenuNums.CHECK_IN + ["222222224"], "Invalid"),
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
    "input_strs",
    [
        (
            MenuNums.RECORD_SERVICE
            + [
                "09-15-1997",  # Service Date
                "MemName",  # member Name
                "222222222",  # member ID
                "100001",  # service ID
                "50",  # price (dollars)
                "45",  # price (cents)
            ]
        ),
    ],
)
@pytest.mark.usefixtures("mock_input_series", "save_example_info")
def test_member_record_service(
    mock_input_series,
    save_example_info,
    capsys,
    check_in_response,
):
    """Test a valid login by a provider, then recording a service entry."""
    provider_directory_before = load_records_from_file(PROVIDER_DIRECTORY_INFO)
    with pytest.raises(StopIteration):
        login_menu()
    provider_directory_after = load_records_from_file(PROVIDER_DIRECTORY_INFO)
    assert len(provider_directory_before) == len(provider_directory_after) - 1
