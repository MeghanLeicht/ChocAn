"""Tests of functions in the manager module."""
import pytest
from choc_an_simulator.manager import (
    manager_menu,
    add_member_record,
    remove_member_record,
    add_provider_record,
    update_provider_record,
    remove_provider_record,
    add_provider_directory_record,
    update_provider_directory_record,
    remove_provider_directory_record,
    generate_member_report,
    generate_provider_report,
    generate_summary_report,
)


def test_manager_menu():
    with pytest.raises(NotImplementedError):
        manager_menu()


def test_add_member_record():
    with pytest.raises(NotImplementedError):
        add_member_record()


def test_remove_member_record():
    with pytest.raises(NotImplementedError):
        remove_member_record()


def test_add_provider_record():
    with pytest.raises(NotImplementedError):
        add_provider_record()


def test_update_provider_record():
    with pytest.raises(NotImplementedError):
        update_provider_record()


def test_remove_provider_record():
    with pytest.raises(NotImplementedError):
        remove_provider_record()


def test_add_provider_directory_record():
    with pytest.raises(NotImplementedError):
        add_provider_directory_record()


def test_update_provider_directory_record():
    with pytest.raises(NotImplementedError):
        update_provider_directory_record()


def test_remove_provider_directory_record():
    with pytest.raises(NotImplementedError):
        remove_provider_directory_record()


def test_generate_member_report():
    with pytest.raises(NotImplementedError):
        generate_member_report()


def test_generate_provider_report():
    with pytest.raises(NotImplementedError):
        generate_provider_report()


def test_generate_summary_report():
    with pytest.raises(NotImplementedError):
        generate_summary_report()
