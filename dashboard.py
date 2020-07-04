import dash
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import re

import dash_bootstrap_components as dbc


from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State

from datetime import datetime
from datetime import timedelta
from golf_bokning import TeeTimes
from pprint import pprint

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP], 
    suppress_callback_exceptions=True,
    prevent_initial_callbacks=True
    )
server = app.server


TODAYS_DATE = datetime.today().strftime('%Y%m%d')
CURRENT_TIME = datetime.now().strftime('%H%M%S')
MAX_DATE = datetime.today() + timedelta(days=365)
TEE_TIME = TeeTimes(username=None, password=None, date=None)
USERNAME_FORMAT = r"(^\d\d\d\d\d\d-\d\d\d$)"
DATE_FORMAT = r"(^\d{8}$)"
TIME_FORMAT = r"(^\d{2}:\d{2}$)"


app.layout = dbc.Container([

    dbc.Jumbotron([
        dbc.Container([
            html.H1("Find TeeTimes", className="display-3"),
            html.P(
                "View all available TeeTimes - For Golfbroes",
                className="lead",
            ),
            ],
            fluid=True,
            ),
        ],
        fluid=True,
        style={'margin-bottom': '0px'},
        className="mb-3"
    ),
    dbc.Row([
        dbc.Col(
            dcc.Input(
                id="Username",
                type='text',
                placeholder="Username",
                className="mb-3"
            ),
        ),
        dbc.Col([
            dcc.Input(
                id="Password",
                type='password',
                placeholder="Password",
                className="mb-3"
            ),
        ]),
        dbc.Col([
            dcc.DatePickerSingle(
                id='date-picker',
                min_date_allowed=TODAYS_DATE,
                max_date_allowed=MAX_DATE,
                initial_visible_month=TODAYS_DATE,
                date=TODAYS_DATE,
                display_format='DD/MM/YYYY',
                className="mb-3"
            ),
            html.Div(id='output-container-date-picker')
        ]),
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Input(
                id="Email",
                type='email',
                placeholder="Email",
                className="mb-3",
            ),
        ], width=4),
        dbc.Col([
            dcc.Input(
                id="Time",
                type='text',
                placeholder="Start time, e.g. 10:00",
                className="mb-3",
            ),
        ], width=4),
        dbc.Col([
            dbc.Button("Submit", id="submit", className="mr-2", n_clicks=0),
        ]),

    ]),
    dbc.Row([
        dbc.Col(
            id='submit-output-container'
        ),
    ]),

])
@app.callback(
    Output("submit-output-container", "children"), 
    [Input("submit", "n_clicks"),
    ],
    [
         State("Username", "value"),
         State('Password', 'value'),
         State('Email', 'value'),
         State("date-picker", "date"),
         State("Time", "value")
    ]
)
def on_button_click(n, username, password, email, date, time):
    """Very complex logic to check user input..."""
    if n:
        if username:
            if not re.match(USERNAME_FORMAT, username):
                return f'Username format is incorrect, {username} should be YYMMDD-XXX'
            else:
                TEE_TIME.username = username
                if not password:
                    return f'Please write password before submiting'
                else:
                    TEE_TIME.password = password
            if date:
                if not re.match(DATE_FORMAT, date):
                    formated_date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d')
                else:
                    formated_date = date
                if time:
                    if not re.match(TIME_FORMAT, time):
                        return f'Time should be specified as 10:40'
                    else:
                        formated_time = time[:2] +time[3:5] + '00'
                        TEE_TIME.date = formated_date +'T'+ formated_time
                else:
                    TEE_TIME.date = formated_date +'T'+ CURRENT_TIME
        print(TEE_TIME.date)

@app.callback(
        Output("output-container-date-picker", "children"), 
    [
        Input("date-picker", "date"),
    ])
def output_text(date):
    print(date)

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')