"""Examples of the various prompting functions included in the user_io module."""

from datetime import datetime
from choc_an_simulator.user_io import (
    prompt_date,
    prompt_int,
    prompt_menu_options,
    prompt_str,
)


def ex_prompt_menu():
    """Example use of prompt_menu(). Routes to examples for other functions."""
    selection = 0
    while selection is not None:
        selection = prompt_menu_options(
            "Choose an example using this menu, which is also an example."
            "\nPress Ctrl+C to Exit.",
            ["prompt_str()", "prompt_int()", "prompt_date()"],
        )
        if selection is None:
            continue
        (index, text) = selection
        match text:
            case "prompt_str()":
                assert index == 0
                ex_prompt_string()
            case "prompt_int()":
                assert index == 1
                ex_prompt_int()
            case "prompt_date()":
                ex_prompt_date()

    print("Goodbye!")


def ex_prompt_string():
    """Example use of prompt_str()."""
    print("This is an example of prompt_str! When you're done, press Ctrl+C to exit.")
    answer = ""
    while answer is not None:
        answer = prompt_str("Enter some text", char_limit=range(5, 10))
        if answer is not None:
            print(f"\tYou entered: {answer}")
    print("No answer given. Moving on.\n")


def ex_prompt_int():
    """Example use of prompt_int()."""
    print("This is an example of prompt_int When you're done, press Ctrl+C to exit.")
    answer = ""
    while answer is not None:
        answer = prompt_int(
            "Enter a number", char_limit=range(2, 3), numeric_limit=range(60, 200)
        )
        if answer is not None:
            print(f"\tYou entered: {answer}. Half of {answer} is {answer/2}.")
    print("No answer given. Moving on.\n")


def ex_prompt_date():
    """Example use of prompt_date()."""
    print("This is an example of prompt_date! When you're done, press Ctrl+C to exit.")
    answer = ""
    while answer is not None:
        answer = prompt_date("Enter a date", max_date=datetime.now().date())
        if answer is not None:
            print(
                f"\tYou entered: {answer}."
                "\n\tDay: {answer.day}, Month: {answer.month}, Year: {answer.year}"
            )
    print("No answer given. Moving on.\n")


if __name__ == "__main__":
    ex_prompt_menu()
