import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import pandas as pd
from datetime import datetime
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
################### READING DATA ###################
# Get the directory of the current script
script_dir = os.path.dirname(__file__)

# Construct the full path to the CSV file
# file_name = 'RidershipData.csv'
# file_name = 'Fall2024_RidershipData.csv'
# file_name = '051524-051924_RidershipData.csv'
file_name = 'mock_ridership_data.csv'

# file_path = os.path.join(script_dir, '..','.gitignore','data', file_name)
file_path = os.path.join(script_dir, '..','data', file_name)

# Read the CSV file
df = pd.read_csv(file_path)

################### MODIFY DATA ###################
#removing cancelled trips, skipped/waiting stops (bc no riders getting on)
df.drop(df[df['Ride State'] == 'Cancelled'].index, inplace = True)
df.drop(df[df['Stop State'] == 'Skipped'].index, inplace = True)
df.drop(df[df['Stop State'] == 'Awaiting'].index, inplace = True)

# converting to datetime
date_format = '%Y/%m/%d'
df['Day'] = pd.to_datetime(df['Day'], format=date_format)

#trimming to include time only
ind = df.iloc[0]['Scheduled Time'].find(" ")
df['Scheduled Time'] = df['Scheduled Time'].str[ind+1:]

ind = df.iloc[0]['Actual Arrival'].find(" ")
df['Actual Arrival'] = df['Actual Arrival'].str[ind+1:]

time_format = "%H:%M:%S"
df['Scheduled Time'] = pd.to_datetime(df['Scheduled Time'], format=time_format).dt.time

# Adding a Day of Week column
df['Day of Week'] = df['Day'].dt.day_name()

################### DASH APP ###################
dash.register_page(__name__, title="Ridership over Dates and Time")

# Layout
layout = html.Div([
    html.H1("Ridership Summary",
            style={'font-family': 'Segoe UI', 'padding': '0 2em'}),

    html.H2("All Time Sum of Riders On and Off",
            style={'font-family': 'Segoe UI', 'padding': '0 2em'}),
            
    dcc.Graph(id="total-route-ridership-graph", style={'font-family': 'Segoe UI', 'padding': '0 2em'}),

    # DROPDOWN MENU
    html.Div([
        # ROUTE DROPDOWN
        html.Div([
            dcc.Dropdown(
                id="route-selector",
                options=[{'label': route, 'value': route} for route in df['Route'].unique()],
                value=df['Route'].unique()[0],
                style={'font-family': 'Segoe UI', 'padding': '0 2em'}
            ),
            dcc.Dropdown(
                id='stop-selector',
                options=[],  # Initialize with an empty list
                value=[],
                multi=True,
                style={'max-height': '95px', 'overflow-y': 'auto', 'font-family': 'Segoe UI', 'padding-left': '2em'}
            )
        ], style={'width': '75%'}),

        # Day of the Week Selector
        html.Div([
            dcc.Dropdown(
                id='day-of-week-selector',
                options=[{'label': day, 'value': day} for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']] + [{'label': 'Everyday', 'value': 'Everyday'}],
                value='Everyday',
                style={'font-family': 'Segoe UI', 'padding': '0 2em'}
            )
        ], style={'width': '25%', 'padding-left': '2em'}),

        # DATE SLICER SLIDER
        html.Div([
            dcc.DatePickerRange(
                id='date-slider',
                start_date=df['Day'].min(),
                end_date=df['Day'].max(),
                display_format='YYYY-MM-DD',
                style={'font-family': 'Segoe UI', 'padding': '0 2em'}
            )
        ], style={'width': '75%'})
    ], style={'display': 'flex'}),


])
