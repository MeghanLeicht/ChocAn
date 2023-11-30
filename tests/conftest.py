"""
Collection of testing fixtures and helper functions.

Fixtures in conftest.py are automatically loaded by pytest for use in other tests.
These functions are designed to make testing more straightforward and remove boilerplate.
This includes functions for testing menus and mocking user input.
"""
from typing import List
import re
import pytest
from _pytest.monkeypatch import MonkeyPatch
import pandas as pd
import contextlib

from choc_an_simulator.schemas import USER_INFO, MEMBER_INFO
from choc_an_simulator.database_management import (
    load_records_from_file,
    add_records_to_file,
    _parquet_utils,
    reports,
)


@pytest.fixture
def mock_input_ctrl_c(monkeypatch):
    """
    When included by a test, simulates Ctrl+C as user input.

    Args-
        monkeypatch:
            Pytest fixture for mocking input. To be passed by the test as an indirect parameter.

    Examples-
        See tests/test_user_io.py for several examples
    """
    monkeypatch.setattr("builtins.input", lambda _: exec("raise KeyboardInterrupt"))
    yield


@pytest.fixture
def mock_input_series(input_strs: List[str], monkeypatch):
    """
    When included by a test, simulates input_strs as sequential user inputs.

    Args-
        input_strs: List of strings to simulate as user input
        monkeypatch:
            Pytest fixture for mocking input. To be passed by the test as an indirect parameter.

    Examples-
        See tests/test_user_io.py for several examples
    """
    inputs = iter(input_strs)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))


@pytest.fixture
def assert_menu_endpoint(
    endpoint_func_name: str,
    option_text: str,
    mocker,
    capsys,
    monkeypatch,
):
    """
    Assert that an option chosen by user_io.prompt_menu_options reaches the right endpoint.

    This function is meant to be called by pytest functions in order to test a menu. Works with
    looped and non-looped menus.

    Args-
        menu_func (Callable):
            The menu function to test. This function should use prompt_menu_options.
        endpoint_function_name (str):
            The name of the function that the menu should reach.
        option_text (str): The text shown for the option being tested.
        mocker: Pytest fixture -Pass from parent test function
        capsys: Pytest fixture. Pass from the parent test function.

    Example-
        def example_func_A():
            # Endpoint reached by option A
            print("I'm func A!")

        def example_func_B():
            # Endpoint reached by option B
            print("I'm func B!")

        def example_menu():
            # An example menu that uses prompt_menu_options
            match prompt_menu_options("Pick an option", ["Option A", "Option B"]):
                case (_, "Option A"):
                    example_func_A()
                case (_, "Option B"):
                    example_func_B()

        @pytest.mark.parametrize(
            "option_text,endpoint_function_name",
            [
                # Test that selecting "Option A" leads to example_func_A
                ("Option A", "tests.util.example_func_A"),
                # Test that selecting "Option B" leads to example_func_B
                ("Option B", "tests.util.example_func_B"),
            ],
        )
        def test_example_menu(
            option_text, endpoint_function_name, mocker, capsys, monkeypatch
        ):
            example_menu()

    """

    def extract_option_number(output, text) -> str:
        """Searches stdout for the given text, and returns the number at the start of the line."""
        pattern = re.compile(r"(\d+):.*?" + re.escape(text))
        match = pattern.search(output)
        assert match is not None, "Option text not found in menu output"
        return match[1]

    # Mock the input function to automatically select the correct option
    call_count = 0

    def mock_input(_):
        """
        Searches terminal text for the option text, and returns the matching menu number.

        On the second call, exits the menu with a keyboard interrupt.
        """
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            captured = capsys.readouterr()
            option_number = extract_option_number(captured.out, option_text)
            return option_number
        raise KeyboardInterrupt

    patch = mocker.patch(endpoint_func_name)
    monkeypatch.setattr("builtins.input", mock_input)

    yield

    patch.assert_called()


def save_example_provider_info():
    """Write example provider info to a temporary file."""
    user_df = pd.DataFrame(
        {
            "id": [111111111, 333333333],
            "type": [1, 0],
            "name": ["Joe", "Manny"],
            "address": "12234 NE Street St.",
            "city": "Metrocity",
            "state": "OR",
            "zipcode": 97212,
            "password_hash": bytes(0),
        },
    )
    with contextlib.suppress(ValueError):  # Avoid adding duplicate values
        add_records_to_file(user_df, USER_INFO)
    assert load_records_from_file(USER_INFO).equals(user_df)


def save_example_member_info():
    """Write example provider info to a temporary file."""
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
    """Create a patcher that lasts for the duration of the test module."""
    mp = MonkeyPatch()
    request.addfinalizer(mp.undo)
    return mp


@pytest.fixture(scope="module")
def save_example_info(monkeysession, tmp_path_factory):
    """Mock the directory that parquet files are stored in."""
    monkeysession.setattr(_parquet_utils, "_PARQUET_DIR_", str(tmp_path_factory.getbasetemp()))
    save_example_member_info()
    save_example_provider_info()
    yield tmp_path_factory


@pytest.fixture(scope="module")
def mock_report_dir(monkeysession, tmp_path_factory):
    """Mock the directory that report files are stored in."""
    monkeysession.setattr(reports, "_REPORT_DIR_", str(tmp_path_factory.getbasetemp()))
    yield tmp_path_factory
