"""Tests of the user_io module."""
from datetime import date
import pytest
from choc_an_simulator.user_io import (
    prompt_str,
    prompt_int,
    prompt_menu_options,
    prompt_date,
    PColor,
    _to_int_,
)


class TestPColor:
    test_parameters = [(PColor.pfail, PColor.FAIL), (PColor.pwarn, PColor.WARNING)]

    @pytest.mark.parametrize("func,ansi_code", test_parameters)
    def test_pfuncs(self, func, ansi_code, capsys):
        func("TEST")
        captured = capsys.readouterr()
        print(captured)
        assert captured.out[:5] == ansi_code
        assert captured.out[-5:-1] == PColor.ENDC


class TestPromptDate:
    """Tests of the prompt_date function"""

    test_parameters = [
        # Normal input, leading zeros
        (["02-01-2021"], None, None, date(2021, 2, 1)),
        # Normal input, no leading zeros
        (["2-1-2021"], None, None, date(2021, 2, 1)),
        # Normal input, in range
        (["2-1-2021"], date(2021, 1, 1), date(2021, 2, 1), date(2021, 2, 1)),
        # Below parsing range
        (["0-0-0000", "2-1-2021"], None, None, date(2021, 2, 1)),
        # Above parsing range
        (["0-0-10000", "2-1-2021"], None, None, date(2021, 2, 1)),
        # Below min_date
        (
            ["1-1-2020", "2-1-2021"],
            date(2021, 1, 1),
            date(2022, 1, 1),
            date(2021, 2, 1),
        ),
        # Above max_date
        (
            ["1-1-2023", "2-1-2021"],
            date(2021, 1, 1),
            date(2022, 1, 1),
            date(2021, 2, 1),
        ),
        # Invalid
        (["invalid", "2-1-2021"], None, None, date(2021, 2, 1)),
    ]

    @pytest.mark.parametrize("input_strs,min_date,max_date,expected", test_parameters)
    def test_prompt_date(self, input_strs, min_date, max_date, expected, monkeypatch):
        inputs = iter(input_strs)
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        result = prompt_date("Enter Date", min_date, max_date)
        print(input_strs, "->", result)
        assert result == expected

    def test_prompt_date_ctrl_c(self, monkeypatch):
        """Test that pressing 'Ctrl+C' returns None."""
        monkeypatch.setattr("builtins.input", lambda _: exec("raise KeyboardInterrupt"))
        assert prompt_date("Enter Date") is None

    def test_prompt_date_min_date_greater(self):
        """Test that using a min_date greater than max_date raises a ValueError"""
        with pytest.raises(ValueError):
            prompt_date("Enter Date", date(2022, 1, 1), date(2021, 1, 1))


class TestPromptMenuOptions:
    """Tests of the prompt_menu_options function"""

    test_parameters = [
        (["A", "B", "C"], ["1"], (0, "A")),
        (["A", "B", "C"], ["0", "2"], (1, "B")),
        (["A", "B", "C"], ["-1", "3"], (2, "C")),
    ]

    @pytest.mark.parametrize("choices,input_strs,expected", test_parameters)
    def test_prompt_menu_options_valid_choice(
        self, choices, input_strs, expected, monkeypatch
    ):
        """Test prompt_menu_options using a list of parameters"""
        inputs = iter(input_strs)
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        result = prompt_menu_options("Choose an option:", choices)
        assert result == expected

    def test_prompt_menu_options_empty_choices(self):
        """Test that an empty 'choices' list raises a ValueError."""
        with pytest.raises(ValueError):
            prompt_menu_options("Choose an option:", [])

    def test_prompt_menu_options_ctrl_c(self, monkeypatch):
        """Test that pressing 'Ctrl+C' returns None."""
        monkeypatch.setattr("builtins.input", lambda _: exec("raise KeyboardInterrupt"))
        assert prompt_menu_options("Choose an option:", ["Option 1"]) is None


class TestToInt:
    """Test of the _to_int_ function"""

    test_parameters = [
        ("123", 123),  # Positive int
        ("-123", -123),  # Negative int
        ("1.23", None),  # Decimal
        ("abc", None),  # Non-numeric text
        ("", None),  # Empty string
        ("@#$", None),  # Special characters
    ]

    @pytest.mark.parametrize("input,expected_output", test_parameters)
    def test_to_int_valid(self, input, expected_output):
        assert _to_int_(input) == expected_output


class TestPromptInt:
    test_parameters = [
        (["1"], None, None),  # Normal input
        (["10"], range(1, 4), range(9, 12)),  # Input in range
        (["text", 1], None, None),  # Non-numeric before valid
        (["-1", "10"], None, range(9, 12)),  # Below numeric range before valid
        (["20", "10"], None, range(9, 12)),  # Above numeric before valid
        (["1", "100"], range(2, 4), None),  # Below character limit before valid
        (["10000", "100"], range(2, 4), None),  # Above character limit before valid
    ]

    @pytest.mark.parametrize("input_strs,char_limit,numeric_limit", test_parameters)
    def test_prompt_int(self, input_strs, char_limit, numeric_limit, monkeypatch):
        """Test prompt_int using a list of parameters"""
        inputs = iter(input_strs)
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        expected = int(input_strs[-1])
        assert prompt_int("Enter a number", char_limit, numeric_limit) == expected

    def test_prompt_int_ctrl_c(self, monkeypatch):
        """Test when the user presses 'Ctrl+C'"""
        monkeypatch.setattr("builtins.input", lambda _: exec("raise KeyboardInterrupt"))
        assert prompt_int("Enter a number") is None


class TestPromptString:
    """Tests of the prompt_string() function"""

    test_parameters = [
        (["test"], None),
        (["test"], range(1, 4)),
        (["long input", "test"], range(1, 4)),
        ([""], range(0)),
    ]

    @pytest.mark.parametrize("input_strs,char_limit", test_parameters)
    def test_prompt_string(self, input_strs, char_limit, monkeypatch):
        """Test prompt_string using a list of parameters"""
        inputs = iter(input_strs)
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        # Assert that the last (and only) valid input is returned.
        assert prompt_str("Input", char_limit) == input_strs[-1]

    def test_prompt_string_ctrl_c(self, monkeypatch):
        """Test when the user presses 'Ctrl+C'"""
        monkeypatch.setattr("builtins.input", lambda _: exec("raise KeyboardInterrupt"))
        assert prompt_str("Enter your input", range(1, 9)) is None
