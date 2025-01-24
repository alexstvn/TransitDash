# IMPORTS
import dash
from dash import Dash, html, dcc
import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, use_pages=True, external_stylesheets=external_stylesheets)

# Custom style for the buttons
button_style = {
    'display': 'inline-block',
    'margin': '10px',
    'padding': '10px 20px',
    'font-size': '16px',
    'text-align': 'center',
    'text-decoration': 'none',
    'cursor': 'pointer',
    'border-radius': '5px',
    'border': '1px solid #ccc',
    'background-color': '#f8f8f8',
    'color': '#333',
}

links_container_style = {
    'whiteSpace': 'nowrap',
}

app.layout = html.Div([
    html.H1('DPV Ridership Data', style={'font-family': 'Segoe UI'}),
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']}", 
                     style=button_style,
                     href=page["relative_path"])
        ) for page in dash.page_registry.values()
    ], style=links_container_style),
    dash.page_container
])

if __name__ == '__main__':
    app.run(debug=False,port=8040)