from dash import html, dcc
import dash_bootstrap_components as dbc

'''
Structure/Layout of the Settings sidebar
'''

sidebar = html.Div(
    [
    html.H5("Settings"),
    dbc.Card(dbc.CardBody(
        [

            html.H6("Camera", style={"font-size": "0.95em"}),
            dbc.ButtonGroup(
                [
                    dbc.Button('Def.', id='default-cam', n_clicks=0, style={"font-size": "0.85em"}),
                    dbc.Button('X-Y', id='x-y-cam', n_clicks=0, style={"font-size": "0.85em"}),
                    dbc.Button('X-Z', id='x-z-cam', n_clicks=0, style={"font-size": "0.85em"}),
                    dbc.Button('Y-Z', id='y-z-cam', n_clicks=0, style={"font-size": "0.85em"})
                ], vertical=True, size="sm",
            ),
            html.Hr(),

            dbc.Checkbox(label='Outline', value=True, id='sc-outline',
                         style={'text-align': 'left', "font-size": "0.85em"}),
            dbc.Checkbox(label='Atoms', value=True, id='sc-atoms', style={'text-align': 'left', "font-size": "0.85em"}),
            dbc.Checkbox(label='Cell', value=True, id='cell-boundaries', style={'text-align': 'left', "font-size": "0.85em"}),

            html.Hr(),

            html.H6("", id="sz/isosurf-label", style={"font-size": "0.95em"}),
            html.Div(dcc.Slider(4, 16, 2, value=10, id='sc-size', vertical=True, verticalHeight=150),
                     style={'margin-left': '1.2em'}),

            html.Hr(),

            html.H6("Opacity", id="opac-label", style={"font-size": "0.95em"}),
            dbc.Input(type="number", min=0.1, max=1, step=0.1, id="sc-opac", placeholder="0.1 - 1",
                      style={"width": "7em", 'margin-left': '1.5rem'}, size="sm"),

        ]
    ))], style={'text-align': 'center'})