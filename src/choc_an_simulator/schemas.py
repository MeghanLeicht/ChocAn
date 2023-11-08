"""
Collection of constant schemas, to be used when interacting with the database management module.

Examples -
# 1. Get a full list of members
def get_full_member_list():
    from database_management import load_records_from_file
    from schemas import MEMBER_INFO
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
        """Assertions & assignments after init."""
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
        """Get the index column name of the schema."""
        return self.schema.names[0]

    def includes_columns(self, columns: List[str]) -> bool:
        """Check if all of the given columns exist in the schema."""
        return all(col in self.schema.names for col in columns)

    def check_columns(self, columns: List[str]) -> None:
        """Check that the given columns are the same as the schema columns."""
        if set(self.schema.names) != set(columns):
            raise KeyError("Data and schema have mismatched columns.")

    def check_dataframe(self, data: pd.DataFrame) -> None:
        """
        Check a dataframe for alignment with schema.

        Args-
            data: Dataframe to check against schema

        Raises-
            KeyError: Mismatched columns
            TypeError: Value type is incompatible with field
            ArithmeticError: Out of character range or numeric range.
        """
        data.apply(lambda row: self.check_series(row), axis=1)  # type: ignore

    def check_series(self, data: pd.Series) -> None:
        """
        Check a series for alignment with schema.

        Args-
            data: Series to check for compatibility with field

        Raises-
            KeyError: Field doesn't exist in schema
            TypeError: Value type is incompatible with field
            ArithmeticError: Value doesn't adhere to field's character or numeric limit.
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
        if field_name not in self.schema.names:
            raise KeyError(
                f"Field Name {field_name} does not exist in {self.name} schema."
            )
        field: pa.Field = self.schema.field(field_name)

        # Check for type compatibility
        try:
            _ = pa.array([value], type=field.type)
        except pa.ArrowInvalid:
            raise TypeError(
                f"Value {value} has wrong type for column "
                f"{field_name} ({type(value)} -> {field.type})"
            )

        if field_name in self.character_limits.keys():
            val_len = len(str(value))
            limit_range = self.character_limits[field_name]
            if (val_len < limit_range.start) or (val_len > limit_range.stop):
                raise ArithmeticError(
                    f"{field_name} value {value} is outside character limit {limit_range} "
                )

        if field_name in self.numeric_limits.keys():
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
        "member_id": range(11, 11),
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
            pa.field("id", pa.uint32(), nullable=False),
            pa.field("name", pa.string(), nullable=False),
            pa.field("address", pa.string(), nullable=False),
            pa.field("city", pa.string(), nullable=False),
            pa.field("state", pa.string(), nullable=False),
            pa.field("zipcode", pa.uint32(), nullable=False),
        ]
    ),
    character_limits={
        "id": range(11, 11),
        "name": range(1, 25),
        "address": range(1, 25),
        "city": range(1, 14),
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
            pa.field("service_date_utc", pa.date32(), nullable=False),
            pa.field("provider_id", pa.uint32(), nullable=False),
            pa.field("member_id", pa.uint32(), nullable=False),
            pa.field("service_id", pa.uint32(), nullable=False),
            pa.field("comments", pa.string(), nullable=True),
        ]
    ),
    character_limits={
        "provider_id": USER_INFO.character_limits["id"],
        "member_id": MEMBER_INFO.character_limits["member_id"],
        "service_id": PROVIDER_DIRECTORY_INFO.character_limits["service_id"],
    },
)
