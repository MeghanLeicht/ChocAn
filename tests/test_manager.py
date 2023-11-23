"""Tests of functions in the manager module."""

import pytest
import pandas as pd
from choc_an_simulator.manager import (
    _generate_user_id,
    manager_menu,
    add_member_record,
    update_member_record,
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


class TestGenerateUserID:
    """Tests of the _generate_user_id function"""

    @pytest.mark.parametrize(
        "existing_ids",
        [
            # First valid ID
            [10000000000],
            # Second to last valid ID
            [19999999998],
            # Empty
            [],
        ],
    )
    def test_generate_user_id_valid(self, mocker, existing_ids):
        """Test generating a valid user ID"""
        mocker.patch(
            "choc_an_simulator.manager.load_records_from_file",
            return_value=pd.DataFrame({"id": existing_ids}),
        )
        # print(load_records_from_file(None))
        new_id = _generate_user_id(1)
        assert new_id == max(existing_ids, default=9999999999) + 1

    def test_generate_user_id_out_of_range(self, mocker):
        """Test generating a user ID that exceeds the max value"""
        mocker.patch(
            "choc_an_simulator.manager.load_records_from_file",
            return_value=pd.DataFrame({"id": [19999999999]}),
        )
        with pytest.raises(IndexError):
            _ = _generate_user_id(1)

    @pytest.mark.parametrize("id_prefix", [-1, 0, 10])
    def test_generate_user_id_bad_prefix(self, mocker, id_prefix):
        """Test generating a user ID with an ID prefix that's out of range"""
        mocker.patch(
            "choc_an_simulator.manager.load_records_from_file",
            return_value=pd.DataFrame({"id": []}),
        )
        with pytest.raises(AssertionError):
            _ = _generate_user_id(id_prefix)


def test_manager_menu():
    """Test of the manager_menu function."""
    with pytest.raises(NotImplementedError):
        manager_menu()


def test_add_member_record():
    """Test of the add_member_record function."""
    with pytest.raises(NotImplementedError):
        add_member_record()


def test_update_member_record():
    """Test of the update_member_record function."""
    with pytest.raises(NotImplementedError):
        update_member_record()


def test_remove_member_record():
    """Test of the remove_member_record function."""
    with pytest.raises(NotImplementedError):
        remove_member_record()


def test_add_provider_record():
    """Test of the add_provider_record function."""
    with pytest.raises(NotImplementedError):
        add_provider_record()


def test_update_provider_record():
    """Test of the update_provider_record function."""
    with pytest.raises(NotImplementedError):
        update_provider_record()


def test_remove_provider_record():
    """Test of the remove_provider_record function."""
    with pytest.raises(NotImplementedError):
        remove_provider_record()


def test_add_provider_directory_record():
    """Test of the add_provider_directory_record function."""
    with pytest.raises(NotImplementedError):
        add_provider_directory_record()


def test_update_provider_directory_record():
    """Test of the update_provider_directory_record function."""
    with pytest.raises(NotImplementedError):
        update_provider_directory_record()


def test_remove_provider_directory_record():
    """Test of the remove_provider_directory_record function."""
    with pytest.raises(NotImplementedError):
        remove_provider_directory_record()


def test_generate_member_report():
    """Test of the generate_member_report function."""
    with pytest.raises(NotImplementedError):
        generate_member_report()


def test_generate_provider_report():
    """Test of the generate_provider_report function."""
    with pytest.raises(NotImplementedError):
        generate_provider_report()


def test_generate_summary_report():
    """Test of the generate_summary_report function."""
    with pytest.raises(NotImplementedError):
        generate_summary_report()
