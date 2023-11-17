import pytest
from choc_an_simulator.provider import show_provider_menu

def test_show_provider_menu(capfd):
    show_provider_menu()
    out, err = capfd.readouterr()
    expected_output = """
\033[1mProvider Terminal\033[m\n
Press 1 to \033[1;32mRequest Provider Directory\033[m  |  2 to \033[1;32mRecord Service Entry\033[m  |  3 to \033[1;31mExit\033[m\n\n
"""
    assert out == expected_output