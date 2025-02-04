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
file_name = 'Fall2024_RidershipData.csv'
# file_name = 'Summer2024_RidershipData.csv'
# file_name = '051524-051924_RidershipData.csv'

file_path = os.path.join(script_dir, '..','data', file_name)

# Read the CSV file
df = pd.read_csv(file_path)
################### MODIFY DATA ###################

date_format = '%Y/%m/%d'
df['Day'] = pd.to_datetime(df['Day'], format=date_format)

# Define the order of days of the week in chronological order
days_of_week_order = [
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
]

################### DASH APP ###################
dash.register_page(__name__)

layout = html.Div([
    # FILTERING OPTIONS
    html.Div([
        dcc.Dropdown(
            id='riders-selector',
            options=[
                {'label': 'Riders On', 'value': 'Riders On'},
                {'label': 'Riders Off', 'value': 'Riders Off'}
            ],
            value='Riders On',
            style={'width': '75%', 'display': 'inline-block', 'font-family': 'Segoe UI'}),
        dcc.Dropdown(
            id='route-selector',
            options=[
                {'label': route, 'value': route} for route in df['Route'].unique()
            ],
            multi=False,
            value='Waltham Shuttle',
            style={'width': '75%', 'display': 'inline-block','font-family': 'Segoe UI'}),
        dcc.Dropdown(
            id='aggregation-selector',
            options=[
                {'label': 'Sum', 'value': 'sum'},
                {'label': 'Average', 'value': 'avg'}
            ],
            value='sum',
            style={'width': '75%', 'display': 'inline-block', 'font-family': 'Segoe UI'}),
        dcc.DatePickerRange(
            id='date-slider',
            start_date=df['Day'].min(),
            end_date=df['Day'].max(),
            style={'width': '75%', 'display': 'inline-block', 'font-family': 'Segoe UI'}
        ),
    ], style={'display': 'flex'}),

    # TOP/BOTTOM 5 STOPS SUM
    # top-x-bar-overall
    dcc.Graph(id='top-5-overall-bar-chart', style={'width': '48%', 'display': 'inline-block'}),
    dcc.Graph(id='bottom-5-overall-bar-chart', style={'width': '48%', 'display': 'inline-block'}),

    #TOP/BOTTOM 5 STOPS BY DAY OF WEEK
    # top/bottom-stops-dayofweek
    dcc.Graph(id='top-stops-dayofweek'),
    dcc.Graph(id='bottom-stops-dayofweek'),

    # ALL STOPS RIDERSHIP
    # STOP MULTI SELECT
        html.Div([
            dcc.Dropdown(
                id='stop-multiselect',
                options=[],  # Initialize with an empty list
                value=[],
                multi=True,
                style={'max-height': '95px', 'overflow-y': 'auto', 'font-family': 'Segoe UI', 'padding-left': '2em'}
            )
        ], style={'width': '75%'}),
    dcc.Graph(id='stop-bar-chart')
])

###### TOP/BOTTOM 5 OVERALL ######
@callback(
    Output('top-5-bar-overall-chart', 'figure'),
    [Input('route-selector', 'value'),
     Input('date-slider', 'start_date'),
     Input('date-slider', 'end_date'),
     Input('riders-selector', 'value')]
)
def update_top_5_chart(selected_route, start_date, end_date, selected_riders):
    filtered_df = df[(df['Route'] == selected_route) &
                     (df['Day'] >= start_date) &
                     (df['Day'] <= end_date)]
    
    sorted_df = filtered_df.groupby(['Stop'])[selected_riders].sum().sort_values(ascending=False).head(10)
    
    title = f'Top 10 Stops by {selected_riders} for Route {selected_route}'
    fig = px.bar(sorted_df, x=selected_riders, y=sorted_df.index, title=title, color_discrete_sequence=['green'], text_auto=True, orientation='h')  # Set orientation to 'h' for horizontal bars
    return fig

@callback(
    Output('bottom-5-bar-overall-chart', 'figure'),
    [Input('route-selector', 'value'),
     Input('date-slider', 'start_date'),
     Input('date-slider', 'end_date'),
     Input('riders-selector', 'value')]
)
def update_bottom_5_chart(selected_route, start_date, end_date, selected_riders):
    filtered_df = df[(df['Route'] == selected_route) &
                     (df['Day'] >= start_date) &
                     (df['Day'] <= end_date)]
    
    sorted_df = filtered_df.groupby(['Stop'])[selected_riders].sum().sort_values().head(10)
    
    title = f'Bottom 10 Stops by {selected_riders} for Route {selected_route}'
    fig = px.bar(sorted_df, x=selected_riders, y=sorted_df.index, title=title, color_discrete_sequence=['red'], text_auto=True, orientation='h')  # Set orientation to 'h' for horizontal bars
    return fig

