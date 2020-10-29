from dashboard.get_data import data
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Div(
        html.Img(
            src='http://cdn.mcauto-images-production.sendgrid.net/'
                'e3acd8c9d23315eb/72be3792-bb15-4a5a-81c2-3eb9c7a04d8e/'
                '241x51.png'
        ),
        style={'textAlign': 'center'}
    ),
    html.P(
        html.Div(
            html.H3('Annual Campaign Dashboard'),
            style={'textAlign': 'center'}
        )
    ),
    html.Div(
        dash_table.DataTable(
            id='philanthropy_dashboard',
            style_table={
                'maxHeight': '700px',
                'maxWidth': '700px',
                # 'overflowY': 'scroll',
            },
            # style_cell={
            #     'maxWidth': '50px',
            # },
            columns=[
                {'name': "", 'id': "labels"},
                {'name': "FY21 YTD", 'id': "fy21_ytd"},
                {'name': "FY21 Goal", 'id': "fy21_goal"},
                # {'name': "% to Goal", 'id': "goal_pct"},
                # {'name': "FY20 YTD", 'id': "fy20_ytd"},
            ],
            data=data.to_dict('records'),
        ),
        style={'textAlign': 'center'},
    ),
])

if __name__ == '__main__':
    print(data.to_dict('records'))
    server.run()
