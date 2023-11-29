"""Tests of functions in the provider module."""
# import pytest
import io
import sys
import unittest
from unittest.mock import patch
import pandas as pd
from datetime import datetime

from choc_an_simulator.provider import record_service_billing_entry


class TestRecordServiceBillingEntry(unittest.TestCase):
    @patch("choc_an_simulator.provider.add_records_to_file")
    @patch("choc_an_simulator.provider.prompt_str")
    @patch("choc_an_simulator.provider.prompt_str")
    @patch("choc_an_simulator.provider.prompt_int")
    @patch("choc_an_simulator.provider.prompt_date")
    @patch("choc_an_simulator.provider.prompt_int")
    @patch("choc_an_simulator.provider.load_records_from_file")
    def test_valid_input(
        self,
        mock_add_records,
        mock_prompt_str_comments,
        mock_prompt_str_confirm,
        mock_prompt_int_provider_id,
        mock_prompt_date,
        mock_prompt_int_service_code,
        mock_load_records,
    ):
        mock_providers_df = pd.DataFrame({"provider_id": [123456789]})
        mock_services_df = pd.DataFrame(
            {
                "service_id": [555555],
                "service_name": ["Nutrition Consultation"],
                "price_dollars": [50],
                "price_cents": [0],
            }
        )
        mock_load_records.side_effect = [mock_providers_df, mock_services_df]
        mock_prompt_str_confirm.return_value = "yes"
        mock_prompt_str_comments.return_value = "Test comment"
        mock_prompt_int_service_code.return_value = 555555
        mock_prompt_int_provider_id.return_value = 123456789
        mock_prompt_date.return_value = datetime.strptime("11-26-2023", "%m-%d-%Y")

        member_id = 987654321

        original_stdout = sys.stdout
        sys.stdout = io.StringIO()

        record_service_billing_entry(member_id)

        # Capture output and revert stdout
        output = sys.stdout.getvalue()
        sys.stdout = original_stdout

        self.assertIn("Service Billing Entry Recorded Successfully", output)
        mock_add_records.assert_called_once()
