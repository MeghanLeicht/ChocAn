import pandas as pd
import pyarrow as pa
import os
import pytest
from choc_an_simulator.schemas import TableInfo
from choc_an_simulator.database_management import (
    add_records_to_file,
    load_records_from_file,
    update_record,
    remove_record,
    _load_all_records_from_file_,
    _overwrite_records_to_file_,
    _PARQUET_DIR_,
    _convert_name_to_path_,
)

TEST_NAME = "test"
TEST_RECORDS = pd.DataFrame({"ID": [1, 2], "value": [1.1, 2.2]})
MISMATCHED_TEST_RECORDS = pd.DataFrame({"mismatched": [1, 2], "records": [1.1, 2.2]})
TEST_TABLE_INFO = TableInfo(
    name="test",
    schema=pa.schema([("ID", pa.int64()), ("value", pa.float64())]),
    numeric_limits={"value": range(0, 3)},
)
MISMATCHED_TEST_TABLE_INFO = TableInfo(
    name="test_mismatched",
    schema=pa.schema([("mismatched", pa.int64()), ("records", pa.float64())]),
)


@pytest.fixture(scope="function")
def test_file():
    """Fixture to setup and teardown an test file"""
    _overwrite_records_to_file_(TEST_RECORDS, TEST_TABLE_INFO)
    yield TEST_NAME
    test_path = os.path.join(_PARQUET_DIR_, f"{TEST_NAME}.pkt")
    if os.path.exists(test_path):
        os.remove(test_path)


@pytest.fixture(scope="function")
def corrupted_test_file():
    """Fixture to setup and teardown an test file"""
    test_name = f"{TEST_NAME}"
    test_path = os.path.join(_PARQUET_DIR_, f"{test_name}.pkt")
    _overwrite_records_to_file_(TEST_RECORDS, TEST_TABLE_INFO)
    with open(test_path, "w") as f:
        f.write("some extra garbage")
    yield test_name
    if os.path.exists(test_path):
        os.remove(test_path)


class TestAddRecordsToFile:
    """Tests for the add_records_to_file function."""

    new_records = pd.DataFrame({"ID": [3, 4], "value": [1.1, 2.2]})

    def test_add_records_to_file_normal_conditions(self, test_file):
        """Test normal add to file."""
        # Test 1: Normal add
        add_records_to_file(self.new_records, TEST_TABLE_INFO)
        updated_records = load_records_from_file(TEST_TABLE_INFO)
        expected_records = pd.concat([TEST_RECORDS, self.new_records]).reset_index(
            drop=True
        )
        assert updated_records.equals(
            expected_records
        ), f"\n{expected_records}\n{updated_records}"

    def test_add_records_to_file_duplicate_entries(self, test_file):
        """Test add duplicate entries"""
        with pytest.raises(ValueError):
            add_records_to_file(TEST_RECORDS, TEST_TABLE_INFO)

    def test_add_records_to_file_corrupted_file(self, corrupted_test_file):
        """Test add to a corrupted file"""
        with pytest.raises(pa.ArrowInvalid):
            add_records_to_file(self.new_records, TEST_TABLE_INFO)

    def test_add_records_to_file_schema_mismatch(self, test_file):
        """Test add record with a mismatched schema"""
        mismatched_records = pd.DataFrame({"mismatched": [3, 4], "test": [1.1, 2.2]})
        mismatched_records_correct_index = pd.DataFrame(
            {"ID": [3, 4], "test": [1.1, 2.2]}
        )

        wrong_type_records = pd.DataFrame({"ID": [3, 4], "value": ["1.1", "2.2"]})
        # Test 1: Add records with incorrect columns
        with pytest.raises(KeyError):
            add_records_to_file(mismatched_records_correct_index, TEST_TABLE_INFO)
        with pytest.raises(KeyError):
            add_records_to_file(mismatched_records, TEST_TABLE_INFO)
        # Test 2: Mismatched types
        with pytest.raises(TypeError):
            add_records_to_file(wrong_type_records, TEST_TABLE_INFO)

    def test_add_records_to_file_read_error(self, test_file, mocker):
        """Test adding records to an unreadable file"""
        mocker.patch("pyarrow.parquet.read_table", side_effect=pa.ArrowIOError)
        with pytest.raises(pa.ArrowIOError):
            add_records_to_file(self.new_records, TEST_TABLE_INFO)

    def test_add_records_to_file_write_error(self, test_file, mocker):
        """Test adding records to an unwriteable file"""
        mocker.patch("pyarrow.parquet.write_table", side_effect=pa.ArrowIOError)
        with pytest.raises(pa.ArrowIOError):
            add_records_to_file(self.new_records, TEST_TABLE_INFO)


