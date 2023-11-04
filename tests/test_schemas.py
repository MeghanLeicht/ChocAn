"""Tests of the TableInfo class and schema constants in the schemas module."""
import pytest
import pandas as pd
import pyarrow as pa
from choc_an_simulator.schemas import (
    TableInfo,
    # PROVIDER_DIRECTORY_INFO,
    # MEMBER_INFO,
    # PROVIDER_INFO,
    # SERVICE_LOG_INFO,
)


class TestTableInfo:
    test_schema = pa.schema(
        [
            pa.field("number", pa.uint32(), nullable=False),
            pa.field("text", pa.string(), nullable=False),
        ]
    )
    test_character_limit = {"number": range(3, 5), "text": range(5, 10)}
    test_numeric_limit = {
        "number": range(200, 50000),
    }

    def test_table_info_initialization(self):
        """Test initialization of the TableInfo class"""
        # Test 1: Normal Init
        test_table_info = TableInfo(
            name="test",
            schema=self.test_schema,
            numeric_limits=self.test_numeric_limit,
            character_limits=self.test_character_limit,
        )
        assert test_table_info.name == "test"
        assert test_table_info.schema == self.test_schema
        # Test 2: Bad character limit
        with pytest.raises(KeyError):
            test_table_info = TableInfo(
                name="test",
                schema=self.test_schema,
                character_limits={"missing column": range(1, 1)},
            )
        # Test 3: Bad numeric limit
        with pytest.raises(KeyError):
            test_table_info = TableInfo(
                name="test",
                schema=self.test_schema,
                numeric_limits={"missing column": range(1, 1)},
            )


def test_check_dataframe():
    example_info = TableInfo(
        "example_info",
        schema=pa.schema([pa.field("a", pa.uint8()), pa.field("b", pa.string())]),
        character_limits={"b": range(3, 10)},
        numeric_limits={"a": range(0, 99)},
    )
    example_info.check_dataframe(pd.DataFrame({"a": [0], "b": ["123"]}))
    with pytest.raises(ArithmeticError):
        example_info.check_dataframe(pd.DataFrame({"a": [0], "b": ["12"]}))
    with pytest.raises(ArithmeticError):
        example_info.check_dataframe(pd.DataFrame({"a": [100], "b": ["123"]}))
