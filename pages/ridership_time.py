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
file_name = 'Summer2024_RidershipData.csv'
# file_name = '051524-051924_RidershipData.csv'

file_path = os.path.join(script_dir, '..','data', file_name)

# Read the CSV file
df = pd.read_csv(file_path)

################### MODIFY DATA ###################
#removing cancelled trips, skipped/waiting stops (bc no riders getting on)
df.drop(df[df['Ride State'] == 'Cancelled'].index, inplace = True)
df.drop(df[df['Stop State'] == 'Skipped'].index, inplace = True)
df.drop(df[df['Stop State'] == 'Awaiting'].index, inplace = True)

# Removing exact duplicate rows
df.drop_duplicates(inplace=True)

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
    html.H1("Ridership Summary", style={'font-family': 'Segoe UI', 'padding': '0 2em'}),

    # AVERAGE STOP RIDERSHIP GRAPH
    # dcc.Graph(id='stop-bar-chart'), # MOVE TO STOP UTILIZATION

    ########### FILTERS / DROPDOWN MENU ###########
    html.Div([
        # ROUTE DROPDOWN
        html.Div([
            dcc.Dropdown(
                id="route-selector",
                options=[{'label': route, 'value': route} for route in df['Route'].unique()],
                value=df['Route'].unique()[0],
                style={'font-family': 'Segoe UI', 'padding': '0 2em'}
            )
        ], style={'width': '75%'}),

        # DAY OF WEEK SELECTION
        html.Div([
            dcc.Dropdown(
                id='day-of-week-selector',
                options=[{'label': day, 'value': day} for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']] + [{'label': 'Weekend', 'value': ['Saturday','Sunday']}] + [{'label': 'Everyday', 'value': 'Everyday'}],
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

    
    # CALCULATION METHOD
    html.Div([
        html.Label("Calculation Method:", style={'font-family': 'Segoe UI', 'width': '25%', 'display': 'inline-block'}),
        dcc.Dropdown( id="calc-method-dropdown",
            options=[
                {'label': 'Average', 'value': 'Average'},
                {'label': 'Sum', 'value': 'Sum'}
            ],
            value='Sum',  # Default to "Average"
            style={'font-family': 'Segoe UI', 'width': '75%', 'display': 'inline-block'}
        )
    ], style={'display': 'flex', 'padding': '0 2em'}),

    ########## BY SEMESTER HERE ##########
    dcc.Graph(id="semester-ridership-graph", style={'padding': '0 2em'}),

    ########## BY MONTH HERE ##########
    dcc.Graph(id="monthly-ridership-graph", style={'padding': '0 2em'}),

    ########## BY WEEK HERE ##########
    dcc.Graph(id="weekly-ridership-graph", style={'padding': '0 2em'}),

    ########## BY DAY/DATE HERE ##########
    # DROPDOWN FOR WEEKLY RANGES
    html.Div([
        html.Label("Select Date Range:", style={'font-family': 'Segoe UI', 'width': '25%', 'display': 'inline-block'}),
        dcc.Dropdown(
            id="date-range-dropdown",
            options=[],  # Will be dynamically populated
            style={'font-family': 'Segoe UI', 'width': '75%', 'display': 'inline-block'}
        ),
    ], style={'display': 'flex', 'padding': '0 2em'}),

    html.Div([
        html.Label("Group Data:", style={'font-family': 'Segoe UI', 'width': '25%', 'display': 'inline-block'}),
        dcc.Dropdown(
            id="group-data-dropdown",
            options=[
                {'label': 'By Week', 'value': 'By Week'},
                {'label': 'Entire Dates with Selected Route', 'value': 'Entire Dates'}
            ],
            value='By Week',  # Default to "By Week"
            style={'font-family': 'Segoe UI', 'width': '75%', 'display': 'inline-block'}
        ),
    ], style={'display': 'flex', 'padding': '0 2em'}),

    # RIDERSHIP-DAILY-BY-WEEK
    # this calculates total ridership over 1 day shown as a week or all time by route (formerly (ridership-dates-graph))
    dcc.Graph(id="ridership-daily-by-week-graph", style={'font-family': 'Segoe UI', 'padding': '0 2em'}),
    
    ########## BY TIME HERE ##########
    # RIDERSHIP-30MIN-TIME-GRAPH
    # This breaks down and calculates ridership over 30 minute increments.
    # Overall Ridership by Scheduled Time Graph (was called overall-ridership-time-graph)
    dcc.Graph(id="ridership-30min-time-graph", style={'font-family': 'Segoe UI', 'padding': '0 2em'}),

    # STOP RIDERSHIP OVER TIME
    # Stop Dropdown
    html.Div([
        html.Label("Select Stop:", style={'font-family': 'Segoe UI', 'width': '25%', 'display': 'inline-block'}),
        dcc.Dropdown(
            id="stop-single-select-dropdown", # formerly stop-dropdown
            options=[],
            value='Admissions',
            style={'font-family': 'Segoe UI', 'width': '75%', 'display': 'inline-block'}
        ),
    ], style={'display': 'flex'}),

    # STOP-SCHEDULED-TIME-GRAPH
    # Given a particular stop, show the riders on/off by scheduled time.
    dcc.Graph(id="stop-scheduled-time-graph", style={'font-family': 'Segoe UI', 'padding': '0 2em'}),
    # formerly ridership-time-graph
])

########## BY-SEMESTER VISUALIZATIONS + DROPDOWNS ##########
@callback(
    Output("semester-ridership-graph", "figure"),
    [Input("route-selector", "value"),
     Input("date-slider", "start_date"),
     Input("date-slider", "end_date"),
     Input("calc-method-dropdown", "value"),
     Input("day-of-week-selector", "value")]
)
def update_semester_ridership_graph(selected_route, start_date, end_date, calc_method, selected_day):
    # Filter data for the selected route and date range
    filtered_df = df.loc[
                    (df['Route'] == selected_route) & 
                    (df['Day'] >= start_date) & 
                    (df['Day'] <= end_date)
                ].copy()
    
    if isinstance(selected_day, list):  # Check if selected_day is a list (for 'Weekend')
        filtered_df = filtered_df[filtered_df['Day of Week'].isin(selected_day)]
    elif selected_day != 'Everyday':  # Handle individual days
        filtered_df = filtered_df[filtered_df['Day of Week'] == selected_day]


    # Add Semester column based on date
    filtered_df['Semester'] = 'Fall ' + filtered_df['Day'].dt.year.astype(str)
    filtered_df.loc[filtered_df['Day'].dt.month < 6, 'Semester'] = 'Spring ' + filtered_df['Day'].dt.year.astype(str)

    filtered_df['Riders On'] = pd.to_numeric(filtered_df['Riders On'], errors='coerce')
    filtered_df = filtered_df.dropna(subset=['Riders On'])  # Drop rows with NaN values
    
    if calc_method == 'Average':
        # filtered_df['Riders On'] = pd.to_numeric(filtered_df['Riders On'], errors='coerce')
        grouped = filtered_df.groupby('Semester')['Riders On'].mean().reset_index()
    else:
        grouped = filtered_df.groupby('Semester')['Riders On'].sum().reset_index()

    # Group by Semester
    # grouped = filtered_df.groupby('Semester')['Riders On'].agg(calc_method.lower()).reset_index()

    # Create pie chart
    fig = px.pie(
        grouped,
        names='Semester',
        values='Riders On',
        title="Ridership by Semester",
        labels={"Semester": "Semester", "Riders On": "Riders On"},
    )
    fig.update_traces(textposition="auto", textinfo='value')
    return fig


########## BY-MONTH VISUALIZATIONS + DROPDOWNS ##########
@callback(
    Output("monthly-ridership-graph", "figure"),
    [Input("route-selector", "value"),
     Input("date-slider", "start_date"),
     Input("date-slider", "end_date"),
     Input("calc-method-dropdown", "value")]
)
def update_monthly_ridership_graph(selected_route, start_date, end_date, calc_method):
    # Filter data for the selected route and date range
    filtered_df = df.loc[
        (df['Route'] == selected_route) & 
        (df['Day'] >= start_date) & 
        (df['Day'] <= end_date)
    ].copy()

    # Add two columns: one for Month-Year as datetime (for sorting) and one for text (for displaying)
    filtered_df['Month'] = filtered_df['Day'].dt.to_period('M').dt.to_timestamp()
    filtered_df['Month_Text'] = filtered_df['Day'].dt.strftime('%B %Y')

    # Convert 'Riders On' to numeric and drop NaN values
    filtered_df['Riders On'] = pd.to_numeric(filtered_df['Riders On'], errors='coerce')
    filtered_df = filtered_df.dropna(subset=['Riders On'])

    # Group data by Month
    if calc_method == 'Average':
        grouped = filtered_df.groupby('Month')['Riders On'].mean().reset_index()
    else:
        grouped = filtered_df.groupby('Month')['Riders On'].sum().reset_index()

    # Add the text version of the Month-Year to the grouped DataFrame for display
    grouped['Month_Text'] = grouped['Month'].dt.strftime('%B %Y')
    grouped = grouped.sort_values(by='Month', ascending=True)

    # Create bar graph
    fig = px.bar(
        grouped,
        x="Month_Text",  # Display the text version of Month-Year
        y="Riders On",
        text="Riders On",
        title="Ridership by Month",
        labels={"Month_Text": "Month", "Riders On": "Riders On"}
    )
    fig.update_traces(textposition="auto")

    # Sort by the datetime column for chronological order
    fig.update_layout(
        xaxis_tickangle=-45
    )

    return fig

########## BY-WEEK VISUALIZATIONS + DROPDOWNS ##########
@callback(
    Output("weekly-ridership-graph", "figure"),
    [Input("route-selector", "value"),
     Input("date-slider", "start_date"),
     Input("date-slider", "end_date"),
     Input("calc-method-dropdown", "value")]
)
def update_weekly_ridership_graph(selected_route, start_date, end_date, calc_method):
    # Filter data for the selected route and date range
    filtered_df = df.loc[
        (df['Route'] == selected_route) & 
        (df['Day'] >= start_date) & 
        (df['Day'] <= end_date)
    ].copy()

    # Add Week column (Start of the week)
    filtered_df.loc[:, 'Week'] = filtered_df['Day'].dt.to_period('W').apply(lambda r: r.start_time)

    # Ensure 'Riders On' is numeric and drop NaN values
    filtered_df['Riders On'] = pd.to_numeric(filtered_df['Riders On'], errors='coerce')
    filtered_df = filtered_df.dropna(subset=['Riders On']).copy()

    # Group data by 'Week' and calculate based on 'calc_method'
    if calc_method == 'Average':
        grouped = filtered_df.groupby('Week', as_index=False)['Riders On'].mean()
    else:
        grouped = filtered_df.groupby('Week', as_index=False)['Riders On'].sum()

    # Convert 'Week' column to string for Plotly
    grouped['Week'] = grouped['Week'].astype(str)

    # Check for empty data
    if grouped.empty:
        return px.bar(
            title="No Data Available",
            labels={"Week": "Week Starting", "Riders On": "Riders On"}
        )

    # Create bar graph
    fig = px.bar(
        grouped,
        x="Week",
        y="Riders On",
        text="Riders On",
        title="Ridership by Week",
        labels={"Week": "Week Starting", "Riders On": "Riders On"}
    )
    fig.update_traces(textposition="auto")
    return fig


########## BY-DATE/DAY VISUALIZATIONS + DROPDOWNS HERE ##########
###*** Daily Route Ridership based on week selection dropdown ***###

# Update Week Date Ranges Single Select Dropdown (REVISE HERE AT SOME POINT)
@callback(
    Output("date-range-dropdown", "options"),
    Input("date-slider", "start_date"),
    Input("date-slider", "end_date")
)
def update_date_range_dropdown(start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    week_ranges = []

    # Split the date range into week-long intervals (Monday-Sunday)
    current_week_start = date_range[0]
    for date in date_range:
        if date.weekday() == 0 and date != date_range[0]:  # Start a new week on Monday
            week_ranges.append((current_week_start, date - pd.Timedelta(days=1)))
            current_week_start = date
    week_ranges.append((current_week_start, date_range[-1]))  # Last partial week

    # Format each week range for display in dropdown
    week_options = [
        {'label': f"{start.strftime('%m/%d')} - {end.strftime('%m/%d')}", 'value': (start, end)}
        for start, end in week_ranges
    ]
    return week_options

#~~~~~~ Daily Ridership based on Selected Week Graph ~~~~~~~
@callback(
    Output("ridership-daily-by-week-graph", "figure"),
    [Input("route-selector", "value"),
     Input("date-slider", "start_date"),
     Input("date-slider", "end_date"),
     Input("date-range-dropdown", "value"),
     Input("group-data-dropdown", "value")]
)
def update_ridership_daily_by_week_graph(selected_route, start_date, end_date, selected_week_range, group_data):
    if group_data == 'By Week':
        if selected_week_range:
            start_date, end_date = selected_week_range  # Override with the selected week range

        # Filter data within the selected route and date range
        filtered_df = df[(df['Day'] >= start_date) & 
                         (df['Day'] <= end_date)]

        # Group by Day and Route, calculate daily sum of 'Riders On'
        daily_ridership = filtered_df.groupby(['Day', 'Route'])['Riders On'].sum().reset_index()
        daily_ridership['Day'] = pd.to_datetime(daily_ridership['Day'])  # Ensure 'Day' is datetime type
        daily_ridership = daily_ridership.sort_values('Day')  # Sort by date
        daily_ridership['Day'] = daily_ridership['Day'].dt.strftime('%m/%d')  # Format dates as mm/dd for display

        # Create stacked bar chart
        fig = px.bar(
            daily_ridership,
            x="Day",
            y="Riders On",
            color="Route",
            title="Daily Ridership by Route within Selected Week Range",
            labels={"Day": "Date", 
                    "Riders On": "Total Riders On"},
            category_orders={"Day": sorted(daily_ridership['Day'].unique())},  # Sort x-axis by date order
            text="Riders On"  # Add text for each segment
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Total Riders On",
            font=dict(family="Segoe UI", size=12, color="black")
        )
        fig.update_traces(textposition='auto')

    elif group_data == 'Entire Dates':
        # Filter data for the selected route and date range
        filtered_df = df[(df['Route'] == selected_route) & 
                         (df['Day'] >= start_date) & 
                         (df['Day'] <= end_date)]

        # Group by Day, calculate the total sum of 'Riders On'
        daily_totals = filtered_df.groupby('Day')['Riders On'].sum().reset_index()
        daily_totals['Day'] = pd.to_datetime(daily_totals['Day'])  # Ensure 'Day' is datetime type
        daily_totals = daily_totals.sort_values('Day')  # Sort by date
        daily_totals['Day'] = daily_totals['Day'].dt.strftime('%m/%d')  # Format dates as mm/dd for display

        # Create bar chart
        fig = px.bar(
            daily_totals,
            x="Day",
            y="Riders On",
            title=f"Total Riders On for Route {selected_route}",
            labels={"Day": "Date", 
                    "Riders On": "Total Riders On"},
            category_orders={"Day": sorted(daily_totals['Day'].unique())}  # Sort x-axis by date order
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Total Riders On",
            font=dict(family="Segoe UI", size=12, color="black")
        )
        fig.update_traces(text=daily_totals['Riders On'], textposition='auto')

    return fig

##########---------------end-by-date-day-section----------------##########

########## BY-TIME VISUALIZATIONS + DROPDOWNS HERE ##########
###*** Ridership in 30 Minute Increments Graph ***###
@callback(
    Output("ridership-30min-time-graph", "figure"),
    [Input('route-selector', 'value'),
     Input('date-slider', 'start_date'),
     Input('date-slider', 'end_date'),
     Input('day-of-week-selector', 'value')]
)
def update_ridership_30min_time_graph(selected_route, start_date, end_date, selected_day):
    # Copy the dataframe and apply the filters
    filtered_df = df[(df['Route'] == selected_route) & 
                     (df['Day'] >= start_date) & 
                     (df['Day'] <= end_date)]
    
    if isinstance(selected_day, list):  # Check if selected_day is a list (for 'Weekend')
        filtered_df = filtered_df[filtered_df['Day of Week'].isin(selected_day)]
    elif selected_day != 'Everyday':  # Handle individual days
        filtered_df = filtered_df[filtered_df['Day of Week'] == selected_day]

    # Generate 30-minute time blocks from 00:00 to 23:59
    time_blocks = pd.date_range("00:00", "23:59", freq="30T").time
    time_df = pd.DataFrame(time_blocks, columns=["Time"])
    time_df["Riders On"] = 0
    time_df["Riders Off"] = 0

    # Populate time_df by summing Riders On and Off for each 30-minute block
    for _, row in filtered_df.iterrows():
        # Find the 30-minute block to place this row in
        time = row['Scheduled Time']
        block_time = min(time_blocks, key=lambda t: abs(pd.Timestamp.combine(pd.Timestamp.min, time) - pd.Timestamp.combine(pd.Timestamp.min, t)))
        idx = time_df[time_df["Time"] == block_time].index[0]
        
        # Accumulate the values
        time_df.at[idx, "Riders On"] += row["Riders On"]
        time_df.at[idx, "Riders Off"] += row["Riders Off"]

    # Filter out rows where both Riders On and Riders Off are zero
    time_df = time_df[(time_df["Riders On"] > 0) | (time_df["Riders Off"] > 0)]

    # Create the stacked bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=time_df["Time"],
            y=time_df["Riders On"],
            name="Riders On",
            text=time_df["Riders On"], 
            textposition='auto'
        ),
        go.Bar(
            x=time_df["Time"],
            y=time_df["Riders Off"],
            name="Riders Off",
            text=time_df["Riders Off"], 
            textposition='auto'
        )
    ])

    fig.update_layout(
        barmode="stack",
        title="Overall Ridership for all Stops by Time (30-Minute Intervals)",
        xaxis_title="Time of Day",
        yaxis_title="Total Riders On/Off",
        font=dict(family="Segoe UI", size=12, color="black")
    )
    
    return fig

###*** Specific Stop Ridership by Time Graph + Dropdown ***###
#~~~~~~ Stop Single Select Dropdown ~~~~~~~
@callback(
    Output("stop-single-select-dropdown", "options"),
    Input("route-selector", "value")
)
def update_stop_options(selected_route):
    if selected_route is None:
        return []
    
    stop_options = [{'label': stop, 'value': stop} for stop in df[df['Route'] == selected_route]['Stop'].unique()]
    return stop_options

#~~~~~~ Specific Stop Ridership by Scheduled Time ~~~~~~
@callback(
    Output("stop-scheduled-time-graph", "figure"),
    [Input("stop-single-select-dropdown", "value"),
     Input("route-selector", "value"),
     Input("date-slider", "start_date"),
     Input("date-slider", "end_date"),
     Input("day-of-week-selector", "value"),
     Input("calc-method-dropdown", "value")]
)
def update_stop_scheduled_time_graph(selected_stop, selected_route, start_date, end_date, selected_day, calc_method):
    filtered_data = df[(df['Stop'] == selected_stop) & 
                       (df['Route'] == selected_route) &
                       (df['Day'] >= start_date) & 
                       (df['Day'] <= end_date)]
    
    if selected_day != 'Everyday':
        filtered_data = filtered_data[filtered_data['Day of Week'] == selected_day]

    if calc_method == 'Average':
        rider_data = filtered_data.groupby('Scheduled Time')[['Riders On', 'Riders Off']].mean().reset_index()
    else:
        rider_data = filtered_data.groupby('Scheduled Time')[['Riders On', 'Riders Off']].sum().reset_index()
    
    rider_data['Riders On'] = rider_data['Riders On'].round(2)
    rider_data['Riders Off'] = rider_data['Riders Off'].round(2)

    fig = go.Figure(data=[
        go.Bar(
            x=rider_data['Scheduled Time'],
            y=rider_data['Riders On'],
            name='Riders On',
            text=rider_data['Riders On'],
            textposition='auto'
        ),
        go.Bar(
            x=rider_data['Scheduled Time'],
            y=rider_data['Riders Off'],
            name='Riders Off',
            text=rider_data['Riders Off'],
            textposition='auto'
        )
    ])
    
    fig.update_layout(barmode='stack',
                      title=f"{calc_method} Riders On/Off for Stop: {selected_stop}, Route: {selected_route}",
                      xaxis_title="Scheduled Time",
                      yaxis_title=f"{calc_method} Riders On/Off",
                      font=dict(family='Segoe UI', size=12, color='black'))
    
    return fig

##########---------------end-by-time-section----------------##########