class TestLoadRecordsFromFile:
    """Tests of the load_records_from_file function"""

    def test_load_records_from_file_all_records(self, test_file):
        """Test loading with no filters"""
        all_records = load_records_from_file(TEST_TABLE_INFO)
        assert TEST_RECORDS.equals(all_records)

    def test_load_records_from_file_corrupted_file(self, corrupted_test_file):
        """Test loading a corrupted file"""
        with pytest.raises(pa.ArrowInvalid):
            load_records_from_file(TEST_TABLE_INFO)

    # def test_load_records_from_file_schema_mismatch(self, test_file):
    #    """Test loading a file with the incorrect schema"""
    #    with pytest.raises(KeyError):
    #        load_records_from_file(M)

    def test_load_records_from_file_io_error(self, test_file, mocker):
        """Test loading an inacessible file"""
        mocker.patch("pyarrow.parquet.read_table", side_effect=pa.ArrowIOError)
        with pytest.raises(pa.ArrowIOError):
            load_records_from_file(TEST_TABLE_INFO)

    def test_load_records_from_file_valid_filters(self, test_file):
        """Test loading with valid filters"""
        # Test 1: Equality filter
        eq_records = load_records_from_file(TEST_TABLE_INFO, eq_cols={"ID": 1})
        assert TEST_RECORDS[TEST_RECORDS["ID"] == 1].equals(eq_records)
        # Test 2: Less-than filter
        lt_records = load_records_from_file(TEST_TABLE_INFO, lt_cols={"value": 2.0})
        assert TEST_RECORDS[TEST_RECORDS["value"] < 2.0].equals(lt_records)
        # Test 3: Greater-than filter
        lt_records = load_records_from_file(TEST_TABLE_INFO, gt_cols={"value": 2.0})
        assert TEST_RECORDS[TEST_RECORDS["value"] > 2.0].equals(lt_records)

    def test_load_records_from_file_invalid_filters(self, test_file):
        """Test loading with invalid filters"""
        # Test 1: Invalid comparisons
        with pytest.raises(TypeError):

            class NoEq:
                """Example of a class that doesn't support equality"""

                def __eq__(self, other):
                    raise TypeError(
                        "Equality between no_eq and {type(other)} not supported"
                    )

            load_records_from_file(TEST_TABLE_INFO, eq_cols={"ID": NoEq()})
        with pytest.raises(TypeError):
            load_records_from_file(TEST_TABLE_INFO, lt_cols={"value": "a"})
        with pytest.raises(TypeError):
            load_records_from_file(TEST_TABLE_INFO, gt_cols={"value": "a"})

        # Test 2: Invalid columns
        with pytest.raises(KeyError):
            load_records_from_file(TEST_TABLE_INFO, eq_cols={"invalid": 1})
        with pytest.raises(KeyError):
            load_records_from_file(TEST_TABLE_INFO, lt_cols={"invalid": 1})
        with pytest.raises(KeyError):
            load_records_from_file(TEST_TABLE_INFO, gt_cols={"invalid": 1})

    def test_load_records_from_file_missing_file(self):
        """Test loading from a file that doesn't exist."""
        empty_records = load_records_from_file(TEST_TABLE_INFO)
        assert empty_records.empty


class TestUpdateRecord:
    """Tests of the update_record function."""

    def test_update_record__normal_update(self, test_file):
        """Test normal record update."""
        updated_record = update_record(2, TEST_TABLE_INFO, value=2.3)
        loaded_record = load_records_from_file(TEST_TABLE_INFO, eq_cols={"ID": 2}).iloc[
            0
        ]
        assert (updated_record == loaded_record).all()

    def test_update_record__no_keywordargs(self, test_file):
        """Test updating without providing any updates."""
        with pytest.raises(AssertionError):
            update_record(2, TEST_TABLE_INFO)

    def test_update_record__invalid_index(self, test_file):
        """Test updating an entry with an index that isn't in the dataset"""
        with pytest.raises(IndexError):
            update_record(3, TEST_TABLE_INFO, value=3.3)

    def test_update_record__invalid_column(self, test_file):
        """Test updating a field in column that isn't in the dataset"""
        with pytest.raises(KeyError):
            update_record(2, TEST_TABLE_INFO, bad_column_name="hello")

    @pytest.mark.filterwarnings("ignore: Setting an item of incompatible dtype")
    def test_update_record__type_mismatch(self, test_file):
        """Test updating a field with a different type than in the schema"""
        with pytest.raises(TypeError):
            update_record(2, TEST_TABLE_INFO, value="hello")

    # def test_update_record__schema_mismatch(self, test_file):
    #    """Test updating with mismatched file / schema"""
    #    # Test 1: Mismatched schema / file
    #    with pytest.raises(KeyError):
    #        update_record(2, MISMATCHED_TEST_TABLE_INFO, value=2.2)

    def test_update_record__corrupted_file(self, corrupted_test_file):
        """Test add record with mismatched file / schema"""
        with pytest.raises(pa.ArrowInvalid):
            update_record(2, TEST_TABLE_INFO, value=2.2)

    def test_update_record__read_error(self, test_file, mocker):
        """Test updating an unreadable file"""
        mocker.patch("pyarrow.parquet.read_table", side_effect=pa.ArrowIOError)
        with pytest.raises(pa.ArrowIOError):
            update_record(2, TEST_TABLE_INFO, value=2.2)

    def test_update_record__write_error(self, test_file, mocker):
        """Test updating an unwriteable file"""
        mocker.patch("pyarrow.parquet.write_table", side_effect=pa.ArrowIOError)
        with pytest.raises(pa.ArrowIOError):
            update_record(2, TEST_TABLE_INFO, value=2.2)


