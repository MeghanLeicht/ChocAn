"""Systems tests for the provider interface."""
import contextlib
import pytest
from _pytest.monkeypatch import MonkeyPatch
import pandas as pd
from choc_an_simulator.login import login_menu
from choc_an_simulator.database_management import (
    add_records_to_file,
    load_records_from_file,
)
from choc_an_simulator.database_management import _parquet_utils
from choc_an_simulator.schemas import USER_INFO, MEMBER_INFO

PROVIDER_LOGIN_SEQUENCE = ["111111111", "password"]


class MenuNums:
    """Collection of menu numbers corresponding to each option."""

    REQUEST_DIRECTORY = 1
    RECORD_SERVICE = 2
    CHECK_IN = 3


def save_example_provider_info():
    """Write example provider info to a temporary file"""
    user_df = pd.DataFrame(
        {
            "id": 111111111,
            "type": 1,
            "name": "Joe",
            "address": "12234 NE Street St.",
            "city": "Metrocity",
            "state": "OR",
            "zipcode": 97212,
            "password_hash": bytes(0),
        },
        index=[0],
    )
    with contextlib.suppress(ValueError):  # Avoid adding duplicate values
        add_records_to_file(user_df, USER_INFO)
    assert load_records_from_file(USER_INFO).equals(user_df)


def save_example_member_info():
    """Write example provider info to a temporary file"""
    member_df = pd.DataFrame(
        {
            "member_id": [222222222, 222222223],
            "name": ["Mary", "Marie"],
            "address": ["4321 NE Street St.", "A second place"],
            "city": "Metrocity",
            "state": "OR",
            "zipcode": 97212,
            "suspended": [False, True],
        },
    )
    with contextlib.suppress(ValueError):  # Avoid adding duplicate values
        add_records_to_file(member_df, MEMBER_INFO)
    assert load_records_from_file(MEMBER_INFO).equals(member_df)


@pytest.fixture(scope="module")
def monkeysession(request):
    """Create a patcher that lasts for the duration of the test module"""
    mp = MonkeyPatch()
    request.addfinalizer(mp.undo)
    return mp


@pytest.fixture(scope="module")
def save_example_info(monkeysession, tmp_path_factory):
    """Mock the directory that parquet files are stored"""
    monkeysession.setattr(_parquet_utils, "_PARQUET_DIR_", str(tmp_path_factory.getbasetemp()))
    save_example_member_info()
    save_example_provider_info()
    yield tmp_path_factory


@pytest.mark.parametrize("input_strs", [PROVIDER_LOGIN_SEQUENCE])
@pytest.mark.usefixtures("mock_input_series")
def test_provider_login(mock_input_series, capsys, save_example_info):
    """Test a valid login by a provider"""
    with pytest.raises(StopIteration):
        login_menu()
    out = capsys.readouterr().out
    assert "User ID: 111111111" in out
    assert "User Name: Joe" in out
    assert "Provider Menu" in out


@pytest.mark.parametrize(
    "input_strs,check_in_response",
    [
        (PROVIDER_LOGIN_SEQUENCE + [MenuNums.CHECK_IN, "222222222"], "Valid"),
        (PROVIDER_LOGIN_SEQUENCE + [MenuNums.CHECK_IN, "222222223"], "Suspended"),
        (PROVIDER_LOGIN_SEQUENCE + [MenuNums.CHECK_IN, "222222224"], "Invalid"),
    ],
)
@pytest.mark.usefixtures(
    "mock_input_series",
)
def test_member_check_in(
    mock_input_series,
    capsys,
    save_example_info,
    check_in_response,
):
    """Test a valid login by a provider, all member check-in responses."""
    with pytest.raises(StopIteration):
        login_menu()
    out = capsys.readouterr().out
    print(out)
    assert check_in_response in out
    assert "Provider Menu" in out
