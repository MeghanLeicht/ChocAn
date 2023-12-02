"""
Provides a suite of functions for terminal-based user interactions.

Includes capabilities for prompting users for various types of input (dates, integers, strings,
and menu selections) and displaying information with ANSI color codes. The module is designed to
enhance user experience in command-line applications by facilitating easy and structured user input
and colorful text output.

See 'examples/prompting.py' for usage examples.
"""

from typing import Optional, List, Tuple
from enum import Enum
from datetime import date, datetime


class PColor:
    """
    Provides methods for printing text in various colors / styles in the terminal using ANSI codes.

    This class encapsulates the functionality for color-coded output, making it easier to produce
    visually distinct messages, such as warnings, errors, or confirmations.
    """

    class AnsiColor(Enum):
        """
        Enumerates ANSI color codes for terminal text formatting.

        These codes are used to change the color and style of text output in the terminal.
        Source: https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
        """

        HEADER = "\033[95m"
        OKBLUE = "\033[94m"
        OKCYAN = "\033[96m"
        OKGREEN = "\033[92m"
        WARNING = "\033[93m"
        FAIL = "\033[91m"
        BOLD = "\033[1m"
        UNDERLINE = "\033[4m"

    # ANSI color code to end a color
    _ENDC = "\033[0m"

    @classmethod
    def pfail(cls, text: str, **kwargs) -> None:
        """
        Prints text in red to indicate failure or error messages.

        Args-
            text: The text to be printed.
            **kwargs: Additional keyword arguments passed to the built-in print function.
        """
        cls.pcolor(text, cls.AnsiColor.FAIL, **kwargs)

    @classmethod
    def pwarn(cls, text: str, **kwargs) -> None:
        """
        Prints text in yellow to indicate warnings.

        Args-
            text: The text to be printed.
            **kwargs: Additional keyword arguments passed to the built-in print function.
        """
        cls.pcolor(text, cls.AnsiColor.WARNING, **kwargs)

    @classmethod
    def pok(cls, text: str, **kwargs) -> None:
        """
        Prints text in green to indicate success or confirmation messages.

        Args-
            text: The text to be printed.
            **kwargs: Additional keyword arguments passed to the built-in print function.
        """
        cls.pcolor(text, cls.AnsiColor.OKGREEN, **kwargs)

    @classmethod
    def pcolor(cls, text: str, color_code: AnsiColor, **kwargs):
        """
        Prints text in a specified color or style.

        Args-
            text: The text to be printed.
            color_code: The AnsiColor code defining the color or style of the text.
            **kwargs: Additional keyword arguments passed to the built-in print function.
        """
        print(f"{color_code.value}{text}{cls._ENDC}", **kwargs)


def _parse_date(date_str: str) -> date:
    """
    Parse a date string into a date object, using %m-%d-%Y format.

    Args-
        date_str (str): String to parse into a date.

    Returns-
        date: The parsed date.

    Raises-
        ValueError: Date is in the incorrect format.
    """
    try:
        result = datetime.strptime(date_str, "%m-%d-%Y").date()
    # Date incorrectly formatted
    except ValueError:
        raise ValueError("Incorrect date format")
    return result


def _prompt_single_date(message: str, min_date: date, max_date: date) -> Optional[date]:
    """
    Prompt the user for a single date.

    Args-
        message (str): The prompt message displayed to the user.
        min_date (date): Minimum allowed date
        max_date (date): Maximum allowed date

    Returns-
        int: Valid input, parsed as an integer.
        None: user aborted.

    Raises-
        ValueError: Input invalid.
    """
    date_str = prompt_str(message)
    if date_str is None:
        return None
    try:
        result = _parse_date(date_str)
    except ValueError:
        PColor.pfail(f"{date_str} is not in MM-DD-YYYY format.")
        raise ValueError
    if not (min_date <= result <= max_date):
        min_date_str = min_date.strftime("%m-%d-%Y")
        max_date_str = max_date.strftime("%m-%d-%Y")
        PColor.pfail(f"Date must be between {min_date_str} and {max_date_str}")
        raise ValueError
    return result


