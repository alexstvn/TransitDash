from dash import dcc, html
import dash

dash.register_page(__name__, path='/')

layout = html.Div([
    html.Section([
        html.H1('Telling Stories Through Ridership Data'),
        html.P('This web application looks at ridership report data over a particular period of time through different perspectives, each of which can be viewed through a different tab.'),
    ]),

    html.Section([
        html.H2('Ridership: Average Summary'),
        html.P('This dashboard includes two bar charts: one showing the average Riders On/Off by stop and the other showing the average Riders On/Off by Scheduled Time.'),
        html.P('It includes filter options that allow you to focus on a particular route and a date range which filters out data that does not fall within the selected date range.'),
        html.P('The average ridership by stop graph can also be modified to exclude particular stops if you want to remove stops that are considerably higher than others and skew the scaling of the data.'),
        html.P('The average ridership by scheduled time graph includes a stop selector so that you can focus on a particular stop’s ridership by time.'),
    ]),

    html.Section([
        html.H2('Ridership: Capacity'),
        html.P('This dashboard includes two bar charts, one displaying the frequency of a particular capacity being met by day of week and one by scheduled hour. The calculation of the capacity reached is determined by dividing Riders Cumulative (the amount of riders on the bus) by the vehicle capacity.'),
        html.P('The user is able to narrow down what data is included by selecting the route, date range to include, and the capacity percentage range we want to check is being met.'),
        html.P('For analyzing the frequency of capacity reached by scheduled time, the user is also able to select a particular day of the week to see if there are trends for those particular days.'),
    ]),

    html.Section([
        html.H2('Ridership: Outliers'),
        html.P('This particular dashboard dives deeper into the data by highlighting the most and least frequented stops, depending on Riders On and Off (based on what is selected).'),
        html.P('It summarizes the stops first, by showing the overall sum of riders getting on or off. Then the next two graphs break it down further by day of week.'),
    ])
], style={'padding': '2em'})
