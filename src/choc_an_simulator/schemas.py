"""
Defines schemas for various database tables used in the ChocAn data management system.

This module contains predefined schemas for different types of data, such as provider information,
member details, and service logs. These schemas are used to ensure data consistency and integrity
when interacting with the database.

Examples-
    # 1. Get a full list of members
    from database_management import load_records_from_file
    from schemas import MEMBER_INFO
    def get_full_member_list():
        members = load_records_from_file(MEMBER_INFO)
"""
from typing import Any, List
import pyarrow as pa
import pandas as pd
from dataclasses import dataclass, field


@dataclass(frozen=True)
class TableInfo:
    """Info for one database file."""

    name: str
    schema: pa.Schema
    # Limits on character length (e.g. only 9 digit numbers)
    character_limits: dict[str, range] = field(default_factory=lambda: {})
    # Limits on numeric length (e.g. only numbers between 0 and 99)
    numeric_limits: dict[str, range] = field(default_factory=lambda: {})

    def __post_init__(self):
        """
        Validates the character and numeric limits against the schema fields.

        Ensures that the specified limits correspond to existing fields in the schema.
        Raises KeyError if a limit is set for a non-existent field.
        """
        for col_name in self.character_limits.keys():
            if col_name not in self.schema.names:
                raise KeyError(
                    f"Character limit column {col_name} could not be found in schema {self.name}"
                )
        for col_name in self.numeric_limits.keys():
            if col_name not in self.schema.names:
                raise KeyError(
                    f"Numeric limit column {col_name} could not be found in schema {self.name}"
                )

    def index_col(self) -> str:
        """
        Retrieves the name of the index (first) column for the table.

        Returns-
            The name of the first column in the schema, used as the index.
        """
        return self.schema.names[0]

    def includes_columns(self, columns: List[str]) -> bool:
        """
        Checks if the schema includes all specified columns.

        Args-
            columns (List[str]): A list of column names to check.

        Returns-
            True if all columns are present in the schema, False otherwise.
        """
        return all(col in self.schema.names for col in columns)

    def check_columns(self, columns: List[str]) -> None:
        """
        Ensures that the given columns match the schema's columns.

        Args-
            columns (List[str]): A list of column names to verify.

        Raises-
            KeyError: If there's a mismatch between the data columns and schema columns.
        """
        if set(self.schema.names) != set(columns):
            raise KeyError("Data and schema have mismatched columns.")

    def check_dataframe(self, data: pd.DataFrame) -> None:
        """
        Validates a DataFrame against the table's schema.

        Args-
            data (pd.DataFrame): The DataFrame to validate.

        Raises-
            KeyError: If columns in the DataFrame don't match the schema.
            TypeError: If a value's type is incompatible with the schema.
            ArithmeticError: If a value violates character or numeric limits.
        """
        data.apply(lambda row: self.check_series(row), axis=1)  # type: ignore

    def check_series(self, data: pd.Series) -> None:
        """
        Validates a single field value against the schema.

        Args-
            value (Any): The value to validate.
            field_name (str): The name of the field to validate against.

        Raises-
            KeyError: Field doesn't exist in the schema.
            TypeError: Value's type is incompatible with the schema.
            ArithmeticError: Value violates character or numeric limits.
        """
        self.check_columns(list(data.index.values))
        for field_name, value in data.items():
            self.check_field(value, str(field_name))

    def check_field(self, value: Any, field_name: str) -> None:
        """
        Check a single field value for alignment with the schema.

        Args-
            value: Value to check for compatibility with field
            field_name: Name of the schema field to check the value against

        Raises-
            KeyError: Field doesn't exist in schema
            TypeError: Value type is incompatible with field
            ArithmeticError: Value doesn't adhere to field's character or numeric limit.
        """
        self._check_field_exists(field_name)
        self._check_type(field_name, value)
        self._check_character_limit(field_name, value)
        self._check_numeric_limit(field_name, value)

    def _check_field_exists(self, field_name: str):
        """Raise a KeyError if a given field doesn't exist in the schema."""
        if field_name not in self.schema.names:
            raise KeyError(
                f"Field Name {field_name} does not exist in {self.name} schema."
            )

    def _check_type(self, field_name: str, value: Any):
        """Raise an Arithmetic error if a given field/value pair has an incompatible type."""
        field: pa.Field = self.schema.field(field_name)
        try:
            _ = pa.array([value], type=field.type)
        except pa.ArrowInvalid as err_invalid:
            raise TypeError(
                f"Value {value} has wrong type for column. \n"
                f"{field_name} ({type(value)} -> {field.type})\n"
                f"{err_invalid}"
            )

    def _check_character_limit(self, field_name: str, value: Any):
        """Raise an Arithmetic error if a given field/value pair exceeds its character limit."""
        if field_name not in self.character_limits.keys():
            return
        val_len = len(str(value))
        limit_range = self.character_limits[field_name]
        if (val_len < limit_range.start) or (val_len > limit_range.stop):
            print(type(value))
            raise ArithmeticError(
                f"{field_name} value {value} is outside character limit {limit_range} "
            )

    def _check_numeric_limit(self, field_name: str, value: Any):
        """Raise an Arithmetic error if a given field/value pair exceeds its numeric limit."""
        if field_name not in self.numeric_limits.keys():
            return
        limit_range = self.numeric_limits[field_name]
        if (value < limit_range.start) or (value > limit_range.stop):
            raise ArithmeticError(
                f"{field_name} value {value} is outside numeric limit {limit_range} "
            )


