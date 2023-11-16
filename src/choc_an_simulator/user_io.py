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


def prompt_date(
    message: str, min_date: Optional[date] = None, max_date: Optional[date] = None
) -> Optional[date]:
    """
    Prompts the user to enter a date within an optional range.

    Args-
        message: The prompt message displayed to the user.
        min_date: The minimum allowable date (inclusive).
        max_date: The maximum allowable date (inclusive).

    Returns-
        The date entered by the user, or None if the input is aborted.

    Raises-
        ValueError: If min_date is greater than max_date.
    """
    result: Optional[date] = None
    message = f"{message} (MM-DD-YYYY)"
    # min_date can't be greater than max_date
    if ((min_date is not None) and (max_date is not None)) and (min_date > max_date):
        raise ValueError(
            "min_date must be less than or equal to max_date "
            f"({min_date}>{max_date})"
        )

    while result is None:
        date_str = prompt_str(message)
        if date_str is None:
            return None
        try:
            result = datetime.strptime(date_str, "%m-%d-%Y").date()
        # Date incorrectly formatted
        except ValueError:
            PColor.pfail(f"{date_str}is not in MM-DD-YYYY format.")
            continue
        # Date before min_date
        if (min_date is not None) and (result < min_date):
            PColor.pfail(f"Date must be on or after {min_date.strftime('%m-%d-%Y')}")
            result = None

        # Date after max_date
        elif (max_date is not None) and (result > max_date):
            PColor.pfail(f"Date must be on or before {max_date.strftime('%m-%d-%Y')}")
            result = None
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
    if len(choices) == 0:
        raise ValueError("'choices' may not be empty.")
    print(message)
    for i, choice in enumerate(choices):
        PColor.pok(f"{i+1}: ", end=f"{choice}\n")
    selection = prompt_int(
        message="Selection",
        char_limit=None,
        numeric_limit=range(1, len(choices)),
    )
    if selection is None:
        return None
    return (selection - 1, choices[selection - 1])


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
    if numeric_limit is not None:
        message = f"{message} ({numeric_limit.start}-{numeric_limit.stop})"

    while result is None:
        result_text = prompt_str(message, char_limit)
        if result_text is None:  # user pressed ctrl+c
            return None
        result = _to_int_(result_text)
        if result is None:  # Result could not be converted
            print(f'"{result_text}" is not a valid integer.')
        elif (numeric_limit is not None) and not (
            numeric_limit.start <= result <= numeric_limit.stop
        ):
            PColor.pfail(
                f"{result} is not in the range ({numeric_limit.start}-{numeric_limit.stop})"
            )
            result = None

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
    try:
        result: Optional[str] = None
        while result is None:
            result = input(f"{message}: ")
            if (char_limit is not None) and not (
                char_limit.start <= len(result) <= char_limit.stop
            ):
                PColor.pfail(
                    "Input must be between "
                    f"{char_limit.start} and {char_limit.stop} characters long."
                )
                result = None
        return result
    except KeyboardInterrupt:
        print()
        return None


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
