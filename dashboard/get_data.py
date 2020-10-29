from typing import List
from dashboard.bbec_api import run_query, get_query_id
import pandas as pd


def to_dataframe(headers: list, data: List[list], **kwargs):
    return pd.DataFrame(columns=headers, data=data, **kwargs)


def get_data(name, db_id='4249COL', **kwargs):
    query_id = get_query_id(name=name, db_id=db_id)
    results = run_query(query_id=query_id, db_id=db_id, max_rows=10000)
    df = to_dataframe(*results, **kwargs)
    df['Amount'] = df['Amount'].astype('float')
    return sum(df['Amount'].to_list())


if __name__ == '__main__':
    print(get_data('KPI Rest to Jco (new way) - AK'))
