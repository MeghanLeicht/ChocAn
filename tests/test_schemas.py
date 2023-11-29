"""Tests of the TableInfo class and schema constants in the schemas module."""
from typing import Dict

import pytest
import pandas as pd
import pyarrow as pa
from choc_an_simulator.schemas import TableInfo


@pytest.fixture()
def test_schema() -> pa.schema:
    """Generate a basic schema for testing"""
    return pa.schema([pa.field("number", pa.uint32()), pa.field("text", pa.string())])


@pytest.fixture()
def test_character_limit() -> Dict[str, range]:
    """Generate a basic character limit for testing"""
    return {"number": range(3, 5), "text": range(3, 10)}


@pytest.fixture()
def test_numeric_limit() -> Dict[str, range]:
    """Generate a basic numeric limit for testing"""
    return {"number": range(200, 50000)}


@pytest.fixture()
def test_info(test_schema, test_character_limit, test_numeric_limit) -> TableInfo:
    """Generate a basic TableInfo object for testing"""
    return TableInfo("test", test_schema, test_character_limit, test_numeric_limit)


class TestTableInfo:
    """Validate functionality and error handling of all TableInfo functions."""

    def test_table_info_initialization(self, test_schema, test_character_limit, test_numeric_limit):
        """Test initialization of the TableInfo class"""
        # Test 1: Normal Init
        test_table_info = TableInfo(
            "test",
            test_schema,
            numeric_limits=test_numeric_limit,
            character_limits=test_character_limit,
        )
        assert test_table_info.name == "test"
        assert test_table_info.schema == test_schema

    @pytest.mark.parametrize(
        "character_limits,numeric_limits",
        [
            # Bad character limit column
            ({"missing column": range(1, 1)}, {}),
            # Bad numeric limit column
            ({}, {"missing column": range(1, 1)}),
        ],
    )
    def test_table_info_initialization_invalid(self, test_schema, character_limits, numeric_limits):
        with pytest.raises(KeyError):
            TableInfo(
                name="test",
                schema=test_schema,
                character_limits=character_limits,
                numeric_limits=numeric_limits,
            )

    def test_index_col(self, test_info):
        """Test the check_dataframe function"""
        assert test_info.index_col() == "number"

    @pytest.mark.parametrize(
        "columns,includes",
        [
            # All correct columns
            (["number", "text"], True),
            # One correct column
            (["number"], True),
            # No columns
            ([], True),
            # Missing column
            (["missing_column"], False),
        ],
    )
    def test_includes_columns(self, columns, includes, test_info):
        """Test of the includes_columns function"""
        assert test_info.includes_columns(columns) == includes

    def test_check_columns(self, test_info):
        """Test of the check_columns function"""
        test_info.check_columns(["number", "text"])

    @pytest.mark.parametrize(
        "columns",
        [
            # Missing column
            (["number"]),
            # Extra column
            (["number", "test", "extra_column"]),
            # Incorrect column
            (["incorrect_column"]),
        ],
    )
    def test_check_columns_invalid(self, test_info, columns):
        """Parameterized tests of failed calls to check_columns()"""
        with pytest.raises(KeyError):
            test_info.check_columns(columns)

    def test_check_dataframe_valid(self, test_info):
        """Test a successful call to check_dataframe()"""
        test_info.check_dataframe(pd.DataFrame({"number": [200], "text": ["abc"]}))

    @pytest.mark.parametrize(
        "dataframe,error_type",
        [
            # Out of numeric range
            (pd.DataFrame({"number": [199], "text": ["abc"]}), ArithmeticError),
            # Out of character range
            (pd.DataFrame({"number": [199], "text": ["12"]}), ArithmeticError),
            # Column mismatch
            (pd.DataFrame({"digits": [200], "text": ["123"]}), KeyError),
            # Missing column
            (pd.DataFrame({"text": ["123"]}), KeyError),
            # Wrong type
            (pd.DataFrame({"number": ["a"], "text": ["123"]}), TypeError),
        ],
    )
    def test_check_dataframe_invalid(self, dataframe, error_type, test_info):
        """Parameterized tests of failed calls to check_dataframe()"""
        with pytest.raises(error_type):
            test_info.check_dataframe(dataframe)

    def test_check_series_valid(self, test_info):
        """Test a successful call to check_series()"""
        test_info.check_series(pd.Series({"number": 200, "text": "abc"}))

    @pytest.mark.parametrize(
        "series,error_type",
        [
            # Out of numeric range
            (pd.Series({"number": 199, "text": "abc"}), ArithmeticError),
            # Out of character range
            (pd.Series({"number": 199, "text": "12"}), ArithmeticError),
            # Column mismatch
            (pd.Series({"digits": 200, "text": "123"}), KeyError),
            # Missing column
            (pd.Series({"text": "123"}), KeyError),
            # Wrong type
            (pd.Series({"number": "a", "text": "123"}), TypeError),
        ],
    )
    def test_check_series_invalid(self, series, error_type, test_info):
        """Parameterized tests of failed calls to check_series()"""
        with pytest.raises(error_type):
            test_info.check_series(series)

    def test_check_field_valid(self, test_info):
        """Test a successful call to check_field()"""
        # Test 1: Passed check
        test_info.check_field(200, "number")

    @pytest.mark.parametrize(
        "field_name,field_val,error_type",
        [
            # Out of numeric range
            ("number", 199, ArithmeticError),
            # Out of character range
            ("text", "12", ArithmeticError),
            # Column mismatch
            ("digits", 200, KeyError),
            # Wrong type
            ("number", "a", TypeError),
        ],
    )
    def test_check_field_invalid(self, field_name, field_val, error_type, test_info):
        """Parameterized tests of failed calls to check_field()"""
        with pytest.raises(error_type):
            test_info.check_field(field_val, field_name)
