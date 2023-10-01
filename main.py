import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H1("Analysis Options"),
    html.Button("Univariate Analysis", id="univariate-button"),
    html.Button("Multivariate Analysis", id="multivariate-button"),
    html.Div(id="ticker-input", children=[]),
])


@app.callback(
    Output('ticker-input', 'children'),
    Input('univariate-button', 'n_clicks')
)
def get_ticker_input(n_clicks):
    if n_clicks:
        return dbc.Input(id="ticker-input-box", placeholder="Enter Ticker Symbol", type="text", value="")
    else:
        return []


if __name__ == '__main__':
    app.run_server(debug=True)
