from dashboard.get_data import get_data
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table

rest_jco = get_data('KPI Rest to Jco (new way) - AK')
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.P(html.Div(html.H3('Annual Campaign Dashboard'))),
    html.P(f"Restricted to JCO: {rest_jco}")
])

if __name__ == '__main__':
    server.run(port=8050)