"""All services offered by ChocAn, and their codes."""
PROVIDER_DIRECTORY_INFO = TableInfo(
    name="provider_directory",
    schema=pa.schema(
        [
            pa.field("service_id", pa.int64(), nullable=False),
            pa.field("service_name", pa.string(), nullable=False),
            pa.field("price_dollars", pa.int64(), nullable=False),
            pa.field("price_cents", pa.int64(), nullable=False),
        ]
    ),
    character_limits={"service_id": range(6, 6), "service_name": range(1, 20)},
    numeric_limits={"price_cents": range(1, 99)},
)

"""All current ChocAn members."""
MEMBER_INFO = TableInfo(
    name="members",
    schema=pa.schema(
        [
            pa.field("member_id", pa.int64(), nullable=False),
            pa.field("name", pa.string(), nullable=False),
            pa.field("address", pa.string(), nullable=False),
            pa.field("city", pa.string(), nullable=False),
            pa.field("state", pa.string(), nullable=False),
            pa.field("zipcode", pa.int64(), nullable=False),
            pa.field("suspended", pa.bool_(), nullable=False),
        ]
    ),
    character_limits={
        "member_id": range(9, 9),
        "name": range(1, 25),
        "address": range(1, 25),
        "city": range(1, 14),
        "state": range(2, 2),
        "zipcode": range(5, 5),
    },
)

"""All current ChocAn providers & managers."""
USER_INFO = TableInfo(
    name="providers",
    schema=pa.schema(
        [
            pa.field("id", pa.int64(), nullable=False),
            pa.field("type", pa.int64(), nullable=False),  # 0 = manager, 1 = provider.
            pa.field("name", pa.string(), nullable=False),
            pa.field("address", pa.string(), nullable=False),
            pa.field("city", pa.string(), nullable=False),
            pa.field("state", pa.string(), nullable=False),
            pa.field("zipcode", pa.int64(), nullable=False),
            pa.field("password_hash", pa.binary(), nullable=False),
        ]
    ),
    character_limits={
        "id": range(9, 9),
        "name": range(1, 25),
        "address": range(1, 25),
        "city": range(1, 14),
        "state": range(2, 2),
        "zipcode": range(5, 5),
    },
    numeric_limits={"type": range(0, 1)},
)

"""Record of all services logged"""
SERVICE_LOG_INFO = TableInfo(
    name="service_log",
    schema=pa.schema(
        [
            pa.field("entry_datetime_utc", pa.date64(), nullable=False),
            pa.field("service_date_utc", pa.date32(), nullable=False),
            pa.field("provider_id", pa.int64(), nullable=False),
            pa.field("member_id", pa.int64(), nullable=False),
            pa.field("service_id", pa.int64(), nullable=False),
            pa.field("comments", pa.string(), nullable=True),
        ]
    ),
    character_limits={
        "provider_id": USER_INFO.character_limits["id"],
        "member_id": MEMBER_INFO.character_limits["member_id"],
        "service_id": PROVIDER_DIRECTORY_INFO.character_limits["service_id"],
    },
)
