import pandas as pd
import pyarrow as pa
import os
from choc_an_simulator.database_management import (
    add_records_to_file,
    load_records_from_file,
    _load_all_records_from_file_,
    _overwrite_records_to_file_,
    _convert_name_to_path_,
    _PARQUET_DIR_,
)

EXAMPLE_NAME = "test"
EXAMPLE_RECORDS = pd.DataFrame({"ID": [1, 2], "value": [1.1, 2.2]})
EXAMPLE_SCHEMA = pa.schema([("ID", pa.int64()), ("value", pa.float64())])


def save_example_file():
    """Save an example file for testing"""
    _overwrite_records_to_file_(EXAMPLE_NAME, EXAMPLE_RECORDS, EXAMPLE_SCHEMA)


def delete_example_file():
    """Delete file saved by save_example_file"""
    test_path = os.path.join(_PARQUET_DIR_, f"{EXAMPLE_NAME}.pkt")
    if os.path.exists(test_path):
        os.remove(test_path)


def test_add_records_to_file():
    save_example_file()
    add_records_to_file(EXAMPLE_NAME, EXAMPLE_RECORDS, EXAMPLE_SCHEMA)
    updated_records = load_records_from_file(EXAMPLE_NAME, EXAMPLE_SCHEMA)
    expected_records = pd.concat([EXAMPLE_RECORDS, EXAMPLE_RECORDS]).reset_index(
        drop=True
    )
    assert updated_records.equals(
        expected_records
    ), f"\n{expected_records}\n{updated_records}"
    delete_example_file()


def test_load_records_from_file():
    """Tests of the load_records_from_file function"""
    save_example_file()
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
    delete_example_file()
    # Test 5: Missiing file
    empty_records = load_records_from_file(EXAMPLE_NAME, EXAMPLE_SCHEMA)
    assert empty_records.empty
    delete_example_file()


def test_overwrite_records_to_file_():
    """Tests of the overwrite_records_to_file_ function"""
    save_example_file()
    records = pd.DataFrame({"ID": [3, 4], "value": [3.3, 4.4]})
    _overwrite_records_to_file_(EXAMPLE_NAME, records, EXAMPLE_SCHEMA)

    # Load records to check
    updated_records = _load_all_records_from_file_(EXAMPLE_NAME, EXAMPLE_SCHEMA)
    assert updated_records.equals(records), (
        "\n" + str(records) + "\n" + str(updated_records)
    )
    delete_example_file()
