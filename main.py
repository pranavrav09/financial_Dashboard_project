import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import yfinance as yf
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
import scipy.stats as stats
from datetime import datetime, timedelta
from sklearn.preprocessing import scale
from sklearn.model_selection import train_test_split
from matplotlib.ticker import FuncFormatter

# Import Plotly
import plotly.express as px

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H1("Analysis Options"),
    html.Button("Univariate Analysis", id="univariate-button"),
    html.Button("Multivariate Analysis", id="multivariate-button"),
    html.Div(id="ticker-input", children=[]),
    html.Div(id="output-div", children=[]),
    dcc.Graph(id="stock-histogram")  # Add a Graph component for the histogram
])


@app.callback(
    Output('ticker-input', 'children'),
    Input('univariate-button', 'n_clicks')
)
def get_ticker_input(n_clicks):
    if n_clicks and n_clicks > 0:
        TICKER = dbc.Input(id="ticker-input-box", placeholder="Enter Ticker Symbol", type="text")
        START_DATE = dcc.DatePickerSingle(id="start-date-input-box", placeholder="Enter Start Date")
        END_DATE = dcc.DatePickerSingle(id="end-date-input-box", placeholder="Enter End Date")
        return [TICKER, START_DATE, END_DATE]
    return []


@app.callback(
    Output('output-div', 'children'),
    Output('stock-histogram', 'figure'),  # Output for the stock histogram
    Input('ticker-input-box', 'value'),
    Input('start-date-input-box', 'date'),
    Input('end-date-input-box', 'date')
)
def update_output(ticker, start_date, end_date):
    if ticker and start_date and end_date:
        df = get_stock_data(ticker, start_date, end_date)
        if df is not None:
            table = dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                style_table={'overflowX': 'scroll'},
                page_size=10
            )

            # Create a histogram of stock values
            fig = px.histogram(df, x="Adj Close", title=f"Histogram of {ticker} Stock Values")
            return [table, fig]  # Return the table and the histogram
    return [], {}


def get_stock_data(ticker, start_date, end_date):
    try:
        stock_data = yf.download(ticker, start_date, end_date)
        stock_data.reset_index(inplace=True)
        stock_data['Year'] = stock_data['Date'].dt.year
        yearly_data = stock_data.groupby('Year').mean()
        return yearly_data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


if __name__ == '__main__':
    app.run_server(debug=True)
