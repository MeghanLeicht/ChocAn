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
    _convert_name_to_path_,
    _check_schema_columns_,
)

TEST_NAME = "test"
TEST_RECORDS = pd.DataFrame({"ID": [1, 2], "value": [1.1, 2.2]})
TEST_SCHEMA = pa.schema([("ID", pa.int64()), ("value", pa.float64())])
MISMATCHED_TEST_SCHEMA = pa.schema([("mismatched", pa.int64()), ("test", pa.float64())])


@pytest.fixture(scope="function")
def test_file():
    """Fixture to setup and teardown an test file"""
    _overwrite_records_to_file_(TEST_NAME, TEST_RECORDS, TEST_SCHEMA)
    yield TEST_NAME
    test_path = os.path.join(_PARQUET_DIR_, f"{TEST_NAME}.pkt")
    if os.path.exists(test_path):
        os.remove(test_path)


@pytest.fixture(scope="function")
def corrupted_test_file():
    """Fixture to setup and teardown an test file"""
    test_name = f"{TEST_NAME}_corrupted"
    test_path = os.path.join(_PARQUET_DIR_, f"{test_name}.pkt")
    _overwrite_records_to_file_(TEST_NAME, TEST_RECORDS, TEST_SCHEMA)
    with open(test_path, "w") as f:
        f.write("some extra garbage")
    yield test_name
    if os.path.exists(test_path):
        os.remove(test_path)


class TestAddRecordsToFile:
    """Tests for the add_records_to_file function."""

    new_records = pd.DataFrame({"ID": [3, 4], "value": [1.1, 2.2]})

    @classmethod
    def test_add_normal(cls, test_file):
        """Test normal add to file."""
        # Test 1: Normal add
        add_records_to_file(test_file, cls.new_records, TEST_SCHEMA)
        updated_records = load_records_from_file(TEST_NAME, TEST_SCHEMA)
        expected_records = pd.concat([TEST_RECORDS, cls.new_records]).reset_index(
            drop=True
        )
        assert updated_records.equals(
            expected_records
        ), f"\n{expected_records}\n{updated_records}"

    @classmethod
    def test_add_duplicate(cls, test_file):
        """Test add duplicate entries"""
        with pytest.raises(ValueError):
            add_records_to_file(test_file, TEST_RECORDS, TEST_SCHEMA)

    @classmethod
    def test_add_corrupted(cls, corrupted_test_file):
        """Test add to a corrupted file"""
        with pytest.raises(pa.ArrowInvalid):
            add_records_to_file(corrupted_test_file, cls.new_records, TEST_SCHEMA)

    @classmethod
    def test_add_schema_mismatch(cls, test_file):
        """Test add record with a mismatched schema"""
        mismatched_records = pd.DataFrame({"mismatched": [3, 4], "test": [1.1, 2.2]})
        mismatched_records_correct_index = pd.DataFrame(
            {"ID": [3, 4], "test": [1.1, 2.2]}
        )

        wrong_type_records = pd.DataFrame({"ID": [3, 4], "value": ["1.1", "2.2"]})
        # Test 1: Add records with incorrect columns
        with pytest.raises(KeyError) as k:
            add_records_to_file(
                test_file, mismatched_records_correct_index, TEST_SCHEMA
            )
        print("K: ", k)
        # Test 2: Mismatched schema / file
        with pytest.raises(KeyError):
            add_records_to_file(test_file, cls.new_records, MISMATCHED_TEST_SCHEMA)
        # Test 3: Mismatched types
        with pytest.raises(pa.ArrowInvalid):
            add_records_to_file(test_file, wrong_type_records, TEST_SCHEMA)
        # Test 4: Matching schema / records, mismatched file
        with pytest.raises(KeyError):
            add_records_to_file(test_file, mismatched_records, MISMATCHED_TEST_SCHEMA)

    @classmethod
    def test_add_read_err(cls, test_file, mocker):
        """Test adding records to an unreadable file"""
        mocker.patch("pyarrow.parquet.read_table", side_effect=pa.ArrowIOError)
        with pytest.raises(pa.ArrowIOError):
            add_records_to_file(test_file, cls.new_records, TEST_SCHEMA)

    @classmethod
    def test_add_write_err(cls, test_file, mocker):
        """Test adding records to an unwriteable file"""
        mocker.patch("pyarrow.parquet.write_table", side_effect=pa.ArrowIOError)
        with pytest.raises(pa.ArrowIOError):
            add_records_to_file(test_file, cls.new_records, TEST_SCHEMA)


