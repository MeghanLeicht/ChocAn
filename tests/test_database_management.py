import pandas as pd
import pyarrow as pa
import os
import pytest
from choc_an_simulator.database_management import (
    add_records_to_file,
    load_records_from_file,
    update_record,
    remove_record,
    _load_all_records_from_file_,
    _overwrite_records_to_file_,
    _PARQUET_DIR_,
)

EXAMPLE_NAME = "test"
EXAMPLE_RECORDS = pd.DataFrame({"ID": [1, 2], "value": [1.1, 2.2]})
EXAMPLE_SCHEMA = pa.schema([("ID", pa.int64()), ("value", pa.float64())])


def _save_example_file_():
    """Save an example file for testing"""
    _overwrite_records_to_file_(EXAMPLE_NAME, EXAMPLE_RECORDS, EXAMPLE_SCHEMA)


def _delete_example_file_():
    """Delete file saved by save_example_file"""
    test_path = os.path.join(_PARQUET_DIR_, f"{EXAMPLE_NAME}.pkt")
    if os.path.exists(test_path):
        os.remove(test_path)


def test_add_records_to_file():
    """Test of the add_records_to_file function"""
    _save_example_file_()
    new_records = pd.DataFrame({"ID": [3, 4], "value": [1.1, 2.2]})
    add_records_to_file(EXAMPLE_NAME, new_records, EXAMPLE_SCHEMA)
    updated_records = load_records_from_file(EXAMPLE_NAME, EXAMPLE_SCHEMA)
    expected_records = pd.concat([EXAMPLE_RECORDS, new_records]).reset_index(drop=True)
    assert updated_records.equals(
        expected_records
    ), f"\n{expected_records}\n{updated_records}"
    with pytest.raises(ValueError):
        add_records_to_file(EXAMPLE_NAME, EXAMPLE_RECORDS, EXAMPLE_SCHEMA)
    _delete_example_file_()


def test_load_records_from_file():
    """Tests of the load_records_from_file function"""
    _save_example_file_()
    # Test 1: No Filter
    all_records = load_records_from_file(EXAMPLE_NAME, EXAMPLE_SCHEMA)
    assert EXAMPLE_RECORDS.equals(all_records)
    # Test 2: Equality filter
    eq_records = load_records_from_file(EXAMPLE_NAME, EXAMPLE_SCHEMA, eq_cols={"ID": 1})
    assert EXAMPLE_RECORDS[EXAMPLE_RECORDS["ID"] == 1].equals(eq_records)
    # Test 3: Less-than filter
    lt_records = load_records_from_file(
        EXAMPLE_NAME, EXAMPLE_SCHEMA, lt_cols={"value": 2.0}
    )
    assert EXAMPLE_RECORDS[EXAMPLE_RECORDS["value"] < 2.0].equals(lt_records)
    # Test 4: Greater-than filter
    lt_records = load_records_from_file(
        EXAMPLE_NAME, EXAMPLE_SCHEMA, gt_cols={"value": 2.0}
    )
    assert EXAMPLE_RECORDS[EXAMPLE_RECORDS["value"] > 2.0].equals(lt_records)
    _delete_example_file_()
    # Test 5: Missiing file
    empty_records = load_records_from_file(EXAMPLE_NAME, EXAMPLE_SCHEMA)
    assert empty_records.empty
    _delete_example_file_()


def test_overwrite_records_to_file_():
    """Tests of the overwrite_records_to_file_ function"""
    _save_example_file_()
    records = pd.DataFrame({"ID": [3, 4], "value": [3.3, 4.4]})
    _overwrite_records_to_file_(EXAMPLE_NAME, records, EXAMPLE_SCHEMA)

    # Load records to check
    updated_records = _load_all_records_from_file_(EXAMPLE_NAME, EXAMPLE_SCHEMA)
    assert updated_records.equals(records), (
        "\n" + str(records) + "\n" + str(updated_records)
    )
    _delete_example_file_()


def test_update_record():
    """Tests of the update_record function"""
    _save_example_file_()
    # Test 1: Normal update
    updated_record = update_record(EXAMPLE_NAME, 2, EXAMPLE_SCHEMA, value=2.3)
    loaded_record = load_records_from_file(
        EXAMPLE_NAME, EXAMPLE_SCHEMA, eq_cols={"ID": 2}
    ).iloc[0]
    assert (updated_record == loaded_record).all()

    # Test 2: No keyword arguments
    with pytest.raises(AssertionError):
        update_record(EXAMPLE_NAME, 2, EXAMPLE_SCHEMA)

    # Test 3: Bad index
    with pytest.raises(IndexError):
        update_record(EXAMPLE_NAME, 3, EXAMPLE_SCHEMA, value=3.3)

    # Test 4: Bad column
    with pytest.raises(KeyError):
        update_record(EXAMPLE_NAME, 2, EXAMPLE_SCHEMA, bad_column_name="hello")

    _delete_example_file_()


def test_remove_record():
    """Tests of the remove_record function"""
    _save_example_file_()
    # Test 1: Remove existing entry
    records_before = load_records_from_file(EXAMPLE_NAME, EXAMPLE_SCHEMA)
    assert 1 in records_before["ID"]
    removed = remove_record(EXAMPLE_NAME, 1, EXAMPLE_SCHEMA)
    assert removed
    # Load updated table from file
    records_rem_1 = load_records_from_file(EXAMPLE_NAME, EXAMPLE_SCHEMA)
    assert len(records_rem_1) == len(records_before) - 1
    assert 1 not in records_rem_1["ID"]

    # Test 2: Remove non
    removed = remove_record(EXAMPLE_NAME, 1, EXAMPLE_SCHEMA)
    records_rem_2 = load_records_from_file(EXAMPLE_NAME, EXAMPLE_SCHEMA)
    assert removed is False
    assert records_rem_1.equals(records_rem_2)

    _delete_example_file_()
