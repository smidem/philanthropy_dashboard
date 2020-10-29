from typing import List
from dashboard.bbec_api import run_query, get_query_id
import pandas as pd


def to_dataframe(headers: list, data: List[list], **kwargs):
    return pd.DataFrame(columns=headers, data=data, **kwargs)


def get_kpi(name, db_id='4249COL'):
    query_id = get_query_id(name=name, db_id=db_id)
    results = run_query(query_id=query_id, db_id=db_id, max_rows=10000)
    df = to_dataframe(*results)
    df['Amount'] = df['Amount'].astype('float')
    return sum(df['Amount'].to_list())


data_dict = {
    'labels': [
        'Flagship',
        'Israel/Global',
        # 'Jewish Life and Engagement',
        # 'Jewish Community Relations Council',
        # 'Regional Security Initiative',
        'Aspen',
        'Sponsorships',
        'Operations',
    ],
    'fy21_ytd': [
        f"${get_kpi('KPI Unrestricted - AK'):,.2f}",
        f"${get_kpi('KPI Israel Global - SM'):,.2f}",
        f"${get_kpi('KPI Aspen - AK'):,.2f}",
        f"${get_kpi('KPI In year sponsorships and grants'):,.2f}",
        f"${get_kpi('KPI Operations - SM'):,.2f}"
    ],
    'fy21_goal': [
        '$3,500,000',
        '$0',
        '$0',
        '$528,000',
        '$506,500',
    ]
}
data = pd.DataFrame.from_dict(data_dict)

if __name__ == '__main__':
    df = pd.DataFrame.from_dict(data_dict)