class TestLoadRecordsFromFile:
    """Tests of the load_records_from_file function"""

    @classmethod
    def test_load_all(cls, test_file):
        """Test loading with no filters"""
        all_records = load_records_from_file(test_file, TEST_SCHEMA)
        assert TEST_RECORDS.equals(all_records)

    @classmethod
    def test_load_corrupted(cls, corrupted_test_file):
        """Test loading a corrupted file"""
        with pytest.raises(pa.ArrowInvalid):
            load_records_from_file(corrupted_test_file, TEST_SCHEMA)

    @classmethod
    def test_load_schema_mismatch(cls, test_file):
        """Test loading a file with the incorrect schema"""
        with pytest.raises(KeyError):
            load_records_from_file(test_file, MISMATCHED_TEST_SCHEMA)

    @classmethod
    def test_load_io_err(cls, test_file, mocker):
        """Test loading an inacessible file"""
        mocker.patch("pyarrow.parquet.read_table", side_effect=pa.ArrowIOError)
        with pytest.raises(pa.ArrowIOError):
            load_records_from_file(test_file, TEST_SCHEMA)

    @classmethod
    def test_load_with_valid_filters(cls, test_file):
        """Test loading with valid filters"""
        # Test 1: Equality filter
        eq_records = load_records_from_file(test_file, TEST_SCHEMA, eq_cols={"ID": 1})
        assert TEST_RECORDS[TEST_RECORDS["ID"] == 1].equals(eq_records)
        # Test 2: Less-than filter
        lt_records = load_records_from_file(
            test_file, TEST_SCHEMA, lt_cols={"value": 2.0}
        )
        assert TEST_RECORDS[TEST_RECORDS["value"] < 2.0].equals(lt_records)
        # Test 3: Greater-than filter
        lt_records = load_records_from_file(
            test_file, TEST_SCHEMA, gt_cols={"value": 2.0}
        )
        assert TEST_RECORDS[TEST_RECORDS["value"] > 2.0].equals(lt_records)

    @classmethod
    def test_load_with_invalid_filters(cls, test_file):
        """Test loading with invalid filters"""
        # Test 1: Invalid comparisons
        with pytest.raises(TypeError):

            class no_eq:
                """Example of a class that doesn't support equality"""

                def __eq__(self, other):
                    raise TypeError(
                        "Equality between no_eq and {type(other)} not supported"
                    )

            load_records_from_file(test_file, TEST_SCHEMA, eq_cols={"ID": no_eq()})
        with pytest.raises(TypeError):
            load_records_from_file(test_file, TEST_SCHEMA, lt_cols={"value": "a"})
        with pytest.raises(TypeError):
            load_records_from_file(test_file, TEST_SCHEMA, gt_cols={"value": "a"})

        # Test 2: Invalid columns
        with pytest.raises(KeyError):
            load_records_from_file(test_file, TEST_SCHEMA, eq_cols={"invalid": 1})
        with pytest.raises(KeyError):
            load_records_from_file(test_file, TEST_SCHEMA, lt_cols={"invalid": 1})
        with pytest.raises(KeyError):
            load_records_from_file(test_file, TEST_SCHEMA, gt_cols={"invalid": 1})

    @classmethod
    def test_load_missing_file(cls):
        """Test loading from a file that doesn't exist."""
        empty_records = load_records_from_file("missing", TEST_SCHEMA)
        assert empty_records.empty


class TestUpdateRecord:
    """Tests of the update_record function."""

    @classmethod
    def test_update_normal(cls, test_file):
        """Test normal record update."""
        updated_record = update_record(test_file, 2, TEST_SCHEMA, value=2.3)
        loaded_record = load_records_from_file(
            test_file, TEST_SCHEMA, eq_cols={"ID": 2}
        ).iloc[0]
        assert (updated_record == loaded_record).all()

    @classmethod
    def test_update_no_kwarg(cls, test_file):
        """Test updating without providing any updates."""
        with pytest.raises(AssertionError):
            update_record(test_file, 2, TEST_SCHEMA)

    @classmethod
    def test_update_bad_index(cls, test_file):
        """Test updating an entry with an index that isn't in the dataset"""
        with pytest.raises(IndexError):
            update_record(test_file, 3, TEST_SCHEMA, value=3.3)

    @classmethod
    def test_update_bad_column(cls, test_file):
        """Test updating a field in column that isn't in the dataset"""
        with pytest.raises(KeyError):
            update_record(test_file, 2, TEST_SCHEMA, bad_column_name="hello")

    @classmethod
    @pytest.mark.filterwarnings("ignore: Setting an item of incompatible dtype")
    def test_update_type_mismatch(cls, test_file):
        """Test updating a field with a different type than in the schema"""
        with pytest.raises(pa.ArrowInvalid):
            update_record(test_file, 2, TEST_SCHEMA, value="hello")

    @classmethod
    def test_update_schema_mismatch(cls, test_file):
        """Test updating with mismatched file / schema"""
        # Test 1: Mismatched schema / file
        with pytest.raises(KeyError):
            update_record(test_file, 2, MISMATCHED_TEST_SCHEMA, value=2.2)

    @classmethod
    def test_update_corrupted(cls, corrupted_test_file):
        """Test add record with mismatched file / schema"""
        with pytest.raises(pa.ArrowInvalid):
            update_record(corrupted_test_file, 2, TEST_SCHEMA, value=2.2)

    @classmethod
    def test_update_read_err(cls, test_file, mocker):
        """Test updating an unreadable file"""
        mocker.patch("pyarrow.parquet.read_table", side_effect=pa.ArrowIOError)
        with pytest.raises(pa.ArrowIOError):
            update_record(test_file, 2, TEST_SCHEMA, value=2.2)

    @classmethod
    def test_update_write_err(cls, test_file, mocker):
        """Test updating an unwriteable file"""
        mocker.patch("pyarrow.parquet.write_table", side_effect=pa.ArrowIOError)
        with pytest.raises(pa.ArrowIOError):
            update_record(test_file, 2, TEST_SCHEMA, value=2.2)


