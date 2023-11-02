"""
Collection of constant schemas, to be used when interacting with the database management module.

Examples -
# 1. Get a full list of members
def get_full_member_list():
    from database_management import load_records_from_file
    from schemas import MEMBER_INFO
    members = load_records_from_file(MEMBER_INFO.name, MEMBER_INFO.schema)
"""
from typing import Any
import pyarrow as pa
import pandas as pd
from dataclasses import dataclass, field


@dataclass(frozen=True)
class TableInfo:
    """Info for one database file on the disc."""

    name: str
    schema: pa.Schema
    # Limits on character length (e.g. only 9 digit numbers)
    character_limits: dict[str, range] = field(default_factory=lambda: {})
    # Limits on numeric length (e.g. only numbers between 0 and 99)
    numeric_limits: dict[str, range] = field(default_factory=lambda: {})

    def __post_init__(self):
        """Assert that character limit information aligns with schema information."""
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

    def check_dataframe(self, data: pd.DataFrame) -> None:
        """Checks a dataframe for alignment with schema."""
        if set(self.schema.names) != set(data.columns):
            raise KeyError("Dataframe and schema have mismatched columns.")
        for col_name, limit_range in self.character_limits.items():
            char_lens = data[col_name].astype(str).str.len()
            if any((char_lens < limit_range.start) | (char_lens > limit_range.stop)):
                raise ArithmeticError(
                    f"Column {col_name} contains entries outsde of character limit ({limit_range})."
                )
        for col_name, limit_range in self.numeric_limits.items():
            if any(
                (data[col_name] < limit_range.start)
                | (data[col_name] > limit_range.stop)
            ):
                raise ArithmeticError(
                    f"Column {col_name} contains entries outside of numeric limit ({limit_range})."
                )

    def check_series(self, data: pd.Series) -> None:
        """Checks a series for alignment with schema."""
        if set(self.schema.names) != set(data.index.values):
            raise KeyError("Series and schema have mismatched columns.")
        for col_name, limit_range in self.character_limits.items():
            char_len = len(str(data[col_name]))
            if (char_len < limit_range.start) or (char_len > limit_range.stop):
                raise ArithmeticError(
                    f"Column {col_name} contains entries out of range {limit_range}."
                )
        for col_name, limit_range in self.numeric_limits.items():
            if (data[col_name] < limit_range.start) or (
                data[col_name] > limit_range.stop
            ):
                raise ArithmeticError(
                    f"Column {col_name} contains entries outside of numeric limit ({limit_range})."
                )

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
        if field_name not in self.schema.names:
            raise KeyError(
                f"Field Name {field_name} does not exist in {self.name} schema."
            )
        field: pa.Field = self.schema.field_by_name(field_name)

        # Check for type compatibility
        try:
            _ = pa.array([value], type=field.type)
        except TypeError:
            raise TypeError(
                f"Value {value} has wrong type for column "
                f"{field_name} ({type(value)} -> {field.type})"
            )

        if field_name in self.character_limits.keys():
            val_len = len(str(value))
            limit_range = self.character_limits[field_name]
            if val_len < limit_range.start:
                raise ArithmeticError(
                    f"{field_name} value {value} is below character limit {limit_range} "
                )
            if val_len > limit_range.stop:
                raise ArithmeticError(
                    f"{field_name} value {value} is above character limit {limit_range} "
                )

        if field_name in self.numeric_limits.keys():
            limit_range = self.numeric_limits[field_name]
            if value < limit_range.start:
                raise ArithmeticError(
                    f"{field_name} value {value} is below numeric limit {limit_range} "
                )
            if value > limit_range.stop:
                raise ArithmeticError(
                    f"{field_name} value {value} is above numeric limit {limit_range} "
                )


"""All services offered by ChocAn, and their codes."""
PROVIDER_DIRECTORY_INFO = TableInfo(
    name="provider_directory",
    schema=pa.schema(
        [
            pa.field("service_id", pa.uint32(), nullable=False),
            pa.field("service_name", pa.string(), nullable=False),
            pa.field("price_dollars", pa.uint32(), nullable=False),
            pa.field("price_cents", pa.uint32(), nullable=False),
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
            pa.field("member_id", pa.uint32(), nullable=False),
            pa.field("name", pa.string(), nullable=False),
            pa.field("address", pa.string(), nullable=False),
            pa.field("city", pa.string(), nullable=False),
            pa.field("state", pa.string(), nullable=False),
            pa.field("zipcode", pa.uint32(), nullable=False),
            pa.field("suspended", pa.bool_(), nullable=False),
        ]
    ),
    character_limits={
        "member_id": range(9, 9),
        "name": range(1, 25),
        "address": range(1, 25),
        "city": range(1, 25),
        "state": range(2, 2),
        "zipcode": range(5, 5),
    },
)

"""All current ChocAn providers."""
PROVIDER_INFO = TableInfo(
    name="providers",
    schema=pa.schema(
        [
            pa.field("provider_id", pa.uint32(), nullable=False),
            pa.field("name", pa.string(), nullable=False),
            pa.field("address", pa.string(), nullable=False),
            pa.field("city", pa.string(), nullable=False),
            pa.field("state", pa.string(), nullable=False),
            pa.field("zipcode", pa.uint32(), nullable=False),
        ]
    ),
    character_limits={
        "provider_id": range(9, 9),
        "name": range(1, 25),
        "address": range(1, 25),
        "city": range(1, 25),
        "state": range(2, 2),
        "zipcode": range(5, 5),
    },
)

"""Record of all services logged"""
SERVICE_LOG_INFO = TableInfo(
    name="service_log",
    schema=pa.schema(
        [
            pa.field("entry_datetime_utc", pa.date64(), nullable=False),
            pa.field("service_datetime_utc", pa.date32(), nullable=False),
            pa.field("provider_id", pa.uint32(), nullable=False),
            pa.field("member_id", pa.uint32(), nullable=False),
            pa.field("service_id", pa.uint32(), nullable=False),
            pa.field("comments", pa.string(), nullable=True),
        ]
    ),
    character_limits={
        "provider_id": PROVIDER_INFO.character_limits["provider_id"],
        "member_id": MEMBER_INFO.character_limits["member_id"],
        "service_id": PROVIDER_DIRECTORY_INFO.character_limits["service_id"],
    },
)
