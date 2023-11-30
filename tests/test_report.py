from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pyarrow as pa
from pyarrow import ArrowIOError
import pytest
from _pytest.fixtures import fixture

from choc_an_simulator.report import (
    generate_member_report,
    generate_provider_report,
    generate_summary_report,
)
from choc_an_simulator.schemas import TableInfo

"""
Create test data for the generate_member_report function.
"""
test_user_info = pd.DataFrame(
    {
        "id": [940672921, 265608022, 637066975, 483185890, 385685178, 807527890],
        "name": [
            "Case Hall",
            "Regina George",
            "Ray Donald",
            "Karla Tanners",
            "Zelda Hammersmith",
            "Linda Smith",
        ],
        "address": [
            "123 Main St",
            "456 Elm St",
            "789 Oak St",
            "1011 Pine St",
            "1213 Maple St",
            "1415 Cedar St",
        ],
        "city": [
            "Chicago",
            "New York",
            "Los Angeles",
            "Portland",
            "Sandy",
            "Muscle Shoals",
        ],
        "state": ["IL", "NY", "CA", "OR", "OR", "AL"],
        "zipcode": [15603, 38322, 84524, 64198, 34268, 73952],
        "password_hash": pa.array(
            [
                "password1",
                "password2",
                "password3",
                "password4",
                "password5",
                "password6",
            ],
            type=pa.binary(),
        ),
    }
)

test_member_info = pd.DataFrame(
    {
        "member_id": [137002632, 989635272, 752880910, 367868907, 344690896, 406072422],
        "name": [
            "John Doe",
            "Jane Doe",
            "Alex Smith",
            "Bob Henderson",
            "Rebecca Miller",
            "Leah Jones",
        ],
        "address": [
            "123 Main St",
            "456 Elm St",
            "789 Oak St",
            "1011 Pine St",
            "1213 Maple St",
            "1415 Cedar St",
        ],
        "city": [
            "Chicago",
            "New York",
            "Los Angeles",
            "Portland",
            "Sandy",
            "Muscle Shoals",
        ],
        "state": ["IL", "NY", "CA", "OR", "OR", "AL"],
        "zipcode": [15603, 38322, 84524, 64198, 34268, 73952],
        "suspended": [False, False, False, False, True, False],
    }
)

test_service_log_info = pd.DataFrame(
    {
        "entry_datetime_utc": [
            datetime(2023, 11, 21),
            datetime(2023, 11, 24),
            datetime(2023, 11, 26),
            datetime(2023, 11, 21),
            datetime(2023, 11, 21),
            datetime(2023, 11, 24),
        ],
        "service_date_utc": [
            datetime(2023, 11, 21),
            datetime(2023, 11, 24),
            datetime(2023, 11, 26),
            datetime(2023, 11, 21),
            datetime(2023, 11, 21),
            datetime(2023, 11, 24),
        ],
        "member_id": [367868907, 752880910, 367868907, 989635272, 752880910, 137002632],
        "provider_id": [
            483185890,
            483185890,
            940672921,
            385685178,
            385685178,
            637066975,
        ],
        "service_id": [889804, 951175, 495644, 805554, 427757, 708195],
        "comments": [
            "",
            "Test comment",
            "Test comment 2",
            "Test comment 3",
            "Test comment 4",
            "Test comment 5",
        ],
    }
)

test_provider_directory_info = pd.DataFrame(
    {
        "service_id": [889804, 951175, 495644, 805554, 427757, 708195],
        "service_name": [
            "Service 1",
            "Service 2",
            "Service 3",
            "Service 4",
            "Service 5",
            "Service 6",
        ],
        "price_cents": [33, 15, 99, 75, 50, 25],
        "price_dollars": [100, 200, 300, 400, 500, 600],
    }
)


def load_records_from_file_side_effect(*args, **kwargs):
    """
    Side effect for the load_records_from_file function.

    Returns-
        test_user_info: If the table_info argument is "providers"
        test_member_info: If the table_info argument is "members"
        test_service_log_info: If the table_info argument is "service_log"
        test_provider_directory_info: If the table_info argument is "provider_directory"
    """
    # Get the table_info argument
    table_info: TableInfo = args[0]

    if table_info.name == "service_log":
        return test_service_log_info
    elif table_info.name == "members":
        return test_member_info
    elif table_info.name == "providers":
        return test_user_info
    elif table_info.name == "provider_directory":
        return test_provider_directory_info


