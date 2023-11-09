"""
Functions related to interaction with the terminal.

This includes both user input and formatted display.
"""

from typing import Optional, List, Tuple


def prompt_menu_options(message: str, choices: List[str]) -> Optional[Tuple[int, str]]:
    """
    Prompt the user to choose from a list of options.

    Args-
        message: Message to display before menu options.

    Returns-
        Tuple[int, str]: Tuple containin the choice index and text

    Raises-
        ArgumentError: choices is empty
    """
    if len(choices) == 0:
        raise ValueError("'choices' may not be empty.")
    print(message)
    for i, choice in enumerate(choices):
        print(f"\t{i+1}: {choice}")
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
        Optional[int]: The user's input if 'Ctrl+C' was not pressed, otherwise None.
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
            print(
                f'"{result}" is not in the range ({numeric_limit.start}-{numeric_limit.stop})"'
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
        Optional[str]: The user's input if 'Ctrl+C' was not pressed, otherwise None.
    """
    try:
        result: Optional[str] = None
        while result is None:
            result = input(f"{message}: ")
            if (char_limit is not None) and not (
                char_limit.start <= len(result) <= char_limit.stop
            ):
                print(
                    "Input must be between "
                    f"{char_limit.start} and {char_limit.stop} characters long."
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
