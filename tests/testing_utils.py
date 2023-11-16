from typing import Callable
import pytest
import re


def assert_menu_endpoint(
    menu_func: Callable,
    endpoint_function_name: str,
    option_text: str,
    mocker,
    capsys,
    monkeypatch,
):
    """
    Assert that an option chosen by user_io.prompt_menu_options reaches the right endpoint.

    This function is meant to be called by pytest functions in order to test a menu.

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
            # Parameterized tests of each endpoint in example_menu.
            assert_menu_endpoint(
                menu_func=example_menu,
                endpoint_function_name=endpoint_function_name,
                option_text=option_text,
                mocker=mocker,
                capsys=capsys,
                monkeypatch=monkeypatch,
            )

    """

    def extract_option_number(output, text) -> str:
        """Searches stdout for the given text, and returns the number at the start of the line."""
        pattern = re.compile(r"(\d+):.*?" + re.escape(text))
        match = pattern.search(output)
        if match:
            return match.group(1)
        else:
            raise ValueError("Option text not found in menu output")

    # Mock the input function to automatically select the correct option
    def mock_input(_):
        captured = capsys.readouterr()
        option_number = extract_option_number(captured.out, option_text)
        return option_number

    mocker.patch(endpoint_function_name, side_effect=Exception(endpoint_function_name))
    monkeypatch.setattr("builtins.input", mock_input)
    with pytest.raises(Exception) as err_endpoint:
        menu_func()
    assert endpoint_function_name in str(err_endpoint)