def save_report_side_effect(*args, **kwargs):
    """
    Side effect for the save_report function.

    Returns-
        Returns a mocked file path using the save_report file_name argument.
        "/path/to/report/{report_file_path}.csv"

    """
    # Get the report argument
    report_file_path: str = args[1]
    return f"/path/to/report/{report_file_path}.csv"


@fixture
def expected_report_df():
    """Fixture for the expected report."""
    return pd.DataFrame(
        {
            "Name": ["John Doe", "Bob Henderson", "Alex Smith", "Jane Doe"],
            "Member Number": [137002632, 367868907, 752880910, 989635272],
            "address": ["123 Main St", "1011 Pine St", "789 Oak St", "456 Elm St"],
            "city": ["Chicago", "Portland", "Los Angeles", "New York"],
            "state": ["IL", "OR", "CA", "NY"],
            "zipcode": [15603, 64198, 84524, 38322],
            "Services": [
                [(datetime(2023, 11, 24).date(), "Service 6", "Ray Donald")],
                [
                    (datetime(2023, 11, 21).date(), "Service 1", "Karla Tanners"),
                    (datetime(2023, 11, 26).date(), "Service 3", "Case Hall"),
                ],
                [
                    (datetime(2023, 11, 21).date(), "Service 5", "Zelda Hammersmith"),
                    (datetime(2023, 11, 24).date(), "Service 2", "Karla Tanners"),
                ],
                [(datetime(2023, 11, 21).date(), "Service 4", "Zelda Hammersmith")],
            ],
        }
    )


@fixture
def expected_output():
    """Fixture for the expected output."""
    current_date = datetime.now().strftime("%m-%d-%Y")
    return "".join(
        [
            f"Report saved to /path/to/report/John Doe_{current_date}.csv\n",
            f"Report saved to /path/to/report/Bob Henderson_{current_date}.csv\n",
            f"Report saved to /path/to/report/Alex Smith_{current_date}.csv\n",
            f"Report saved to /path/to/report/Jane Doe_{current_date}.csv\n",
        ]
    )


@patch("choc_an_simulator.report.save_report", side_effect=save_report_side_effect)
@patch(
    "choc_an_simulator.report.load_records_from_file",
    side_effect=load_records_from_file_side_effect,
)
def test_generate_member_report(
    mock_load_records_from_file,
    mock_save_report,
    expected_report_df,
    expected_output,
    capsys,
):
    """Test the generate_member_report function."""
    generate_member_report()
    captured = capsys.readouterr()

    assert captured.out == expected_output

    actual_df = pd.DataFrame()
    for i in range(mock_save_report.call_args_list.__len__()):
        actual_df = actual_df._append(mock_save_report.call_args_list[i][0][0])

    assert actual_df.equals(expected_report_df)


@patch("choc_an_simulator.report.load_records_from_file", return_value=pd.DataFrame())
def test_generate_member_report_no_members(mock_load_records_from_file, capsys):
    """
    Test the generate_member_report function with no members having had a service in the last
    7 days.
    """
    expected_output = "No records found within the last 7 days.\n"

    generate_member_report()
    captured = capsys.readouterr()

    assert captured.out == expected_output


@patch("choc_an_simulator.report.load_records_from_file", side_effect=ArrowIOError)
def test_generate_member_report_arrow_io_error(mock_load_records_from_file, capsys):
    """Test the generate_member_report function with a KeyError."""
    expected = "\033[93mThere was an issue accessing the database.\n\tError: \x1b[0m\n"
    generate_member_report()
    captured = capsys.readouterr()
    assert captured.out == expected


def test_generate_provider_report():
    """Test of the generate_provider_report function."""
    with pytest.raises(NotImplementedError):
        generate_provider_report()


def test_generate_summary_report():
    """Test of the generate_summary_report function."""
    with pytest.raises(NotImplementedError):
        generate_summary_report()
