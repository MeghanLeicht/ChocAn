"""
Functions for generating reports.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import pyarrow as pa
from pandas.errors import MergeError

from .database_management import load_records_from_file, save_report
from .user_io import PColor
from .schemas import MEMBER_INFO, PROVIDER_DIRECTORY_INFO, SERVICE_LOG_INFO, TableInfo, USER_INFO


def error_handler(func):
    """
    Decorator to handle exceptions raised by calls to 'database_management.py'
    and the pandas library.
    """

    def wrapper(*args, **kwargs):
        """
        Wrapper function to handle exceptions raised by calls to 'database_management.py'.
        """
        try:
            func(*args, **kwargs)
        except KeyError as err_key:
            raise
        except pa.ArrowTypeError as err_type:
            raise
        except pa.ArrowInvalid as err_invalid:
            raise
        except pa.ArrowIOError as err_io:
            raise
        except TypeError as err_type:
            raise
        except MergeError as err_merge:
            raise
        except ValueError as err_value:
            raise

    return wrapper


@error_handler
def generate_member_report() -> None:
    """
    Generate a report for each member who has consulted with a ChocAn provider.
    A 'date' filter will be added to 'gt_cols' to retrieve members that have
    had services provided to them in the last 7 days.The members are listed in
    the order of the service date. After a report is generated, the path to it
    is printed to the console.

    Returns-
        None

    Raises-
        KeyError: If a column name is not found in the schema.
        ArrowTypeError: If a column value is not of the correct type.
        ArrowInvalid: If a column value is invalid.
        ArrowIOError: If an IO error occurs.
        TypeError: If a column value is not of the correct type.
    """
    gt_cols = {"service_date_utc": datetime.now() - timedelta(days=7)}
    tables = [
        _generate_data_dict(SERVICE_LOG_INFO, gt_cols=gt_cols,
                            kept_cols=['service_date_utc', 'member_id', 'provider_id', 'service_id']),
        _generate_data_dict(MEMBER_INFO, kept_cols=['member_id', 'name', 'address', 'city', 'state', 'zipcode']),
        _generate_data_dict(USER_INFO, kept_cols=['name', 'id']),
        _generate_data_dict(PROVIDER_DIRECTORY_INFO, kept_cols=['service_name', 'service_id']),
    ]

    records = _load_all_records(tables)

    if records['service_log'].empty:
        print("No records found within the last 7 days.")
        return

    merge_instructions = [
        {
            'left_df': records[SERVICE_LOG_INFO.name],
            'right_df': records[PROVIDER_DIRECTORY_INFO.name],
            'merge_kwargs': {
                'on': 'service_id'
            },
        },
        {
            'right_df': records[USER_INFO.name],
            'merge_kwargs': {
                'left_on': 'provider_id',
                'right_on': 'id'
            },
            'drop_cols': ['id'],
        },
        {
            'right_df': records[MEMBER_INFO.name],
            'merge_kwargs': {
                'on': 'member_id'
            },
        },
    ]

    records = merge_dataframes(merge_instructions)

    records = records.groupby('member_id').apply(
        lambda x: pd.DataFrame(
            {
                'Member name': x['name_y'].iloc[0],
                'Member number': x['member_id'].iloc[0],
                'Member street address': x['address'].iloc[0],
                'Member city': x['city'].iloc[0],
                'Member state': x['state'].iloc[0],
                'Member zip code': x['zipcode'].iloc[0],
                'Services': [
                    sorted(
                        x[['service_date_utc', 'name_x', 'service_name']].values.tolist(),
                        key=lambda y: pd.to_datetime(y[0])
                    )
                ]
            }
        )
    ).reset_index(drop=True)

    list_of_members = [pd.DataFrame(records.iloc[i]).T for i in range(len(records))]

    for member_record in list_of_members:
        file_path = save_report(member_record, f"{member_record['Member name'].values.item()}_{_current_date()}")
        print(f"Report saved to {file_path}")


def _load_all_records(tables: List[Dict[str, Any]]) -> Dict[str, pd.DataFrame]:
    """
    Load the data needed to generate the member report.

    Returns-
        A dataframe containing the data needed to generate the member report.

    Raises-
        KeyError: If a column name is not found in the schema.
        ArrowTypeError: If a column value is not of the correct type.
        ArrowInvalid: If a column value is invalid.
        ArrowIOError: If an IO error occurs.
        TypeError: If a column value is not of the correct type.
    """
    records = {}
    for table in tables:
        records[table['table'].name] = load_records_from_file(
            table['table'],
            gt_cols=table['filter'].get('gt_cols'),
            lt_cols=table['filter'].get('lt_cols'),
            eq_cols=table['filter'].get('eq_cols'),
        )[table['kept_cols']]

    return records


def merge_dataframes(merge_instructions: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Merge dataframes.

    Args-
        df_dict (Dict[str, pd.DataFrame]): A dictionary of dataframes to merge.
        merge_instructions (List[Dict[str, Any]]): list of dictionaries containing instructions for merging dataframes.

    Returns-
        A merged dataframe.

    Raises-
        KeyError: If a column name is not found in the schema.
        ArrowTypeError: If a column value is not of the correct type.
        ArrowInvalid: If a column value is invalid.
        ArrowIOError: If an IO error occurs.
        TypeError: If a column value is not of the correct type.
    """
    merged_dfs = pd.DataFrame()
    for instruction in merge_instructions:
        merged_dfs = pd.merge(
            instruction['left_df'] if merged_dfs.empty else merged_dfs,
            instruction['right_df'],
            **instruction['merge_kwargs']
        )
        if 'drop_cols' in instruction:
            merged_dfs = merged_dfs.drop(instruction['drop_cols'], axis=1)

    return merged_dfs


def _generate_data_dict(
        table_info: TableInfo,
        kept_cols: [List[str]],
        eq_cols: Optional[Dict[str, Any]] = None,
        lt_cols: Optional[Dict[str, Any]] = None,
        gt_cols: Optional[Dict[str, Any]] = None,

) -> Dict[str, Any]:
    """
    Generate a dictionary of TableInfo and filter information to be used to generate a report.

    Args-
        table_info (TableInfo): Object with schema and table details.
        eq_cols (Optional[Dict[str, Any]]): Specifies columns and values for equality filtering.
        lt_cols (Optional[Dict[str, Any]]): Specifies columns and values for less-than filtering.
        gt_cols (Optional[Dict[str, Any]]): Specifies columns and values for greater-than filtering.

    Returns-
        A dictionary of TableInfo and filter information to be used to generate a report.
    """
    data_dict = {}
    filters = {}
    if eq_cols is not None:
        filters['eq_cols'] = eq_cols
    if lt_cols is not None:
        filters['lt_cols'] = lt_cols
    if gt_cols is not None:
        filters['gt_cols'] = gt_cols

    data_dict = {
        'table': table_info,
        'filter': filters,
        'kept_cols': kept_cols,
    }

    return data_dict


def _current_date() -> str:
    """
    Returns the current date in the format MM-DD-YYYY.
    """
    return datetime.now().strftime("%m-%d-%Y")
