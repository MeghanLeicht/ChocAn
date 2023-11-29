"""Tests of functions in the provider module."""
# import pytest
from unittest.mock import patch
import pandas as pd
from datetime import datetime

from choc_an_simulator.provider import record_service_billing_entry

# from choc_an_simulator.schemas import SERVICE_LOG_INFO, PROVIDER_DIRECTORY_INFO


def mock_prompt_date(message):
    return datetime.strptime("11-26-2023", "%m-%d-%Y")


def mock_prompt_int(message, char_limit, numeric_limit):
    if "provider ID" in message:
        return 123456789
    elif "service code" in message:
        return 555555


mock_providers_df = pd.DataFrame({"provider_id": [123456789]})

mock_services_df = pd.DataFrame(
    {
        "service_id": [555555],
        "service_name": ["Nutrition Consultation"],
        "price_dollars": [50],
        "price_cents": [0],
    }
)


class TestRecordServiceBillingEntry:
    @patch("choc_an_simulator.user_io.prompt_str", return_value="Test service")
    @patch("choc_an_simulator.user_io.prompt_date", side_effect=mock_prompt_date)
    @patch("choc_an_simulator.user_io.prompt_int", side_effect=mock_prompt_int)
    @patch("choc_an_simulator.database_management.load_records_from_file")
    @patch("choc_an_simulator.database_management.add_records_to_file")
    @patch("builtins.input", return_value="yes")
    def test_valid_input(
        self,
        mock_input,
        mock_add_records,
        mock_load_records,
        mock_prompt_int,
        mock_prompt_date,
        mock_prompt_str,
        capsys,
    ):
        mock_load_records.side_effect = [mock_providers_df, mock_services_df]

        member_id = 987654321
        record_service_billing_entry(member_id)

        captured = capsys.readouterr()
        assert "Service Billing Entry Recorded Successfully" in captured.out
        mock_add_records.assert_called_once()
