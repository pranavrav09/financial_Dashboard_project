import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import scipy.stats as stats
from datetime import datetime

# Additional imports for the new distributions
from scipy.stats import t, laplace

def get_stock_data(ticker, start_date, end_date):
    try:
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        return stock_data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def getUniTailRiskTable(lrets, q=0.05):
    VaR = lrets.quantile(q)
    ES = lrets[lrets <= VaR].mean()
    return pd.DataFrame({'VaR': [VaR], 'ES': [ES]})

def getQQPlots(lrets):
    plots = {}
    distributions = {
        'Normal': stats.norm.rvs(size=len(lrets)),
        'Student-t': t.rvs(df=10, size=len(lrets)),
        'Double Exponential': laplace.rvs(size=len(lrets))
    }

    for name, samples in distributions.items():
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=np.sort(samples),
                                 y=np.sort(lrets),
                                 mode='markers',
                                 name=f'{name} Q-Q'))
        fig.update_layout(title=f"{name} Q-Q Plot",
                          xaxis_title="Theoretical Quantiles",
                          yaxis_title="Sample Quantiles")
        plots[name] = fig

    return plots

def getTimePlots(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Adj Close'], mode='lines', name='Asset Prices'))
    log_returns = np.log(df['Adj Close'] / df['Adj Close'].shift(1)).replace([np.inf, -np.inf], np.nan).dropna()
    fig.add_trace(go.Scatter(x=df.index[1:], y=log_returns, mode='lines', name='Log Returns'))
    fig.update_layout(title="Time Series Plot for Asset Prices and Log Returns",
                      xaxis_title="Date",
                      yaxis_title="Price / Log Return")
    return fig



# Function to create time plots for asset prices and log returns
def getTimePlots(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Adj Close'], mode='lines', name='Asset Prices'))
    fig.add_trace(go.Scatter(x=df.index, y=np.log(df['Adj Close']).replace([np.inf, -np.inf], np.nan).dropna(), mode='lines', name='Log Returns'))
    fig.update_layout(title="Time Series Plot for Asset Prices and Log Returns",
                      xaxis_title="Date",
                      yaxis_title="Price / Log Return")
    return fig

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

today_date = datetime.today().strftime('%Y-%m-%d')

app.layout = dbc.Container([
    html.H1("Stock Data Visualization", style={'textAlign': 'center', 'margin': '20px 0'}),
    dbc.Card([
        dbc.CardHeader(
            dbc.Button("Options", id="collapse-button", color="link")
        ),
        dbc.Collapse(
            dbc.CardBody([
                dbc.Input(id="ticker-input-box", placeholder="Enter Ticker Symbol", type="text", debounce=True),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    start_date=today_date,
                    end_date=today_date,
                    display_format='YYYY-MM-DD',
                    clearable=True
                ),
                dbc.Button("View Analysis", id="analysis-button", color="primary", n_clicks=0)
            ]),
            id="collapse",
        ),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Tabs([
                dcc.Tab(id='tab-histogram', label='Histogram'),
                dcc.Tab(id='tab-qq-normal', label='QQ Plot - Normal'),
                dcc.Tab(id='tab-qq-student-t', label='QQ Plot - Student-t'),
                dcc.Tab(id='tab-qq-double-exponential', label='QQ Plot - Double Exponential'),
                dcc.Tab(id='tab-qq-generalized-error', label='QQ Plot - Generalized Error'),
                dcc.Tab(id='tab-time-plots', label='Time Series Plots'),
                dcc.Tab(id='tab-risk-table', label='Risk Measures')
            ])
        ]),
    ]),
], fluid=True)

@app.callback(
    [Output('tab-histogram', 'children'),
     Output('tab-qq-normal', 'children'),
     Output('tab-qq-student-t', 'children'),
     Output('tab-qq-double-exponential', 'children'),
     Output('tab-qq-generalized-error', 'children'),
     Output('tab-time-plots', 'children'),
     Output('tab-risk-table', 'children')],
    [Input('analysis-button', 'n_clicks'),
     Input('ticker-input-box', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')],
    prevent_initial_call=True
)
def update_analysis(n_clicks, ticker, start_date, end_date):
    df = get_stock_data(ticker, start_date, end_date)
    if df is None:
        return [html.Div("No data available")] * 7

    lrets = np.log(df['Adj Close'] / df['Adj Close'].shift(1)).replace([np.inf, -np.inf], np.nan).dropna()

    histogram = go.Figure()
    histogram.add_trace(go.Histogram(x=lrets, nbinsx=30, name='Log Returns'))
    histogram.update_layout(title="Histogram for Log Returns",
                            xaxis_title="Log Returns",
                            yaxis_title="Frequency")

    qq_plots = getQQPlots(lrets)
    time_plot = getTimePlots(df)
    risk_table = getUniTailRiskTable(lrets)

    return (
        [dcc.Graph(figure=histogram)],
        [dcc.Graph(figure=qq_plots['Normal'])],
        [dcc.Graph(figure=qq_plots['Student-t'])],
        [dcc.Graph(figure=qq_plots['Double Exponential'])],
        [dcc.Graph(figure=qq_plots['Generalized Error'])],
        [dcc.Graph(figure=time_plot)],
        [html.Div([html.H4("Risk Measures"), dbc.Table.from_dataframe(risk_table, striped=True, bordered=True, hover=True)])]
    )

@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [dash.dependencies.State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run_server(debug=True)
