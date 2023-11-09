"""
Functions related to interaction with the terminal.

This includes both user input and formatted display.
"""

from typing import Optional


def prompt_int(message: str, char_limit: range) -> Optional[int]:
    """
    Prompt the user for a number with a character limit. Returns 'None' if 'Ctrl+C' is pressed.

    Args-
        message: The message to display to the user.
        char_limit: The range of acceptable # of digits for the input.

    Returns-
        Optional[int]: The user's input if 'Ctrl+C' was not pressed, otherwise None.
    """
    result: Optional[int] = None
    while result is None:
        result_text = prompt_str(message, char_limit)
        if result_text is None:  # user pressed ctrl+z
            return None
        result = _to_int_(result_text)
        if result is None:  # Result could not be converted
            print(f'"{result_text}" is not a valid integer.')
    return result


def prompt_str(message: str, char_limit: range) -> Optional[str]:
    """
    Prompt the user for input with a character limit. Returns 'None' if 'Ctrl+C' is pressed.

    Args-
        message: The message to display to the user.
        char_limit: The range of acceptable character lengths for the input.

    Returns-
        Optional[str]: The user's input if 'Ctrl+C' was not pressed, otherwise None.
    """
    try:
        result: Optional[str] = None
        while result is None:
            result = input(f"{message}: ")
            if not (char_limit.start <= len(result) <= char_limit.stop):
                print(
                    f"Input must be between {char_limit.start} and {char_limit.stop} characters."
                )
                result = None
        return result
    except KeyboardInterrupt:
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