class TestRemoveRecord:
    """Tests of the remove_record function"""

    def test_remove_record__normal_removal(self, test_file):
        """Test normal removal"""
        records_before = load_records_from_file(TEST_TABLE_INFO)
        assert 1 in records_before["ID"]
        removed = remove_record(1, TEST_TABLE_INFO)
        assert removed
        records_after = load_records_from_file(TEST_TABLE_INFO)
        assert len(records_after) == len(records_before) - 1
        assert 1 not in records_after["ID"]

    def test_remove_record__missing_index(self, test_file):
        """Test removal at a non-existant index"""
        records_before = load_records_from_file(TEST_TABLE_INFO)
        removed = remove_record(3, TEST_TABLE_INFO)
        records_after = load_records_from_file(TEST_TABLE_INFO)
        assert removed is False
        assert records_before.equals(records_after)

    def test_remove_record__corrupted_file(self, corrupted_test_file):
        """Test removing from a corrupted file"""
        with pytest.raises(pa.ArrowInvalid):
            remove_record(2, TEST_TABLE_INFO)

    def test_remove_record__read_error(self, test_file, mocker):
        """Test removing from an unreadable file"""
        mocker.patch("pyarrow.parquet.read_table", side_effect=pa.ArrowIOError)
        with pytest.raises(pa.ArrowIOError):
            remove_record(2, TEST_TABLE_INFO)

    def test_remove_record__write_error(self, test_file, mocker):
        """Test removing from an unwriteable file"""
        mocker.patch("pyarrow.parquet.write_table", side_effect=pa.ArrowIOError)
        with pytest.raises(pa.ArrowIOError):
            remove_record(1, TEST_TABLE_INFO)

    # def test_remove_record__schema_mismatch(self, test_file):
    #    with pytest.raises(KeyError):
    #        remove_record(1, MISMATCHED_TEST_TABLE_INFO)


class TestOverwriteRecordsToFile:
    """Tests of the _overwrite_records_to_file_ function"""

    new_records = pd.DataFrame({"ID": [3, 4], "value": [2.0, 1.0]})

    def test_overwrite_records_to_file_normal_overwrite(self, test_file):
        """Tests of the overwrite_records_to_file_ function"""
        _overwrite_records_to_file_(self.new_records, TEST_TABLE_INFO)

        # Load records to check equality
        updated_records = _load_all_records_from_file_(TEST_TABLE_INFO)
        assert updated_records.equals(self.new_records), (
            "\n" + str(self.new_records) + "\n" + str(updated_records)
        )

    def test_overwrite_records_to_file_schema_mismatch(self, test_file):
        """Test overwrite record with a mismatched schema"""
        mismatched_records = pd.DataFrame({"mismatched": [3, 4], "test": [1.1, 2.2]})
        with pytest.raises(KeyError):
            _overwrite_records_to_file_(mismatched_records, TEST_TABLE_INFO)

    def test_overwrite_records_to_file_io_error(self, test_file, mocker):
        mocker.patch("pyarrow.parquet.write_table", side_effect=pa.ArrowIOError)
        with pytest.raises(pa.ArrowIOError):
            _overwrite_records_to_file_(self.new_records, TEST_TABLE_INFO)


def test_convert_name_to_path():
    """Test of the _convert_name_to_path_ function"""
    assert _convert_name_to_path_("name") == os.path.join(_PARQUET_DIR_, "name.pkt")
