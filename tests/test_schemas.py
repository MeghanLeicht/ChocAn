"""Tests of the TableInfo class and schema constants in the schemas module."""
import pytest
import pandas as pd
import pyarrow as pa
from choc_an_simulator.schemas import TableInfo


class TestTableInfo:
    """Tests for the TableInfo class"""

    test_schema = pa.schema(
        [
            pa.field("number", pa.uint32(), nullable=False),
            pa.field("text", pa.string(), nullable=False),
        ]
    )
    test_character_limit = {"number": range(3, 5), "text": range(3, 10)}
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

    def test_check_dataframe(self):
        """Test the check_dataframe function"""
        test_info = TableInfo(
            "test", self.test_schema, self.test_character_limit, self.test_numeric_limit
        )
        # Test 1: Passed check
        test_info.check_dataframe(pd.DataFrame({"number": [200], "text": ["abc"]}))
        # Test 2: Failed numeric check
        with pytest.raises(ArithmeticError) as err_numeric:
            test_info.check_dataframe(pd.DataFrame({"number": [199], "text": ["abc"]}))
        assert "numeric" in str(err_numeric)
        # Test 3: Failed character check
        with pytest.raises(ArithmeticError) as err_character:
            test_info.check_dataframe(pd.DataFrame({"number": [200], "text": ["12"]}))
        assert "character" in str(err_character)
        # Test 4: Column mismatch
        with pytest.raises(KeyError):
            test_info.check_dataframe(pd.DataFrame({"digits": [200], "text": ["123"]}))
        # Test 5: Missing column
        with pytest.raises(KeyError):
            test_info.check_dataframe(pd.DataFrame({"text": ["123"]}))
        # Test 6: Type mismatch
        with pytest.raises(TypeError):
            test_info.check_dataframe(
                pd.DataFrame(
                    {"number": [200, 300, "hello"], "text": ["123", "123", "123"]}
                )
            )

    def test_check_series(self):
        """Test the check_series function"""
        test_info = TableInfo(
            "test", self.test_schema, self.test_character_limit, self.test_numeric_limit
        )
        # Test 1: Passed check
        test_info.check_series(pd.Series({"number": 200, "text": "abc"}))
        # Test 2: Failed numeric check
        with pytest.raises(ArithmeticError) as err_numeric:
            test_info.check_series(pd.Series({"number": 199, "text": "abc"}))
        assert "numeric" in str(err_numeric)
        # Test 3: Failed character check
        with pytest.raises(ArithmeticError) as err_character:
            test_info.check_series(pd.Series({"number": 200, "text": "12"}))
        assert "character" in str(err_character)
        # Test 4: Column mismatch
        with pytest.raises(KeyError):
            test_info.check_series(pd.Series({"digits": 200, "text": "123"}))
        # Test 5: Missing column
        with pytest.raises(KeyError):
            test_info.check_series(pd.Series({"text": "123"}))
        # Test 6: Type mismatch
        with pytest.raises(TypeError):
            test_info.check_series(pd.Series({"number": "hello", "text": "123"}))

    def test_check_field(self):
        """Test the check_field function"""
        test_info = TableInfo(
            "test", self.test_schema, self.test_character_limit, self.test_numeric_limit
        )
        # Test 1: Passed check
        test_info.check_field(200, "number")
        # Test 2: Failed numeric check
        with pytest.raises(ArithmeticError) as err_numeric:
            test_info.check_field(199, "number")
        assert "numeric" in str(err_numeric)
        # Test 3: Failed character check
        with pytest.raises(ArithmeticError) as err_character:
            test_info.check_field("12", "text")
        assert "character" in str(err_character)
        # Test 4: Column mismatch
        with pytest.raises(KeyError):
            test_info.check_field(200, "digits")
        # Test 5: Type mismatch
        with pytest.raises(TypeError):
            test_info.check_field("hello", "number")