###### TOP/BOTTOM 5 BY DAY OF WEEK ######
@callback(
    [Output('top-stops-dayofweek', 'figure'), Output('bottom-stops-dayofweek', 'figure')],
    [Input('riders-selector', 'value'), Input('route-selector', 'value'), Input('aggregation-selector', 'value'),
     Input('date-slider', 'start_date'), Input('date-slider', 'end_date')]
)
def update_graphs(riders_option, selected_route, aggregation_option, start_date, end_date):
    filtered_df = df[(df['Route'] == selected_route) & (df['Day'] >= start_date) & (df['Day'] <= end_date)]

    if aggregation_option == 'sum':
        grouped_df = filtered_df.groupby(['Stop', 'Day Of Week'])[riders_option].sum().reset_index()
    else:
        grouped_df = filtered_df.groupby(['Stop', 'Day Of Week'])[riders_option].mean().reset_index()

    # Get the top 5 stops with the all-time highest Riders On/Off
    top_stops = grouped_df.groupby('Stop')[riders_option].sum().nlargest(10).index
    bottom_stops = grouped_df.groupby('Stop')[riders_option].sum().nsmallest(10).index

    # Create DataFrames to store daily data for top and bottom stops
    top_daily_data = grouped_df[grouped_df['Stop'].isin(top_stops)]
    bottom_daily_data = grouped_df[grouped_df['Stop'].isin(bottom_stops)]

    # Create a color mapping for stops
    color_mapping = {}
    common_stops = set(top_stops).intersection(bottom_stops)
    for stop in common_stops:
        color_mapping[stop] = px.colors.qualitative.Plotly[len(color_mapping) % len(px.colors.qualitative.Plotly)]

    # Create clustered vertical bar charts for the top and bottom stops with common color mapping
    fig_top = px.bar(top_daily_data, 
                     x='Day Of Week', 
                     y=riders_option, 
                     color='Stop',
                     title=f'Highest 10 Stops for {riders_option} by Day of Week', 
                     barmode='group',
                     color_discrete_map=color_mapping,
                     text_auto=True)  # Updated title and color mapping
    fig_bottom = px.bar(bottom_daily_data, 
                        x='Day Of Week', 
                        y=riders_option, color='Stop',
                        title=f'Lowest 10 Stops for {riders_option} by Day of Week', 
                        barmode='group',
                        color_discrete_map=color_mapping,
                        text_auto=True)  # Updated title and color mapping

    # Sort days of the week in chronological order
    fig_top.update_xaxes(categoryorder='array', categoryarray=days_of_week_order)
    fig_bottom.update_xaxes(categoryorder='array', categoryarray=days_of_week_order)
    
    return fig_top, fig_bottom

######## OVERALL STOP ###########
@callback(
    [Output('stop-multiselect', 'options'),
     Output('stop-multiselect', 'value')],  # Set the initial value of stop-multiselect
    Input('route-selector', 'value')
)
def update_stop_selector_options(selected_route):
    stops_for_route = df[df['Route'] == selected_route]['Stop'].unique()
    stop_options = [{'label': stop, 'value': stop} for stop in stops_for_route]
    return stop_options, stops_for_route  # Set the initial value

# RIDERSHIP BY STOP
@callback(
    Output('stop-bar-chart', 'figure'),
    [Input('route-selector', 'value'),
     Input('date-slider', 'start_date'),
     Input('date-slider', 'end_date'),
     Input('stop-multiselect', 'value'),
     Input('day-of-week-selector', 'value'),
     Input('calc-method-dropdown', 'value')]
)
def update_stop_bar_chart(selected_route, start_date, end_date, selected_stops, selected_day, calc_method):
    filtered_df = df[(df['Route'] == selected_route) & 
                     (df['Stop'].isin(selected_stops)) & 
                     (df['Day'] >= start_date) & 
                     (df['Day'] <= end_date)]
    
    if selected_day != 'Everyday':
        filtered_df = filtered_df[filtered_df['Day of Week'] == selected_day]

    if calc_method == 'Average':
        stop_data = filtered_df.groupby('Stop')[['Riders On', 'Riders Off']].mean().reset_index()
    else:
        stop_data = filtered_df.groupby('Stop')[['Riders On', 'Riders Off']].sum().reset_index()
    
    fig = go.Figure(data=[
        go.Bar(name='Riders On', 
               x=stop_data['Stop'], 
               y=stop_data['Riders On'],
                text=stop_data['Riders On'],  # Add text labels
                textposition='auto'  # Position text labels to be visible
                ),
        go.Bar(name='Riders Off', 
               x=stop_data['Stop'], 
               y=stop_data['Riders Off'],
                text=stop_data['Riders Off'],  # Add text labels
                textposition='auto'  # Position text labels to be visible
            )
    ])
    
    fig.update_layout(barmode='group', title=f'{calc_method} Riders On and Off at Stops for Route {selected_route}')
    return fig
