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
    """Validate functionality and error handling of all functions in the PColor class."""

    @pytest.mark.parametrize(
        "func,ansi_code",
        [
            (PColor.pfail, PColor.AnsiColor.FAIL),
            (PColor.pwarn, PColor.AnsiColor.WARNING),
            (PColor.pok, PColor.AnsiColor.OKGREEN),
        ],
    )
    def test_pfuncs(self, func, ansi_code, capsys):
        """Parameterized tests of the various p{color type} functions."""
        func("TEST")
        captured = capsys.readouterr()
        print(captured)
        assert captured.out[:5] == ansi_code.value
        assert captured.out[5:-5] == "TEST"
        assert captured.out[-5:-1] == PColor._ENDC


class TestPromptDate:
    """Validate functionality and error handling of the prompt_date function."""

    @pytest.mark.parametrize(
        "input_strs,min_date,max_date,expected",
        [
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
        ],
    )
    @pytest.mark.usefixtures("mock_input_series")
    def test_prompt_date(self, mock_input_series, min_date, max_date, expected):
        """Test prompt_date() with a valid date entry."""
        result = prompt_date("Enter Date", min_date, max_date)
        assert result == expected

    def test_prompt_date_ctrl_c(self, mock_input_ctrl_c):
        """Test that pressing 'Ctrl+C' returns None."""
        assert prompt_date("Enter Date") is None

    def test_prompt_date_min_date_greater(self):
        """Test that using a min_date greater than max_date raises a ValueError."""
        with pytest.raises(ValueError):
            prompt_date("Enter Date", date(2022, 1, 1), date(2021, 1, 1))


class TestPromptMenuOptions:
    """Validate functionality and error handling of the prompt_menu_options function."""

    @pytest.mark.parametrize(
        "input_strs,choices,expected",
        [
            # Valid input
            (["1"], ["A", "B", "C"], (0, "A")),
            # Below range, then valid
            (["0", "2"], ["A", "B", "C"], (1, "B")),
            # Above range, then valid
            (["-1", "3"], ["A", "B", "C"], (2, "C")),
        ],
    )
    @pytest.mark.usefixtures("mock_input_series")
    def test_prompt_menu_options_valid_choice(
        self, mock_input_series, choices, expected
    ):
        """Test prompt_menu_options using a list of parameters."""
        result = prompt_menu_options("Choose an option:", choices)
        assert result == expected

    def test_prompt_menu_options_empty_choices(self):
        """Test that an empty 'choices' list raises a ValueError."""
        with pytest.raises(ValueError):
            prompt_menu_options("Choose an option:", [])

    @pytest.mark.usefixtures("mock_input_ctrl_c")
    def test_prompt_menu_options_ctrl_c(self, mock_input_ctrl_c):
        """Test that pressing 'Ctrl+C' returns None."""
        assert prompt_menu_options("Choose an option:", ["Option 1"]) is None


class TestToInt:
    """Validate functionality and error handling of the _to_int_ function."""

    @pytest.mark.parametrize(
        "input,expected_output",
        [
            # Positive int
            ("123", 123),
            # Negative int
            ("-123", -123),
            # Decimal
            ("1.23", None),
            # Non-numeric text
            ("abc", None),
            # Empty string
            ("", None),
            # Special characters
            ("@#$", None),
        ],
    )
    def test_to_int_valid(self, input, expected_output):
        """Test of _to_int_ with valid integer string input."""
        assert _to_int_(input) == expected_output


class TestPromptInt:
    """Validate functionality and error handling of the prompt_int function."""

    @pytest.mark.parametrize(
        "input_strs,expected,char_limit,numeric_limit",
        [
            # Normal input
            (["1"], 1, None, None),
            # Input in range
            (["10"], 10, range(1, 4), range(9, 12)),
            # Non-numeric
            (["text", 1], 1, None, None),
            # Below numeric range
            (["-1", "10"], 10, None, range(9, 12)),
            # Above numeric range
            (["20", "10"], 10, None, range(9, 12)),
            # Below character limit
            (["1", "100"], 100, range(2, 4), None),
            # Above character limit
            (["10000", "100"], 100, range(2, 4), None),
        ],
    )
    @pytest.mark.usefixtures("mock_input_series")
    def test_prompt_int(self, mock_input_series, expected, char_limit, numeric_limit):
        """Test prompt_int using a list of parameters."""
        assert prompt_int("Enter a number", char_limit, numeric_limit) == expected

    @pytest.mark.usefixtures("mock_input_ctrl_c")
    def test_prompt_int_ctrl_c(self, mock_input_ctrl_c):
        """Test when the user presses 'Ctrl+C'"""
        assert prompt_int("Enter a number") is None


class TestPromptString:
    """Validate functionality and error handling of the prompt_str function."""

    @pytest.mark.parametrize(
        "input_strs,expected,char_limit",
        [
            # Valid
            (["test"], "test", None),
            # Valid, within character limit
            (["test"], "test", range(1, 4)),
            # Outside character limit
            (["long input", "test"], "test", range(1, 4)),
            # Empty input
            ([""], "", range(0)),
        ],
    )
    @pytest.mark.usefixtures("mock_input_series")
    def test_prompt_string(self, mock_input_series, expected, char_limit):
        """Test prompt_string using a list of parameters."""
        assert prompt_str("Input", char_limit) == expected

    @pytest.mark.usefixtures("mock_input_ctrl_c")
    def test_prompt_string_ctrl_c(self, mock_input_ctrl_c):
        """Test when the user presses 'Ctrl+C'."""
        assert prompt_str("Enter your input", range(1, 9)) is None
