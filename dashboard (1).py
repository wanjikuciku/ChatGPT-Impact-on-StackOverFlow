import dash
from dash import html, dcc, Input, Output
from flask import Flask
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter

flask_app = Flask(__name__)

dash_app = dash.Dash(__name__, server=flask_app)

# Load your data
graph_data = pd.read_csv('data_monthly.csv')
# Load your new_data for post count analysis
new_data = pd.read_csv('new_data.csv')
# Load your forecast data
forecast_data = pd.read_csv('forecast.csv')
# Convert the 'ds' column to datetime in the forecast_data
forecast_data['ds'] = pd.to_datetime(forecast_data['ds'])

# Create the initial plot
def create_time_series_plot(data):
    return px.line(data, x='CreationDate', y='ViewCount', title='Time Series Plot')

# Function to create the time series plot for forecast data
def create_forecast_time_series_plot(data):
    return px.line(data, x='ds', y='yhat', title='Forecast Time Series Plot')


# Convert 'CreationDate' column to datetime
new_data['CreationDate'] = pd.to_datetime(new_data['CreationDate'])

# Set the start and end dates for posts before and after ChatGPT
start_date = pd.to_datetime('2020-11-01')
chat_gpt_release = pd.to_datetime('2022-11-30')

# Filter data for posts before and after the release of ChatGPT
posts_before = new_data[(new_data['CreationDate'] >= start_date) & (new_data['CreationDate'] <= chat_gpt_release)]
posts_after = new_data[new_data['CreationDate'] > chat_gpt_release]

# Calculate the counts of posts before and after the release
count_before = len(posts_before)
count_after = len(posts_after)

# Function to visualize the counts of posts
def visualize_post_counts(count_before, count_after):
    fig = px.bar(x=['Before ChatGPT', 'After ChatGPT'], y=[count_before, count_after], title='Post Count Analysis')
    return fig

# Callback to update the time series plot based on user interactions
@dash_app.callback(
    Output('time-series-plot', 'figure'),
    Input('time-series-plot', 'relayoutData')
)


def update_time_series_plot(relayoutData):
    if relayoutData:
        xaxis_range = relayoutData.get('xaxis.range')
        if xaxis_range:
            filtered_data = graph_data[(graph_data['CreationDate'] >= xaxis_range[0]) & (graph_data['CreationDate'] <= xaxis_range[1])]
            return create_time_series_plot(filtered_data)
    
    return create_time_series_plot(graph_data)



# Create tabs
intro_tab_layout = html.Div(children=[
    html.Div("Introduction Tab Content"),
    html.P("The introduction of ChatGPT has significantly reduced interactions on StackOverflow by streamlining and automating the process of seeking programming and technical assistance. ChatGPT's ability to understand and generate human-like responses to a wide range of coding and software development queries has reduced the need for users to post their questions on StackOverflow. With its rapid, reliable, and readily available support, many programmers and developers turn to ChatGPT first, saving time and effort while still receiving effective solutions to their problems. Consequently, StackOverflow interactions have declined as users increasingly rely on this AI-powered tool to meet their coding challenges, making it a transformative force in the realm of online technical assistance."),
    dcc.Graph(id='time-series-plot')
])
post_count_tab_layout = html.Div(children=[
    html.Div("Post Count Analysis Tab Content"),
    html.P(f"Number of Posts before ChatGPT (2020-2022): {count_before}"),
    html.P(f"Number of Posts after ChatGPT: {count_after}"),
    dcc.Graph(figure=visualize_post_counts(count_before, count_after))
])
prediction_tab_layout = html.Div(children=[
    html.Div("Time Series Predictions Tab Content"),
    html.Div("Due to the ChatGPT launch, the interactions of users with StackOverFlow has been going down drastically despite the increase in the number of people in the coding community. Our predictions show that StackOverflow is going to have zero to little interactions in the next year due to people looking onto ChatGPT for solutions."),
    html.Div("Date Range Slider Label: Date Range"),
    # Date Range Slider
    dcc.Slider(
        id='date-range-slider',
        min=forecast_data['ds'].min().timestamp(),
        max=forecast_data['ds'].max().timestamp(),
        step=24*60*60,  # Step by a day
        marks={i: {'label': pd.to_datetime(i, unit='s').strftime('%Y-%m-%d')} for i in range(
            int(forecast_data['ds'].min().timestamp()), int(forecast_data['ds'].max().timestamp())+1, 24*60*60)},
        value=forecast_data['ds'].min().timestamp(),  
    ),
    dcc.Graph(id='forecast-time-series-plot')
])

@dash_app.callback(
    Output('forecast-time-series-plot', 'figure'),
    Input('date-range-slider', 'value')
)

def update_forecast_graph(date_range):
    if date_range:
        start_date = pd.to_datetime(date_range, unit='s')
        filtered_data = forecast_data[(forecast_data['ds'] >= start_date)]
        
        # Check if the filtered data is empty, and handle it
        if filtered_data.empty:
            return {
                "data": [],
                "layout": {
                    "title": "No data available for the selected date range"
                }
            }
        
        return create_forecast_time_series_plot(filtered_data)
    
    return create_forecast_time_series_plot(forecast_data)
dash_app.layout = dbc.Container([
    html.H1('EFFECT OF CHATGPT ON STACKOVERFLOW'),
    dcc.Tabs([
        dcc.Tab(intro_tab_layout, label='Introduction'),
        dcc.Tab(post_count_tab_layout, label='Post Count Analysis'),
        dcc.Tab(prediction_tab_layout, label='Time Series Predictions')
    ])
])

import warnings
warnings.filterwarnings('ignore')

dash_app.run(debug=True)