class TestRemoveRecord:
    """Tests of the remove_record function"""

    @classmethod
    def test_remove_normal(cls, test_file):
        """Test normal removal"""
        records_before = load_records_from_file(test_file, TEST_SCHEMA)
        assert 1 in records_before["ID"]
        removed = remove_record(test_file, 1, TEST_SCHEMA)
        assert removed
        records_after = load_records_from_file(test_file, TEST_SCHEMA)
        assert len(records_after) == len(records_before) - 1
        assert 1 not in records_after["ID"]

    @classmethod
    def test_remove_missing_index(cls, test_file):
        """Test removal at a non-existant index"""
        records_before = load_records_from_file(test_file, TEST_SCHEMA)
        removed = remove_record(test_file, 3, TEST_SCHEMA)
        records_after = load_records_from_file(test_file, TEST_SCHEMA)
        assert removed is False
        assert records_before.equals(records_after)

    @classmethod
    def test_remove_corrupted(cls, corrupted_test_file):
        """Test removing from a corrupted file"""
        with pytest.raises(pa.ArrowInvalid):
            remove_record(corrupted_test_file, 2, TEST_SCHEMA)

    @classmethod
    def test_remove_read_err(cls, test_file, mocker):
        """Test removing from an unreadable file"""
        mocker.patch("pyarrow.parquet.read_table", side_effect=pa.ArrowIOError)
        with pytest.raises(pa.ArrowIOError):
            remove_record(test_file, 2, TEST_SCHEMA)

    @classmethod
    def test_remove_write_err(cls, test_file, mocker):
        """Test removing from an unwriteable file"""
        mocker.patch("pyarrow.parquet.write_table", side_effect=pa.ArrowIOError)
        with pytest.raises(pa.ArrowIOError):
            remove_record(test_file, 1, TEST_SCHEMA)

    @classmethod
    def test_remove_mismatched_schema(cls, test_file):
        with pytest.raises(KeyError):
            remove_record(test_file, 1, MISMATCHED_TEST_SCHEMA)


class TestOverwriteRecordsToFile:
    """Tests of the _overwrite_records_to_file_ function"""

    new_records = pd.DataFrame({"ID": [3, 4], "value": [3.3, 4.4]})

    @classmethod
    def test_overwrite_normal(cls, test_file):
        """Tests of the overwrite_records_to_file_ function"""
        _overwrite_records_to_file_(test_file, cls.new_records, TEST_SCHEMA)

        # Load records to check equality
        updated_records = _load_all_records_from_file_(test_file, TEST_SCHEMA)
        assert updated_records.equals(cls.new_records), (
            "\n" + str(cls.new_records) + "\n" + str(updated_records)
        )

    @classmethod
    def test_overwrite_schema_mismatch(cls, test_file):
        """Test overwrite record with a mismatched schema"""
        mismatched_records = pd.DataFrame({"mismatched": [3, 4], "test": [1.1, 2.2]})
        with pytest.raises(KeyError):
            _overwrite_records_to_file_(test_file, mismatched_records, TEST_SCHEMA)

    @classmethod
    def test_overwrite_io_err(cls, test_file, mocker):
        mocker.patch("pyarrow.parquet.write_table", side_effect=pa.ArrowIOError)
        with pytest.raises(pa.ArrowIOError):
            _overwrite_records_to_file_(test_file, cls.new_records, TEST_SCHEMA)


def test_convert_name_to_path():
    """Test of the _convert_name_to_path_ function"""
    assert _convert_name_to_path_("name") == f"{_PARQUET_DIR_}/name.pkt"


def test_check_schema_columns():
    """Test of the _check_schema_columns_ function"""
    assert _check_schema_columns_(TEST_SCHEMA, TEST_RECORDS) is True
    assert _check_schema_columns_(MISMATCHED_TEST_SCHEMA, TEST_RECORDS) is False
