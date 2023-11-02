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
