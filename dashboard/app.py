from dashboard.get_data import get_data
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.P(html.Div(html.H3('Annual Campaign Dashboard'))),
])

if __name__ == '__main__':
    server.run()
