import dash
from dash import dcc, html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Analysis Options"),
    html.Button("Univariate Analysis", id="univariate-button"),
    html.Button("Multivariate Analysis", id="multivariate-button"),
])


@app.callback(
    Output('univariate-button', 'n_clicks'),
    Output('multivariate-button', 'n_clicks'),
    Input('univariate-button', 'n_clicks'),
    Input('multivariate-button', 'n_clicks')
)
def handle_button_clicks(univariate_clicks, multivariate_clicks):
    if univariate_clicks or multivariate_clicks:
        print("Button clicked!")
    return univariate_clicks, multivariate_clicks


if __name__ == '__main__':
    app.run_server(debug=True)