def prompt_date(
    message: str, min_date: Optional[date] = None, max_date: Optional[date] = None
) -> Optional[date]:
    """
    Prompts the user to enter a date within an optional range.

    Args-
        message (str): The prompt message displayed to the user.
        min_date (Optional[date]): The minimum allowable date (inclusive, optional).
        max_date (Optional[date]): The maximum allowable date (inclusive, optional).

    Returns-
        The date entered by the user, or None if the input is aborted.

    Raises-
        ValueError: If min_date is greater than max_date.
    """
    result: Optional[date] = None
    # Default min / max date to their absolute min / max values.
    min_date = min_date or date.min
    max_date = max_date or date.max

    if min_date > max_date:
        raise ValueError(f"min_date {min_date} must be less than max_date {max_date}")
    message = f"{message} (MM-DD-YYYY)"
    # Repeatedly prompt for a date until valid input or user exits.
    while True:
        try:
            result = _prompt_single_date(message, min_date, max_date)
        except ValueError:
            continue
        return result


def prompt_menu_options(message: str, choices: List[str]) -> Optional[Tuple[int, str]]:
    """
    Prompts the user to select an option from a list of choices.

    Args-
        message: The prompt message displayed to the user.
        choices: A list of string options to choose from.

    Returns-
        A tuple containing the index and text of the chosen option, or None if aborted.

    Raises-
        ValueError: If the 'choices' list is empty.
    """
    assert choices, "'choices' may not be empty."
    print(message)
    for i, choice in enumerate(choices):
        PColor.pok(f"{i+1}: ", end=f"{choice}\n")
    selection = prompt_int(
        message="Selection",
        char_limit=None,
        numeric_limit=range(1, len(choices)),
    )
    return (selection - 1, choices[selection - 1]) if selection else None


def _prompt_single_int(
    message: str, char_limit: Optional[range], numeric_limit: Optional[range]
) -> Optional[int]:
    """
    Prompt the user for a single integer.

    Args-
        message: The prompt message displayed to the user.
        char_limit: The range of acceptable character counts for the input.
        numeric_limit: The numeric range of acceptable input values.

    Returns-
        int: Valid input, parsed as an integer.
        None: user aborted.

    Raises-
        ValueError: Input invalid.
    """
    result_text = prompt_str(message, char_limit)
    if result_text is None:  # user pressed ctrl+c
        return None

    result = _to_int_(result_text)
    # Result could not be converted
    if result is None:
        print(f'"{result_text}" is not a valid integer.')
        raise ValueError
    # Result could not be converted
    if (numeric_limit is not None) and not (numeric_limit.start <= result <= numeric_limit.stop):
        PColor.pfail(f"{result} is not in the range ({numeric_limit.start}-{numeric_limit.stop})")
        raise ValueError
    return result


def prompt_int(
    message: str,
    char_limit: Optional[range] = None,
    numeric_limit: Optional[range] = None,
) -> Optional[int]:
    """
    Prompts the user for an integer input within specified character and numeric limits.

    Args-
        message: The prompt message displayed to the user.
        char_limit: The range of acceptable character counts for the input.
        numeric_limit: The numeric range of acceptable input values.

    Returns-
        The integer entered by the user, or None if the input is aborted.
    """
    result: Optional[int] = None
    # If there is a numeric limit, add it to the message string.
    if numeric_limit is not None:
        message = f"{message} ({numeric_limit.start}-{numeric_limit.stop})"
    # Repeatedly prompt for an integer until valid input or user exits
    while True:
        try:
            result = _prompt_single_int(message, char_limit, numeric_limit)
        except ValueError:
            continue
        return result


def _prompt_single_str(message: str, char_limit: Optional[range]) -> Optional[str]:
    """
    Prompt the user for a single string.

    Args-
        message (str): The prompt message displayed to the user.
        char_limit (str): The max / min character length of the input (optional).

    Returns-
        int: The inputted string.
        None: user aborted.

    Raises-
        ValueError: Input invalid.
    """
    try:
        result = input(f"{message}: ")
    except KeyboardInterrupt:
        print()
        return None
    if (char_limit is not None) and not (char_limit.start <= len(result) <= char_limit.stop):
        PColor.pfail(
            "Input must be between " f"{char_limit.start} and {char_limit.stop} characters long."
        )
        raise ValueError
    return result


def prompt_str(message: str, char_limit: Optional[range] = None) -> Optional[str]:
    """
    Prompts the user for a string input with an optional character limit.

    Args-
        message: The prompt message displayed to the user.
        char_limit: The range of acceptable character lengths for the input.

    Returns-
        The string entered by the user, or None if the input is aborted.
    """
    while True:
        try:
            result = _prompt_single_str(message, char_limit)
        except ValueError:
            continue
        return result


def _to_int_(text: str) -> Optional[int]:
    """
    Attempts to convert a string to an integer.

    Args-
        text: The text to be converted.

    Returns-
        The converted integer, or None if the conversion is not possible.
    """
    try:
        return int(text)
    except ValueError:
        return None
