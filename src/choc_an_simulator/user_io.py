"""
Functions related to interaction with the terminal.

Examples for prompting functions available in examples/prompting.py
"""

from typing import Optional, List, Tuple, Dict, Literal
from datetime import date, datetime


class PColor:
    """Functions for printing in color."""

    # ANSI color codes. Source: https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
    ansi_codes: Dict[str, str] = {
        "HEADER": "\033[95m",
        "OKBLUE": "\033[94m",
        "OKCYAN": "\033[96m",
        "OKGREEN": "\033[92m",
        "WARNING": "\033[93m",
        "FAIL": "\033[91m",
        "ENDC": "\033[0m",
        "BOLD": "\033[1m",
        "UNDERLINE": "\033[4m",
    }
    TColorNames = Literal["HEADER", "OKGREEN", "WARNING", "FAIL", "BOLD", "UNDERLINE"]

    @classmethod
    def pfail(cls, text: str, **kwargs) -> None:
        """Print failure text. kwargs are passed to print()."""
        cls.pcolor(text, "FAIL", **kwargs)

    @classmethod
    def pwarn(cls, text: str, **kwargs) -> None:
        """Print warning text. kwargs are passed to print()."""
        cls.pcolor(text, "WARNING", **kwargs)

    @classmethod
    def pok(cls, text: str, **kwargs) -> None:
        """Print green OK text. kwargs are passed to print()."""
        cls.pcolor(text, "OKGREEN", **kwargs)

    @classmethod
    def pcolor(cls, text: str, color_name: TColorNames, **kwargs):
        """
        Print text with any of the colors / styles listed in TColorNames.

        kwargs are passed to print().
        """
        print(f"{cls.ansi_codes[color_name]}{text}{cls.ansi_codes['ENDC']}", **kwargs)


def prompt_date(
    message: str, min_date: Optional[date] = None, max_date: Optional[date] = None
) -> Optional[date]:
    """
    Prompt the user to enter a date in MM-DD-YYYY format.

    Args-
        message: Message to display before date input.
        min_date: Optional minimum allowed date.
        max_date: Optionam maximum date.
    Returns-
        date: Tuple containin the choice index and text
        None: User pressed Ctrl+C
    Raises-
        ValueError: min_date is greater than max_date
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
    Prompt the user to choose from a list of options.

    Args-
        message: Message to display before menu options.

    Returns-
        Tuple[int, str]: Tuple containing the choice index and text
        None: User pressed Ctrl+C
    Raises-
        ValueError: choices is empty
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
    Prompt the user for a number with a character limit. Returns 'None' if 'Ctrl+C' is pressed.

    Args-
        message: The message to display to the user.
        char_limit: The range of acceptable # of digits for the input.
        numeric_limit: The (optional) numeric range of the input

    Returns-
        int: The user's input
        None: User pressed Ctrl+C
    """
    result: Optional[int] = None
    if numeric_limit is not None:
        message = f"{message} ({numeric_limit.start}-{numeric_limit.stop})"

    while result is None:
        result_text = prompt_str(message, char_limit)
        if result_text is None:  # user pressed ctrl+z
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
    Prompt the user for input with a character limit. Returns 'None' if 'Ctrl+C' is pressed.

    Args-
        message: The message to display to the user.
        char_limit: The range of acceptable character lengths for the input.

    Returns-
        str: The user's input
        None: User pressed Ctrl+C
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
    Attempt to convert text to an integer.

    Args-
        text: text to convert

    Returns-
        int: Successfully-converted text
        None: Text is not valid int
    """
    try:
        return int(text)
    except ValueError:
        return None
