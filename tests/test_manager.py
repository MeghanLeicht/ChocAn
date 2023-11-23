import pytest
import pandas as pd
from choc_an_simulator.manager import _generate_user_id


class TestGenerateUserID:
    @pytest.mark.parametrize(
        "existing_ids",
        [
            # First valid ID
            [10000000000],
            # Second to last valid ID
            [19999999998],
            # Empty
            [],
        ],
    )
    def test_generate_user_id_valid(self, mocker, existing_ids):
        """Test generating a valid user ID"""
        mocker.patch(
            "choc_an_simulator.manager.load_records_from_file",
            return_value=pd.DataFrame({"id": existing_ids}),
        )
        # print(load_records_from_file(None))
        new_id = _generate_user_id(1)
        assert new_id == max(existing_ids, default=9999999999) + 1

    def test_generate_user_id_out_of_range(self, mocker):
        """Test generating a user ID that exceeds the max value"""
        mocker.patch(
            "choc_an_simulator.manager.load_records_from_file",
            return_value=pd.DataFrame({"id": [19999999999]}),
        )
        with pytest.raises(IndexError):
            _ = _generate_user_id(1)

    @pytest.mark.parametrize("id_prefix", [-1, 0, 10])
    def test_generate_user_id_bad_prefix(self, mocker, id_prefix):
        """Test generating a user ID with an ID prefix that's out of range"""
        mocker.patch(
            "choc_an_simulator.manager.load_records_from_file",
            return_value=pd.DataFrame({"id": []}),
        )
        with pytest.raises(AssertionError):
            _ = _generate_user_id(id_prefix)
