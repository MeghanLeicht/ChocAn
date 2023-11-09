"""Tests of the user_io module."""
from choc_an_simulator.user_io import prompt_str, prompt_int, _to_int_


class TestToInt:
    """Test of the _to_int_ function"""

    def test_to_int_valid(self):
        assert _to_int_("123") == 123

    def test_to_int_invalid(self):
        assert _to_int_("abc") is None

    def test_to_int_empty_string(self):
        assert _to_int_("") is None

    def test_to_int_special_chars(self):
        assert _to_int_("@#$") is None


class TestPromptInt:
    def test_prompt_int_valid_input(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda x: "123")
        assert prompt_int("Enter a number", range(1, 4)) == 123

    def test_prompt_int_invalid_then_valid(self, monkeypatch, capsys):
        inputs = iter(["abc", "123"])
        monkeypatch.setattr("builtins.input", lambda x: next(inputs))

        assert prompt_int("Enter a number", range(1, 4)) == 123
        captured = capsys.readouterr()
        assert '"abc" is not a valid integer.' in captured.out

    def test_prompt_int_ctrl_c(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda x: exec("raise KeyboardInterrupt"))
        assert prompt_int("Enter a number", range(1, 4)) is None

    def test_prompt_int_char_limit_exceeded_then_valid(self, monkeypatch):
        inputs = iter(["111111", "11"])
        monkeypatch.setattr("builtins.input", lambda x: next(inputs))
        assert prompt_int("Enter a number", range(2, 4)) == 11

    def test_prompt_int_char_limit_below_then_valid(self, monkeypatch):
        inputs = iter(["1", "11"])
        monkeypatch.setattr("builtins.input", lambda x: next(inputs))
        assert prompt_int("Enter a number", range(2, 4)) == 11


class TestPromptString:
    """Tests of the prompt_string() function"""

    def test_prompt_string_within_limit(self, monkeypatch):
        """Test when the user enters a string within the character limit."""

        inputs = iter(["test"])
        monkeypatch.setattr("builtins.input", lambda x: next(inputs))
        assert prompt_str("Enter your input", range(1, 9)) == "test"

    def test_prompt_string_outside_then_within_limit(self, monkeypatch, capsys):
        """Test when the user initially enters a string outside the character limit."""
        inputs = iter(["long input", "test"])
        monkeypatch.setattr("builtins.input", lambda x: next(inputs))

        assert prompt_str("Enter your input", range(1, 9)) == "test"
        captured = capsys.readouterr()
        assert "Input must be between 1 and 9 characters." in captured.out

    def test_prompt_string_ctrl_c(self, monkeypatch):
        """Test when the user presses 'Ctrl+C'"""
        monkeypatch.setattr("builtins.input", lambda x: exec("raise KeyboardInterrupt"))
        assert prompt_str("Enter your input", range(1, 9)) is None
