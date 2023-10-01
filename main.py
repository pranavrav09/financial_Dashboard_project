import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import yfinance as yf
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import scipy.stats as stats
from datetime import datetime, timedelta
from sklearn.preprocessing import scale
from sklearn.model_selection import train_test_split
from matplotlib.ticker import FuncFormatter
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H1("Analysis Options"),
    html.Button("Univariate Analysis", id="univariate-button"),
    html.Button("Multivariate Analysis", id="multivariate-button"),
    html.Div(id="ticker-input", children=[]),
    html.Div(id="output-div", children=[]),
])

@app.callback(
    Output('ticker-input', 'children'),
    Input('univariate-button', 'n_clicks')
)
def get_ticker_input(n_clicks):
    if n_clicks:
        TICKER =  dbc.Input(id="ticker-input-box", placeholder="Enter Ticker Symbol", type = "text", value ="")
        START_DATE =dbc.Input(id = "start-date-input-box", placeholder = "Enter Start data", type = "text", value = "")
        END_DATE =  dbc.Input(id="end-date-input-box", placeholder="Enter End data", type="text", value="")


        return [TICKER, START_DATE, END_DATE]
    else:
        return []


@app.callback(
    Output('output-div', 'children'),
    Input('ticker-input-box', 'value'),
    Input('start-date-input-box', 'value'),
    Input('end-date-input-box', 'value')
)
def update_output(ticker, start_date, end_date, stockPrice):
    return html.Div([
        html.P(f"Ticker: {ticker}"),
        html.P(f"Start Date: {start_date}"),
        html.P(f"End Date: {end_date}"),
        html.P(f"Stock Price: {stockPrice}")
    ])

def getStockPrice(TICKER, START_DATE, END_DATE):
    stockPrice = yf.download(TICKER, START_DATE, END_DATE)

if __name__ == '__main__':
    app.run_server(debug=True)

