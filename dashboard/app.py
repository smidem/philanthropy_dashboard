from dashboard.get_data import data
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.P(html.Div(html.H3('Annual Campaign Dashboard'))),
    dash_table.DataTable(
        id='philanthropy_dashboard',
        style_table={
            'maxHeight': '700px',
            'overflowY': 'scroll'
        },
        columns=[
            {'name': "", 'id': "labels"},
            {'name': "FY21 YTD", 'id': "fy21_ytd"},
            {'name': "FY21 Goal", 'id': "fy21_goal"},
            # {'name': "% to Goal", 'id': "goal_pct"},
            # {'name': "FY20 YTD", 'id': "fy20_ytd"},
        ],
        data=data.to_dict('records'),
    )
])

if __name__ == '__main__':
    server.run()
