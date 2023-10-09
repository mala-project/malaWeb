# IMPORTS
import json
import os
from collections import Counter

from mala_inference import run_mala_prediction
import dash
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
from dash import dcc, html, Patch
from dash.exceptions import PreventUpdate

# visualization
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go

# I/O
import ase.io
import dash_uploader as du

# CONSTANTS
ATOM_LIMIT = 200
# TODO implement caching of the dataset to improve performance
# as in: https://dash.plotly.com/performance

# TODO: implement patching so that figures are updated, nor recreated
# as in: https://dash.plotly.com/partial-properties

models = json.load(open("models/model_list.json"))
# "label" is the label visible in the apps dropdown ; "value"  is the value passed to the inference script. Ranges are to be surrounded by []


# PX--Graph Object Theme
templ1 = dict(layout=go.Layout(
    scene={
        'xaxis': {'showbackground': False,
                  'visible': False,
                  },
        'yaxis': {'showbackground': False,
                  'visible': False},
        'zaxis': {'showbackground': False,
                  'visible': False},
        'aspectmode': 'data'
    },
    paper_bgcolor='#f8f9fa',
))

templ2 = dict(layout=go.Layout(
    scene={
        'xaxis': {'showbackground': False,
                  'visible': True,
                  },
        'yaxis': {'showbackground': False,
                  'visible': True},
        'zaxis': {'showbackground': False,
                  'visible': True},
        'aspectmode': 'data'
    },
    paper_bgcolor='#fff',
))

default_scatter_marker = dict(marker=dict(
    size=12,
    opacity=1,
    line=dict(width=1, color='DarkSlateGrey')),
)

plot_layout = {
    'title': 'Plot',
    'height': '75vh',
    'width': '80vw',

}
orientation_style = {
    'title': 'x-y-z',
    'height': '3em',
    'width': '3em',
    'background': '#f8f9fa',
    'position': 'fixed',
    'margin-top': '75vh',
    'margin-right': '0.5vw'
}

removeHoverLines = go.layout.Scene(
            xaxis=go.layout.scene.XAxis(spikethickness=0),
            yaxis=go.layout.scene.YAxis(spikethickness=0),
            zaxis=go.layout.scene.ZAxis(spikethickness=0),
        )

# Graph-Object Scene
orient_template = {
    'xaxis': {
        'showgrid': False,
        'showbackground': False,
        'linecolor': 'red',
        'linewidth': 0,
        'ticks': 'inside',
        'showticklabels': False,
        'visible': False,
        'title': 'x',

    },
    'yaxis': {
        'showgrid': False,
        'showbackground': False,
        'linecolor': 'green',
        'linewidth': 0,
        'ticks': '',
        'showticklabels': False,
        'visible': False,
        'title': 'y'
    },
    'zaxis': {
        'showgrid': False,
        'showbackground': False,
        'linecolor': 'blue',
        'linewidth': 0,
        'ticks': '',
        'showticklabels': False,
        'visible': False,
        'title': 'z'
    },
    'bgcolor': '#f8f9fa',
}
'''
    'height': '8vh',
    'width': '8.33vw',
    
'''

dos_plot_layout = {
    'height': '400px',
    'width': '800px',
    'background': '#f8f9fa',
}

# TODO: IDEA: ability to en-/disable individual Atoms (that are in the uploaded file) and let MALA recalculate
#  -> helps see each Atoms' impact in the grid


print("_________________________________________________________________________________________")
print("STARTING UP...")

app = dash.Dash(__name__, external_stylesheets=[dbc.icons.BOOTSTRAP, dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)
server = app.server
app.title = 'MALAweb'

# configure upload folder
du.configure_upload(app, r"./upload", http_request_handler=None)
# for publicly hosting this app, add http_request_handler=True and implement as in:
# https://github.com/np-8/dash-uploader/blob/dev/docs/dash-uploader.md


# just needed for styling of some headings
indent = '      '

# -------------------------------
# Figs
    # Default fig for the main plot - gets overwritten on initial plot update, after that it gets patched on update
def_fig = go.Figure(go.Scatter3d(x=[1], y=[1], z=[1], showlegend=False))
def_fig.update_scenes(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, xaxis_showgrid=False,
                      yaxis_showgrid=False, zaxis_showgrid=False)

orient_fig = go.Figure()
orient_fig.update_scenes(orient_template)
orient_fig.update_layout(margin=dict(l=0, r=0, b=0, t=0), title=dict(text="test"))
orient_fig.add_trace(
    go.Scatter3d(x=[0, 1], y=[0, 0], z=[0, 0], marker={'color': 'red', 'size': 0}, line={'width': 6}, showlegend=False,
                 hoverinfo='skip'))
orient_fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 1], z=[0, 0], marker={'color': 'green', 'size': 0}, line={'width': 6},
                                  showlegend=False, hoverinfo='skip'))
orient_fig.add_trace(
    go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 1], marker={'color': 'blue', 'size': 0}, line={'width': 6}, showlegend=False,
                 hoverinfo='skip'))

orient_plot = dcc.Graph(id="orientation", responsive=True, figure=orient_fig, style=orientation_style,
                        config={'displayModeBar': False, 'displaylogo': False})

# ------------------------------------
# Tables
    # Energy table
row1 = html.Tr([html.Td("Band energy", style={'text-align': 'center', 'padding': 3, 'font-size': '0.85em'})],
               style={"font-weight": "bold"})
row2 = html.Tr([html.Td(0, id="bandEn", style={'text-align': 'right', 'padding': 5, 'font-size': '0.85em'})])
row3 = html.Tr([html.Td('Total energy', style={'text-align': 'center', 'padding': 3, 'font-size': '0.85em'})],
               style={"font-weight": "bold"})
row4 = html.Tr([html.Td(0, id="totalEn", style={'text-align': 'right', 'padding': 5, 'font-size': '0.85em'})])
row5 = html.Tr([html.Td("Fermi energy", style={'text-align': 'center', 'padding': 3, 'font-size': '0.85em'})],
               style={"font-weight": "bold"})
row6 = html.Tr(
    [html.Td("placeholder", id='fermiEn', style={'text-align': 'right', 'padding': 5, 'font-size': '0.85em'})])
table_body = [html.Tbody([row1, row2, row3, row4, row5, row6])]

table = dbc.Table(table_body, bordered=True, striped=True, style={'padding': 0, 'margin': 0})

    # List of ASE-atoms table
table_header = [html.Thead(html.Tr([html.Th("ID"), html.Th("X"), html.Th("Y"), html.Th("Z")]), )]   # , html.Th("Use to run MALA")
table_body = [html.Tbody([], id="atoms_list")]
atoms_table = dbc.Table(table_header + table_body, bordered=True)

# -----------------
# Left SIDEBAR content
menu = html.Div([
    # Logo Section
    html.Div([
        html.Img(src='https://avatars.githubusercontent.com/u/81354661?s=200&v=4', className="logo"),
        html.H2(children='MALA', style={'text-align': 'center'}),
        html.Div(children='''
                    Framework for machine learning materials properties from first-principles data.
                ''', style={'text-align': 'center'}),
    ], className="logo"),

    html.Hr(style={'margin-bottom': '2rem', 'margin-top': '1rem', 'width': '5rem'}),

    dbc.Card(html.H6(children='File-Upload', style={'margin': '5px'}, id="open-upload", n_clicks=0),
             style={"text-align": "center"}),

    dbc.Collapse(
        dbc.Card(dbc.CardBody(  # Upload Section
            html.Div([

                html.Div(children='''
                            Upload atom-positions via file!
                            ''', style={'text-align': 'center', 'font-size': '0.85em'}),

                html.Div(children='''
                            Supported files
                            ''', id="supported-files",
                         style={'text-align': 'center', 'font-size': '0.6em', 'text-decoration': 'underline'}),

                html.Br(),

                dbc.Popover(
                    dbc.PopoverBody(
                        "ASE supports the following file-formats: " + str(ase.io.formats.ioformats.keys())[11:-2]),
                    style={'font-size': "0.6em"},
                    target="supported-files",
                    trigger="legacy",
                ),

                # dash-uploader component (not vanilla)
                du.Upload(id="upload-data", text="Drag & Drop or Click to select"),
                    # Can't manage to extract list of ASE-supported extensions from these IOFormats in:
                    # print(ase.io.formats.ioformats),
                    # -> TODO property "fileformat" could be used in du.Upload() to restrict uploadable extensions (safety-reasons)

                html.Div("Awaiting upload..", id='output-upload-state',
                         style={'margin': '2px', "font-size": "0.85em", 'textAlign': 'center'}),

                html.Hr(style={'margin-bottom': '2rem', 'margin-top': '1rem', 'width': '5rem'}),

                dbc.Button("Edit", id="edit-input", color="success",
                           style={"line-height": "0.85em", 'height': 'min-content', 'width': '100%',
                                  'font-size': '0.85em'}),

                dbc.Button("reset", id="reset-data", color="danger",
                           style={"line-height": "0.85em", 'height': 'min-content',
                                  'font-size': '0.85em'})

            ], className="upload-section"
            ),
        )),
        id="collapse-upload",
        is_open=True,
    ),

    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Your Upload")),
        dbc.ModalBody([
            html.H6("The uploaded File contained the following atoms positions: "),
            html.Br(),


            dbc.Card(html.H6(children=[dbc.Row([dbc.Col(width=1), dbc.Col('List of Atoms', width=10), dbc.Col("⌄", width=1, id="open-atom-list-arrow")])], style={'margin': '5px'}, id="open-atom-list", n_clicks=0),
                         style={"text-align": "center"}),
            dbc.Collapse(
                    dbc.Card(dbc.CardBody(  # Upload Section
                        [
            atoms_table,
            #html.P("Tick all the Atoms you want to use to send to MALA (Default: All checked).\nSee below for a pre-render of the chosen Atom-positions:"),
                        ]

                    )),
                    id="collapse-atom-list",
                    style={"max-height": "30rem"},
                    is_open=False,
                ),

            dcc.Graph(id="atoms-preview"),

            html.Hr(style={'margin-bottom': '1rem', 'margin-top': '1rem'}),

            html.P("Choose the model that MALA should use for calculations"),
            dbc.Row([
                dbc.Col(dcc.Dropdown(id="model-choice", options=models, value=None, placeholder="-", optionHeight=45, style={"font-size": "0.95em"}), width=9),
                dbc.Col(dbc.Input(id="model-temp", disabled=True, type="number", min=0, max=10, step=1), width=2),
                dbc.Col(html.P("K", style={"margin-top": "0.5rem"}), width=1)
            ], className="g-1"),
            html.Br(),

            dbc.Alert(id="atom-limit-warning",
                      children="The amount of Atoms you want to display exceeds our threshold (" + str(
                          ATOM_LIMIT) + ") for short render times. Be aware that continuing with the uploaded data may negatively impact waiting times.",
                      color="warning"),
            # only to be displayed if ATOM_LIMIT is exceeded (maybe as an alert window too)


        ]),
        dbc.ModalFooter(
            dbc.Button(id="run-mala", style={'width': 'min-content'}, disabled=True, children=[
                dbc.Stack([
                        html.Div(dbc.Spinner(
                            dcc.Store(id="df_store"), size="sm", color="success"    # Spinner awaits change here
                                            ), style={'width': '40px'}),
                        html.Div("Run MALA"),
                        html.Div(style={'width': '40px'})
                    ], direction="horizontal"
                )
            ], color="success", outline=True), style={'justify-content': 'center'})
    ], id="upload-modal", size="lg", is_open=False),


    # TODO: Extract Inference to another Collapse below upload section. Have a reset for both upload and inference

], className="sidebar")

# Right SIDEBAR (default) content
r_content = html.Div([
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
            html.Div(dcc.Slider(6, 18, 2, value=12, id='sc-size', vertical=True, verticalHeight=150),
                     style={'margin-left': '1.2em'}),

            html.Hr(),

            html.H6("Opacity", id="opac-label", style={"font-size": "0.95em"}),
            dbc.Input(type="number", min=0.1, max=1, step=0.1, id="sc-opac", placeholder="0.1 - 1",
                      style={"width": "7em", 'margin-left': '1.5rem'}, size="sm"),

        ]
    ))], style={'text-align': 'center'})

# Bottom BAR content
bot_content = dbc.Container([

    dbc.Row([

        dbc.Col(dbc.Card(dbc.CardBody(table)), width='auto'),
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6('Density of State', style={'font-size': '0.85em', 'font-weight': 'bold'}),
            dcc.Graph(id="dos-plot", style={'width': '20vh', 'height': '10vh'}, config={'displaylogo': False})
        ])), width='auto', align='center'),

    ], style={'height': 'min-content', 'padding': 0}, justify='center')

])


# --------------------------
# Filling offcanvasses with respective content

# Left SIDEBAR
side_l = html.Div([
    dbc.Offcanvas(menu, id="offcanvas-l", is_open=True, scrollable=True, backdrop=False,
                  style={'width': '12rem', 'margin-top': '3rem', 'left': '0', 'border-top-right-radius': '5px',
                         'border-bottom-right-radius': '5px',
                         'height': 'min-content',
                         'box-shadow': 'rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px',
                         }
                  )
])

# Right SIDEBAR
side_r = html.Div([
    dbc.Offcanvas(r_content, id="offcanvas-r-sc", is_open=False,
                  style={'width': '9rem', 'height': 'min-content',
                         'margin-top': '3em',
                         'margin-right': '0', 'border-top-left-radius': '5px', 'border-bottom-left-radius': '5px',
                         'box-shadow': 'rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px', },
                  scrollable=True, backdrop=False, placement='end'),
])

# Bottom BAR
bot = html.Div([dbc.Offcanvas(bot_content, id="offcanvas-bot", is_open=False,
                              style={'height': 'min-content', 'width': 'max-content', 'border-radius': '5px',
                                     'background-color': 'rgba(248, 249, 250, 1)',
                                     'left': '0',
                                     'right': '0',
                                     'margin': 'auto',
                                     'bottom': '0.5em',
                                     'box-shadow': 'rgba(0, 0, 0, 0.3) 0px 0px 16px -8px',
                                     'padding': -30
                                     },
                              scrollable=True, backdrop=False, placement='bottom')])

# button to open bottom bar
bot_button = html.Div(dbc.Offcanvas([

    dbc.Row(
        dbc.Col(dbc.Button(html.P("Energy / Density of State",
                                  style={"line-height": "0.65em", "font-size": "0.65em"}),
                           id="open-bot", style={
                "width": "10em",
                "height": "1.2em",
                "position": "absolute",
                "left": "50%",
                "-webkit-transform": "translateX(-50%)",
                "transform": "translateX(-50%)",
                'bottom': '0.5em'
            }, n_clicks=0), width=1)
        , )

], id="open-bot-canv", style={'height': 'min-content',
                              'background-color': 'rgba(0, 0, 0, 0)', 'border': '0'},
    is_open=False, scrollable=True, backdrop=False, close_button=False, placement='bottom')
)

# ---------------------------------
# Plots for the created Figures
main_plot = [

    dcc.Store(id="cam_store"),

    dbc.Card(dbc.CardBody(
        [
            dbc.Row([
                dcc.Graph(id="orientation", responsive=True, figure=orient_fig, style=orientation_style,
                          config={'displayModeBar': False, 'displaylogo': False, 'showAxisDragHandles': True}),

                dcc.Graph(id="scatter-plot", responsive=True, figure=def_fig, style=plot_layout,
                          config={'displaylogo': False}),
            ]),

            # Tools
            dbc.Row([
                html.Hr(),
                dbc.Button(html.P("Tools", style={"line-height": "0.65em", "font-size": "0.65em"}),
                           id="open-sc-tools", style={"width": "5em", "height": "1.2em"}, n_clicks=0)
            ], justify="center", style={"text-align": "center"}),

            dbc.Row(
                dbc.Collapse(
                    dbc.Card(dbc.CardBody(
                        [
                            dbc.Row([
                                # Buttons
                                dbc.Col(
                                    dbc.ButtonGroup(
                                        [
                                            dbc.Button('X', id='sc-active-x', active=False, outline=True,
                                                       color="danger", n_clicks=0),
                                            dbc.Button('Y', id='sc-active-y', active=False, outline=True,
                                                       color="success", n_clicks=0),
                                            dbc.Button('Z', id='sc-active-z', active=False, outline=True,
                                                       color="primary", n_clicks=0),
                                            dbc.Button("Density", id='active-dense', active=False, outline=True,
                                                       color="dark", n_clicks=0)
                                        ],
                                        vertical=True,
                                    ), width=1),

                                # Sliders
                                dbc.Col([
                                    # TODO: Triggers need work
                                    # TODO: rangesliders are only optimized with the example cell used in current models. Differently sheared planes will mess things up, as will cells with bigger datasets (minimum slice will grow/shrink)
                                    dbc.Row([
                                        dbc.Col(dcc.RangeSlider(id='range-slider-cs-x',
                                                                disabled=True,
                                                                min=0,
                                                                max=1,
                                                                #step=None,
                                                                marks=None,
                                                                pushable=10,            # the sheared plane needs a range of values to be able to slice down to approx. 1 layer
                                                                updatemode='drag')),
                                        dbc.Col(html.Img(id="reset-cs-x", src="/assets/x.svg", n_clicks=0,
                                                         style={'width': '1.25em'}), width=1)
                                    ], style={"margin-top": "7px"}),  # X-Axis
                                    dbc.Tooltip(id="x-lower-bound", target="range-slider-cs-x", trigger="hover focus", placement="left"),
                                    dbc.Tooltip(id="x-higher-bound", target="range-slider-cs-x", trigger="hover focus", placement="right"),


                                    dbc.Row([
                                        dbc.Col(dcc.RangeSlider(
                                            id='range-slider-cs-y',
                                            disabled=True,
                                            pushable=0,
                                            min=0, max=1,
                                            marks=None,
                                            updatemode='drag')),
                                        dbc.Col(html.Img(id="reset-cs-y", src="/assets/x.svg", n_clicks=0,
                                                         style={'width': '1.25em'}), width=1)
                                    ]),  # Y-Axis
                                    dbc.Tooltip(id="y-lower-bound", target="range-slider-cs-y", trigger="hover focus", placement="left"),
                                    dbc.Tooltip(id="y-higher-bound", target="range-slider-cs-y", trigger="hover focus", placement="right"),

                                    dbc.Row([
                                        dbc.Col(dcc.RangeSlider(
                                            id='range-slider-cs-z',
                                            disabled=True,
                                            pushable=0,
                                            min=0, max=1,
                                            marks=None,
                                            updatemode='drag')),
                                        dbc.Col(html.Img(id="reset-cs-z", src="/assets/x.svg", n_clicks=0,
                                                         style={'width': '1.25em'}), width=1)

                                    ]),  # Z-Axis
                                    dbc.Tooltip(id="z-lower-bound", target="range-slider-cs-z", trigger="hover focus", placement="left"),
                                    dbc.Tooltip(id="z-higher-bound", target="range-slider-cs-z", trigger="hover focus", placement="right"),

                                    dbc.Row([

                                        dbc.Col(dcc.RangeSlider(
                                            id='range-slider-dense',
                                            disabled=True,
                                            pushable=True,
                                            min=0, max=1,
                                            marks=None,
                                            updatemode='drag')),
                                        dbc.Col(html.Img(id="reset-dense", src="/assets/x.svg", n_clicks=0,
                                                         style={'width': '1.25em', 'position': 'float'}),
                                                width=1),

                                    ]),  # Density
                                    dbc.Tooltip(id="dense-lower-bound", target="range-slider-dense", trigger="hover focus", placement="left"),
                                    dbc.Tooltip(id="dense-higher-bound", target="range-slider-dense", trigger="hover focus", placement="right"),
                                ], width=11),
                            ]),
                        ]
                    )),
                    id="sc-tools-collapse",
                    is_open=False), style={'margin-top': '1em'}
            )
        ]
    ), style={'background-color': 'rgba(248, 249, 250, 1)', 'width': 'min-content',
              'align-content': 'center', 'margin-top': '1.5rem'}),

]

# ----------------
# landing-cell for mc0
mc0_landing = html.Div([
    html.Div([html.H1([indent.join('Welcome')], className='greetings'),
              html.H1([indent.join('To')], className='greetings'),
              html.H1([indent.join('MALA')], className='greetings'),
              html.Div('Upload a file containing atomic positions for MALA to process', className='greetings', ),
              html.Div('Then choose a style for plotting', className='greetings', )]),

], style={'width': 'content-min', 'margin-top': '20vh'})

skel_layout = [dbc.Row([
    dbc.Col(
        [
            side_l,
            dbc.Button(">", id="open-offcanvas-l", n_clicks=0,
                       style={'margin-top': '40vh', 'position': 'absolute', 'left': '0'}),
            bot_button, bot
            # it doesn't matter where offcanvasses are placed here - only their "placement"-prop matters
        ],
        id="l0", width='auto'),

    dbc.Col(mc0_landing, id="mc0", width='auto'),

    dbc.Col(
        [
            side_r,
            dbc.Button("<", id="open-settings", n_clicks=0,
                       style={'visibility': 'hidden', 'margin-top': '40vh', 'position': 'absolute', 'right': '0'}),
        ],
        id="r0", width='auto')

], justify='center')]

# All the previously defined Components are not yet rendered in our app. They have to be inside app.layout
# app.layouts content gets updated, which makes our app reactive

p_layout_landing = dbc.Container([
    dcc.Store(id="page_state", data="landing"),     # determines what is rendered as main content (among other things?)
    dcc.Store(id="UP_STORE"),       # Info on uploaded file (path, ...)
    dcc.Store(id="BOUNDARIES_STORE"),
    #dcc.Store(id="choice_store", data="scatter"),       # unused right now (for multiple vis-options)
    dcc.Store(id="sc_settings"),        # parameters of the righthand sidebar, used to update plot
    html.Div(skel_layout, id="content-layout")
], fluid=True, style={'height': '100vh', 'width': '100vw', 'background-color': '#023B59'})
app.layout = p_layout_landing


# The Div in p_layout_plotting will be redefined on page_state-change


# CALLBACKS & FUNCTIONS

    # Reworked Functions making use of duplicate Outputs
    # TODO: update upload-section (Text, Umrandung, Text im upload)
@app.callback(
    Output("page_state", "data", allow_duplicate=True),
    Output("df_store", "data", allow_duplicate=True),
    Output("offcanvas-r-sc", "is_open", allow_duplicate=True),
    Output("offcanvas-bot", "is_open", allow_duplicate=True),
    Output("UP_STORE", "data", allow_duplicate=True),
    Input("reset-data", "n_clicks"),
    prevent_initial_call = True
)
def click_reset(click):
    return "landing", None, False, False, None



    # End of reworked functions



# sidebar_l collapses
@app.callback(
    Output("collapse-upload", "is_open"),
    Input("open-upload", "n_clicks"),
    Input("collapse-upload", "is_open"),
    prevent_initial_call=True,
)
def toggle_upload_section(n_header, is_open):
    if n_header:
        return not is_open


# end of sidebar_l collapses


# Modal collapsable
# sidebar_l collapses
@app.callback(
    Output("collapse-atom-list", "is_open"),
    Output("open-atom-list-arrow", "children"),
    Input("open-atom-list", "n_clicks"),
    Input("collapse-atom-list", "is_open"),
    prevent_initial_call=True,
)
def toggle_uploaded_atoms(n_header, is_open):
    txt = "⌃"
    if n_header:
        if is_open:
            txt = "⌄"
        return not is_open, txt


# BOTTOM bar callbacks

@app.callback(
    Output("open-bot-canv", "is_open"),
    Input("page_state", "data"),
    State("offcanvas-bot", "is_open"),
    prevent_initial_call=True,
)
def toggle_bot_button(page_state, canv_open):
    if page_state == "plotting":
        if not canv_open:
            return True
        else:
            return False

    else:
        return False


# show button if we're plotting and if bot-canvas is closed

@app.callback(
    Output("offcanvas-bot", "is_open"),
    Input("open-bot", "n_clicks"),
    Input("page_state", "data"),
    prevent_initial_call=True,
)
def toggle_bot_canv(open_cl, page_state):
    if page_state == "plotting":
        if dash.callback_context.triggered_id[0:4] == "open":
            return True
        else:
            return False
    else:
        return False


# END BOTTOM BAR CALLBACKS


# CALLBACKS FOR SCATTERPLOT

# collapsable cross-section and density tools
@app.callback(
    Output("sc-tools-collapse", "is_open"),
    Input("open-sc-tools", "n_clicks"),
    State("sc-tools-collapse", "is_open"),
    prevent_initial_call=True)
def toggle_sc_tools(n_sc_s, is_open):
    if n_sc_s:
        return not is_open


# toggle rangesliders
@app.callback(
    Output("range-slider-cs-x", "disabled"),
    Output("sc-active-x", "active"),
    Input("sc-active-x", "n_clicks"),
    Input("range-slider-cs-x", "disabled"),
    State("sc-active-x", "active"),
    prevent_initial_call=True)
def toggle_x_cs(n_x, active, bc):
    if n_x:
        return not active, not bc


@app.callback(
    Output("range-slider-cs-y", "disabled"),
    Output("sc-active-y", "active"),
    Input("sc-active-y", "n_clicks"),
    Input("range-slider-cs-y", "disabled"),
    State("sc-active-y", "active"),
    prevent_initial_call=True)
def toggle_y_cs(n_x, active, bc):
    if n_x:
        return not active, not bc


@app.callback(
    Output("range-slider-cs-z", "disabled"),
    Output("sc-active-z", "active"),
    Input("sc-active-z", "n_clicks"),
    Input("range-slider-cs-z", "disabled"),
    State("sc-active-z", "active"),
    prevent_initial_call=True)
def toggle_z_cs(n_x, active, bc):
    if n_x:
        return not active, not bc


@app.callback(
    Output("range-slider-dense", "disabled"),
    Output("active-dense", "active"),
    Output("active-dense", "disabled"),
    Input("active-dense", "n_clicks"),
    State("range-slider-dense", "disabled"),
    State("active-dense", "active"),
    prevent_initial_call=True)
def toggle_density_sc(n_d, active, bc):

    if dash.callback_context.triggered_id == "active-dense":
        return not active, not bc, False
    else:
        return True, False, True
    # active actually is the disabled parameter!


@app.callback(
    Output("range-slider-cs-x", "value"),
    Output("range-slider-cs-y", "value"),
    Output("range-slider-cs-z", "value"),
    Output("range-slider-dense", "value"),
    Input("reset-cs-x", "n_clicks"),
    Input("reset-cs-y", "n_clicks"),
    Input("reset-cs-z", "n_clicks"),
    Input("reset-dense", "n_clicks"),
    State("df_store", "data"),
    prevent_initial_call=True)
def reset_sliders(n_clicks_x, n_clicks_y, n_clicks_z, n_clicks_dense, data):
    df = pd.DataFrame(data['MALA_DF']['scatter'])
    if dash.callback_context.triggered_id == 'reset-cs-x':
        return [0, len(np.unique(df['x']))-1], dash.no_update, dash.no_update, dash.no_update
    elif dash.callback_context.triggered_id == 'reset-cs-y':
        return dash.no_update, [0, len(np.unique(df['y']))-1], dash.no_update, dash.no_update
    elif dash.callback_context.triggered_id == 'reset-cs-z':
        return dash.no_update, dash.no_update, [0, len(np.unique(df['z']))-1], dash.no_update
    elif dash.callback_context.triggered_id == 'reset-dense':
        return dash.no_update, dash.no_update, dash.no_update, [0, len(np.unique(df['val']))-1]
    else:
        print("STATUS: something unknown triggered slider reset")
        raise PreventUpdate


# end of collapsable cross-section settings


# Storing camera position
@app.callback(
    Output("cam_store", "data"),
    [Input("default-cam", "n_clicks"),
     Input("x-y-cam", "n_clicks"),
     Input("x-z-cam", "n_clicks"),
     Input("y-z-cam", "n_clicks"),
     Input("scatter-plot", "relayoutData")],
    prevent_initial_call=True)
def store_cam(default_clicks, x_y_clicks, x_z_clicks, y_z_clicks, user_in):
    # user_in is the camera position set by mouse movement, it has to be updated on every mouse input on the fig

    # set stored_cam_setting according to which button was last pressed
    if dash.callback_context.triggered_id[0:-4] == "default":
        return dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=1.5, y=1.5, z=1.5)
        )
    elif dash.callback_context.triggered_id[0:-4] == "x-y":
        return dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=0, y=0, z=3.00)
        )
    elif dash.callback_context.triggered_id[0:-4] == "x-z":
        return dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=0, y=3.00, z=0)
        )
    elif dash.callback_context.triggered_id[0:-4] == "y-z":
        return dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=3.00, y=0, z=0))
    # set to plot cam when user input is camera-movement:
    elif dash.callback_context.triggered_id == "scatter-plot":

        # stops the update in case the callback is triggered by zooming/initializing/smth else
        if user_in is None or "scene.camera" not in user_in.keys():
            raise PreventUpdate
        else:
            if 'scene.camera' in user_in.keys():
                return user_in['scene.camera']
        # stops the update in case the callback is triggered by zooming/smth else
    else:
        print("unknown trigger caused cam_pos_update")
        raise PreventUpdate

    # Feels very unelegant -> this is always run twice when switching to scatter for example
    # END OF SCATTER CALLBACKS


# UPDATE STORED DATA

# page state
# TODO this should be optimized to not transfer the all the data everytime
@app.callback(
    Output("page_state", "data"),
    [Input("df_store", "data"),
     State("page_state", "data")],
    prevent_initial_call=True)
def updatePageState(trig1, state):
    new_state = "landing"
    if dash.callback_context.triggered_id == "df_store":
        if trig1 is not None :
            new_state = "plotting"

    # prevent unnecessary updates
    if state == new_state:
        raise PreventUpdate
    else:
        return new_state




# DASH-UPLOADER
# after file-upload, return upload-status (if successful) and dict with file-path and upload-id (for future verif?)
def upload_exception():
    print("excepted file error")
    return None, "File not supported", dash.no_update, dash.no_update, "upload-failure"
    # = FILE NOT SUPPORTED AS ASE INPUT (some formats listed in supported-files for ase are output only. This will only be filtered here)



@du.callback(
    output=[Output("output-upload-state", "children"), Output("UP_STORE", "data"), Output("atom-limit-warning", "is_open"), Output("atoms_list", "children"), Output("atoms-preview", "figure"), Output("upload-data", "className"), Output("BOUNDARIES_STORE", "data")],
    id="upload-data"
)
def upload_callback(status):  # <------- NEW: du.UploadStatus
    """
    Input
    :param status: All the info necessary to access (latest) uploaded files

    Output
    upload-state: Upload-state below upload-area
    UP_STORE: dcc.Store-component, storing uploader-ID and path of uploaded file
    atom-limit-warning: Boolean for displaying long-computation-time-warning
    atoms_list: Table containing all atoms read by ASE
    atoms-preview: Figure previewing ASE-read Atoms
    upload-data: Changing border-color of this component according to upload-status
    """
    UP_STORE = {"ID": status.upload_id, "PATH": str(status.latest_file.resolve())}
    LIMIT_EXCEEDED = False
    fig = px.scatter_3d()
    fig.update_layout(templ2['layout'])
    boundaries = []
    # ASE.reading to check for file-format support, to fill atoms_table, and to fill atoms-preview
    try:
        print("Trying upload")
        r_atoms = ase.io.read(status.latest_file)
        UPDATE_TEXT = "Upload successful"
        if r_atoms.get_global_number_of_atoms() > ATOM_LIMIT:
            LIMIT_EXCEEDED = True
        table_rows = [
            html.Tr([html.Td(atom.index), html.Td(atom.x), html.Td(atom.y), html.Td(atom.z)])       #, html.Td("checkbox")
            for atom in r_atoms]



        atoms_fig = go.Scatter3d(name="Atoms", x=[atom.x for atom in r_atoms], y=[atom.y for atom in r_atoms],
                           z=[atom.z for atom in r_atoms], mode='markers', hovertemplate='X: %{x}</br></br>Y: %{y}</br>Z: %{z}<extra></extra>')




        # Draw the outline of 4 planes and add them as individual traces
        # (2 / 6 Planes will be obvious by the 4 surrounding them)
        X_axis = r_atoms.cell[0]
        Y_axis = r_atoms.cell[1]
        Z_axis = r_atoms.cell[2]

            # Plane 1: X-Z-1
        x_points = [0, X_axis[0], X_axis[0]+Z_axis[0], Z_axis[0], 0]
        y_points = [0, X_axis[1], X_axis[1]+Z_axis[1], Z_axis[1], 0]
        z_points = [0, X_axis[2], X_axis[2]+Z_axis[2], Z_axis[2], 0]
        fig.add_trace(go.Scatter3d(x=x_points, y=y_points, z=z_points, hoverinfo='skip', mode='lines', marker={'color': 'black'}, name="Cell"))
        boundarie1 = go.Scatter3d(name="cell", x=x_points, y=y_points, z=z_points, hoverinfo='skip', mode='lines', marker={'color': 'black'})
            # Plane 2: X-Z-2
        x_points = [0+Y_axis[0], X_axis[0]+Y_axis[0], X_axis[0]+Z_axis[0]+Y_axis[0], Z_axis[0]+Y_axis[0], 0+Y_axis[0]]
        y_points = [0+Y_axis[1], X_axis[1]+Y_axis[1], X_axis[1]+Z_axis[1]+Y_axis[1], Z_axis[1]+Y_axis[1], 0+Y_axis[1]]
        z_points = [0, X_axis[2], X_axis[2]+Z_axis[2], Z_axis[2], 0]
        fig.add_trace(go.Scatter3d(x=x_points, y=y_points, z=z_points, hoverinfo='skip', mode='lines', marker={'color': 'black'}, showlegend=False))
        boundarie2 = go.Scatter3d(name="cell", x=x_points, y=y_points, z=z_points, hoverinfo='skip', mode='lines', marker={'color': 'black'}, showlegend=False)

            # Plane 3: X-Y-1
        x_points = [0, X_axis[0], X_axis[0]+Y_axis[0], Y_axis[0], 0]
        y_points = [0, X_axis[1], X_axis[1]+Y_axis[1], Y_axis[1], 0]
        z_points = [0, X_axis[2], X_axis[2]+Y_axis[2], Y_axis[2], 0]
        fig.add_trace(go.Scatter3d(x=x_points, y=y_points, z=z_points, hoverinfo='skip', mode='lines', marker={'color': 'black'}, showlegend=False))
        boundarie3 = go.Scatter3d(name="cell", x=x_points, y=y_points, z=z_points, hoverinfo='skip', mode='lines', marker={'color': 'black'}, showlegend=False)
            # Plane 4: X-Y-2
        x_points = [0, X_axis[0], X_axis[0]+Y_axis[0], Y_axis[0], 0]
        y_points = [0, X_axis[1], X_axis[1]+Y_axis[1], Y_axis[1], 0]
        z_points = [0+Z_axis[2], X_axis[2]+Z_axis[2], X_axis[2]+Y_axis[2]+Z_axis[2], Y_axis[2]+Z_axis[2], 0+Z_axis[2]]
        fig.add_trace(go.Scatter3d(x=x_points, y=y_points, z=z_points, hoverinfo='skip', mode='lines', marker={'color': 'black'}, showlegend=False))
        boundarie4 = go.Scatter3d(name="cell", x=x_points, y=y_points, z=z_points, hoverinfo='skip', mode='lines', marker={'color': 'black'}, showlegend=False)

        boundaries = [boundarie1, boundarie2, boundarie3, boundarie4]
        fig.update_scenes(removeHoverLines)
        fig.add_trace(atoms_fig)



        border_style = "upload-success"

    # ValueError or File not sup. - exception for not supported formats (not yet filtered by upload-component)
    except ValueError:
        r_atoms, UPDATE_TEXT, UP_STORE, table_rows, border_style = upload_exception()
    except ase.io.formats.UnknownFileTypeError:
        r_atoms, UPDATE_TEXT, UP_STORE, table_rows, border_style = upload_exception()

    return UPDATE_TEXT, UP_STORE, LIMIT_EXCEEDED, table_rows, go.Figure(fig), border_style, boundaries
# END DASH UPLOADER



# CALLBACK TO ACTIVATE RUN-MALA-button
@app.callback(
    Output("run-mala", "disabled", allow_duplicate=True),
    Input("model-choice", "value"),
    Input("model-temp", "value"),
    prevent_initial_call=True
)
def activate_runMALA_button(model, temp):
    if model is not None and temp is not None:
        return False
    else:
        return True


# END OF CB


# CALLBACK TO OPEN UPLOAD-MODAL
# TODO: Add df_store as input? To fix bug: modal not closing when rerunning mala, while page state is already plotting
@app.callback(
    Output("upload-modal", "is_open"),
    [
        Input("UP_STORE", "data"),
        Input("edit-input", "n_clicks"),
        Input("page_state", "data"),
    ], prevent_initial_call=True
)
def open_UP_MODAL(upload, edit_input, page_state):
    if dash.callback_context.triggered_id == "page_state" and page_state == "plotting":
        return False
    elif (dash.callback_context.triggered_id == "UP_STORE" or dash.callback_context.triggered_id == "edit-input") and upload is not None:
        return True
    else:
        return False
# END OF CB


@app.callback(
    Output("model-temp", "value"),
    Output("model-temp", "disabled"),
    Output("model-temp", "min"),
    Output("model-temp", "max"),
    Input("model-choice", "value"),
    prevent_initial_call=True
)
def init_temp_choice(model_choice):
    if model_choice is None:
        raise PreventUpdate
    # splitting string input in substance and (possible) temperature(s)
    model, temp = model_choice.split("|")

    if "[" in temp:
        min_temp, max_temp = temp.split(",")
        min_temp = min_temp[1:]
        max_temp = max_temp[:-1]
        return min_temp, False, min_temp, max_temp

    else:
        return int(temp), True, None, None



#   UPDATE DF


# Trigger: button "run-mala", button "reset"
# (indirectly) Opens a popup, showing
#   - the uploaded Atoms with a checkmark;
#   - possibly giving a prerender of only the atoms;
#   - giving a warning if more than (ATOM_LIMIT) Atoms are selected
#   - has a "Start MALA" Button
# !!  THIS IS RUNNING MALA INFERENCE  !!
# AND "PARSING" DATA FOR CONTINUED USE

@app.callback(
    Output("df_store", "data"),
    Input("run-mala", "n_clicks"),
    State("model-choice", "value"),
    State("model-temp", "value"),
    State('UP_STORE', 'data'),
    prevent_initial_call=True)
def updateDF(trig, model_choice, temp_choice, upload):
    """
    Input
    :param trig: =INPUT - Pressing button "run-mala" triggers callback
    :param reset: =INPUT - trigger for reset of stored data
    :param model_choice: =STATE - info on the cell-system (substance+temp(-range)), separated by |
    :param temp_choice: =STATE - chosen temperature - either defined by model-choice, or direct input inbetween range
    :param upload: =STATE - dict(upload ID, filepath)

    :return: returns a dictionary with the data necessary to render to store-component

    Output
    df_store[data]... variable where we store the info necessary to render, so that we can use it in other callbacks

    NOW:
    read file from filepath via ASE -> returns ATOM-obj
    on MALA-call, give ATOMS-objs & model_choice
    -> returns density data and energy values +  a .cube-file
    """

    if upload is None:
        raise PreventUpdate

    print("UpdateDF started")
    model_and_temp = {'name': model_choice, 'temperature': float(temp_choice)}
    upID = upload["ID"]
    filepath = upload["PATH"]

    # ASE.reading to receive ATOMS-objs, to pass to MALA-inference

        # no ValueError Exception needed, bc this is done directly on upload
    read_atoms = ase.io.read(filepath)



    # (a) GET DATA FROM MALA (/ inference script)

    print("Running MALA-Inference. Passing: ", read_atoms, " and model-choice: ", model_and_temp)
    mala_data = run_mala_prediction(read_atoms, model_and_temp)
    # contains 'band_energy', 'total_energy', 'density', 'density_of_states', 'energy_grid'
    # mala_data is stored in df_store dict under key 'MALA_DATA'. (See declaration of df_store below for more info)
    density = mala_data['density']

    coord_arr = np.column_stack(
        list(map(np.ravel, np.meshgrid(*map(np.arange, density.shape), indexing="ij"))) + [density.ravel()])
    data0 = pd.DataFrame(coord_arr, columns=['x', 'y', 'z', 'val'])  # untransformed Dataset

    atoms = [[], [], [], [], []]

    x_axis = [mala_data["grid_dimensions"][0], mala_data["voxel"][0][0],
              mala_data["voxel"][0][1], mala_data["voxel"][0][2]]
    y_axis = [mala_data["grid_dimensions"][1], mala_data["voxel"][1][0],
              mala_data["voxel"][1][1], mala_data["voxel"][1][2]]
    z_axis = [mala_data["grid_dimensions"][2], mala_data["voxel"][2][0],
              mala_data["voxel"][2][1], mala_data["voxel"][2][2]]

    # READING ATOMPOSITIONS
    for i in range(0, len(read_atoms)):
        atoms[0].append(read_atoms[i].symbol)
        atoms[1].append(read_atoms[i].charge)
        atoms[2].append(read_atoms.get_positions()[i,0])
        atoms[3].append(read_atoms.get_positions()[i,1])
        atoms[4].append(read_atoms.get_positions()[i,2])
    atoms_data = pd.DataFrame(
        data={'x': atoms[2], 'y': atoms[3], 'z': atoms[4], 'ordinal': atoms[0], 'charge': atoms[1]})

    # SCALING AND SHEARING SCATTER DF
    # (b) SCALING to right voxel-size
    # need to bring atompositions and density-voxels to the same scaling
    data0['x'] *= x_axis[1]
    data0['y'] *= y_axis[2]
    data0['z'] *= z_axis[3]
    data_sc = data0.copy()

    # SHEARING für scatter_3d - linearcombination
    data_sc.x += y_axis[1] * (data0.y / y_axis[2])
    data_sc.x += z_axis[1] * (data0.z / z_axis[3])

    data_sc.y += x_axis[2] * (data0.x / x_axis[1])
    data_sc.y += z_axis[2] * (data0.z / z_axis[3])

    data_sc.z += y_axis[3] * (data0.y / y_axis[2])
    data_sc.z += x_axis[3] * (data0.x / x_axis[1])

    '''
           Importing Data 
               Parameters imported from:
               (a) inference script:
                   - bandEn
                   - totalEn
                   - density
                   - density of states - dOs
                   - energy Grid - enGrid

               (b) .cube file created by running inference script
                   =   axis-data -> x_, y_ and z_axis
                   - voxel"resolution"
                       - f.e. x_axis[0]
                   - unit-vector
                       - f.e. ( x_axis[1] / x_axis[2] / x_axis[3] ) is x-axis unit-vector
               TODO: find a GOOD way to transform our data from kartesian grid to the according (in example data sheared) one
                   - so far only doing that with a linear combination for dataframe in scatter_3d format
                   - need to to this for volume too
                   --> good way would be a matrix multiplication of some sort
    '''

    # _______________________________________________________________________________________

    df_store = {'MALA_DF': {'default': data0.to_dict("records"), 'scatter': data_sc.to_dict("records")},
                'MALA_DATA': mala_data,
                'INPUT_DF': atoms_data.to_dict("records"),
                'SCALE': {'x_axis': x_axis, 'y_axis': y_axis, 'z_axis': z_axis}}

    print("DATA PROCESSING COMPLETE")
    print("_________________________________________________________________________________________")
    return df_store


# SC SETTINGS STORING
@app.callback(
    Output("sc_settings", "data"),
    Output("sc-outline", "value"),
    Input('sc-size', 'value'),
    Input("sc-outline", "value"),
    Input("sc-atoms", "value"),
    Input("sc-opac", "value"),
    State("sc_settings", "data"),
    Input("cell-boundaries", "value")
)
def update_settings_store(size, outline, atoms, opac, saved, cell):
    if saved is None:
        # default settings
        settings = {
            "size": 12,     # particle size
            "opac": 1,      # particle opacity
            "outline": dict(width=1, color='DarkSlateGrey'),    # particle outline
            "atoms": True,
            "cell": 5     # cell boundaries (color)
        }

    else:
        settings = saved
    if dash.callback_context.triggered_id == "sc-size":
        settings["size"] = size
    elif dash.callback_context.triggered_id == "sc-opac":
        if opac is None:
            raise PreventUpdate
        settings["opac"] = opac
        if opac < 1:
            outline = False
            settings["outline"] = dict(width=0, color='DarkSlateGrey')
    elif dash.callback_context.triggered_id == "sc-outline":
        # Define outline settings
        print("Outline: ", outline)
        if outline:
            settings["outline"] = dict(width=1, color='DarkSlateGrey')
        else:
            settings["outline"] = dict(width=0, color='DarkSlateGrey')
        print("Saved outline setting: ", settings['outline'])
    elif dash.callback_context.triggered_id == "sc-atoms":
        settings["atoms"] = atoms
    elif dash.callback_context.triggered_id == "cell-boundaries":
        if cell:
            settings["cell"] = 5
        else:
            settings["cell"] = 0.01
            # for disabling cell-boundaries, we just show them in white for now - should reduce lines thickness
    return settings, outline


# END UPDATE FOR STORED DATA


# TODO: update Tool-Sliders - DENSITY BUG!!
@app.callback(
    [

        Output("range-slider-cs-x", "min"),
        Output("range-slider-cs-x", "max"),
        Output("range-slider-cs-x", "step"),

        Output("range-slider-cs-y", "min"),
        Output("range-slider-cs-y", "max"),
        Output("range-slider-cs-y", "step"),

        Output("range-slider-cs-z", "min"),
        Output("range-slider-cs-z", "max"),
        Output("range-slider-cs-z", "step"),

        Output("range-slider-dense", "min"),
        Output("range-slider-dense", "max"),
        Output("range-slider-dense", "step"),
    ],
    [
        Input("df_store", "data"),
    ],
)
def update_tools(data):
    print("STATUS: Tool-Update")
    if data is None:  # in case of reset:
        raise PreventUpdate
    else:
        df = pd.DataFrame(data['MALA_DF']['scatter'])

        return 0, len(np.unique(df['x']))-1, 1, \
               0, len(np.unique(df['y']))-1, 1, \
               0, len(np.unique(df['z']))-1, 1, \
               0, len(np.unique(df['val']))-1, 1

# TODO: maybe use popover instead of tooltip
# Updating slider-range indicators X
@app.callback(
    Output("x-lower-bound", "children"),
    Output("x-higher-bound", "children"),
    Output("x-lower-bound", "trigger"),     # unused - doesn't seem to be editable on CB
    Input("range-slider-cs-x", "value"),
    Input("range-slider-cs-x", "disabled"),
    State("df_store", "data")
    ,State("x-lower-bound", "trigger")      # unused - needed for see above
)
def update_slider_bound_indicators_X(value, disabled, data, trigger):
    if data is None:  # in case of reset:
        raise PreventUpdate

    # TODO: enabling/disabling hovermode of indicator doesn't work - doesn't seem to overwrite init-param
    if disabled:
        trigger = None
    else:
        trigger = "hover"

    dfX = pd.DataFrame(data['MALA_DF']['scatter'])['x']

    if value is None:
        lower = round(min(dfX), ndigits=5)
        higher = round(max(dfX), ndigits=5)
    else:
        lowB, highB = value
        lower = round(np.unique(dfX)[lowB], ndigits=5)
        higher = round(np.unique(dfX)[highB], ndigits=5)
    return lower, higher, trigger


# Updating slider-range indicators Y
@app.callback(
    Output("y-lower-bound", "children"),
    Output("y-higher-bound", "children"),
    Output("y-lower-bound", "trigger"),
    Input("range-slider-cs-y", "value"),
    Input("range-slider-cs-y", "disabled"),
    State("df_store", "data")
    ,State("y-lower-bound", "trigger")
)
def update_slider_bound_indicators_Y(value, disabled, data, trigger):
    if data is None:  # in case of reset:
        raise PreventUpdate

    # TODO: enabling/disabling hovermode of indicator doesn't work - doesn't seem to overwrite init-param
    if disabled:
        trigger = None
    else:
        trigger = "hover"

    dfY = pd.DataFrame(data['MALA_DF']['scatter'])['y']

    if value is None:
        lower = round(min(dfY), ndigits=5)
        higher = round(max(dfY), ndigits=5)
    else:
        lowB, highB = value
        lower = round(np.unique(dfY)[lowB], ndigits=5)
        higher = round(np.unique(dfY)[highB], ndigits=5)
    return lower, higher, trigger


# Updating slider-range indicators Z
@app.callback(
    Output("z-lower-bound", "children"),
    Output("z-higher-bound", "children"),
    Output("z-lower-bound", "trigger"),
    Input("range-slider-cs-z", "value"),
    Input("range-slider-cs-z", "disabled"),
    State("df_store", "data")
    ,State("z-lower-bound", "trigger")
)
def update_slider_bound_indicators_Z(value, disabled, data, trigger):
    if data is None:  # in case of reset:
        raise PreventUpdate

    # TODO: enabling/disabling hovermode of indicator doesn't work - doesn't seem to overwrite init-param
    if disabled:
        trigger = None
    else:
        trigger = "hover"

    dfZ = pd.DataFrame(data['MALA_DF']['scatter'])['z']

    if value is None:
        lower = round(min(dfZ), ndigits=5)
        higher = round(max(dfZ), ndigits=5)
    else:
        lowB, highB = value
        lower = round(np.unique(dfZ)[lowB], ndigits=5)
        higher = round(np.unique(dfZ)[highB], ndigits=5)
    return lower, higher, trigger


# Updating slider-range indicators density
@app.callback(
    Output("dense-lower-bound", "children"),
    Output("dense-higher-bound", "children"),
    Output("dense-lower-bound", "trigger"),
    Input("range-slider-dense", "value"),
    Input("range-slider-dense", "disabled"),
    State("df_store", "data")
    ,State("dense-lower-bound", "trigger")
)
def update_slider_bound_indicators_density(value, disabled, data, trigger):
    if data is None:  # in case of reset:
        raise PreventUpdate

    # TODO: enabling/disabling hovermode of indicator doesn't work - doesn't seem to overwrite init-param
    if disabled:
        trigger = None
    else:
        trigger = "hover"

    dfDense = pd.DataFrame(data['MALA_DF']['scatter'])['val']

    if value is None:
        lower = round(min(dfDense), ndigits=5)
        higher = round(max(dfDense), ndigits=5)
    else:
        lowB, highB = value
        lower = round(np.unique(dfDense)[lowB], ndigits=5)
        higher = round(np.unique(dfDense)[highB], ndigits=5)
    return lower, higher, trigger



# LAYOUT CALLBACKS
# UPDATING CONTENT-CELL 0

@app.callback(
    Output("mc0", "children"),
    Input("page_state", "data"),
    State("df_store", "data"),
    prevent_initial_call=True)
def updateMC0(state, data):
    if data is None or state == "landing":
        return mc0_landing

    elif state == "plotting":
        return main_plot


'''
# cam-position buttons have to stay as parameters, so they trigger an update. 
cam_store can't be an input or else it triggers an update everytime the cam is moved
'''

@app.callback(
    Output("scatter-plot", "figure", allow_duplicate=True),
    [

        # Settings
        Input("sc_settings", "data"),
        Input("default-cam", "n_clicks"),
        Input("x-y-cam", "n_clicks"),
        Input("x-z-cam", "n_clicks"),
        Input("y-z-cam", "n_clicks"),

        State("cam_store", "data"),
        Input("df_store", "data"),
        State("scatter-plot", "figure"),
        State("BOUNDARIES_STORE", "data")
    ],
    prevent_initial_call = 'initial_duplicate',
)
def updatePlot(
               settings, cam_default, cam_xy, cam_xz, cam_yz, stored_cam_settings, f_data, fig, boundaries_fig):
    # TODO: make this function more efficient
    patched_fig = Patch()

    # DATA
    # the density-Dataframe that we're updating, taken from df_store (=f_data)
    if f_data is None:
        raise PreventUpdate

    print("Plot update")
    df = pd.DataFrame(f_data['MALA_DF']['scatter'])
        # sheared coordinates

    # atoms-Dataframe also taken from f_data
    atoms = pd.DataFrame(f_data['INPUT_DF'])
    no_of_atoms = len(atoms)

    # Dataframes are ready now
    fig_bound=boundaries_fig

    new_cam = stored_cam_settings



    # INIT PLOT
    if dash.callback_context.triggered[0]['prop_id'] == ".":
            # Our main figure = scatter plot
        patched_fig = px.scatter_3d(
            df, x="x", y="y", z="z",
            color="val",
            hover_data=['val'],
            color_continuous_scale=px.colors.sequential.Inferno_r,
            range_color=[min(df['val']), max(df['val'])],
        )
        patched_fig.update_layout(margin=dict(l=0, r=0, b=0, t=0), paper_bgcolor="#f8f9fa", showlegend=False,
                          modebar_remove=["zoom", "resetcameradefault", "resetcameralastsave"], template=templ1)

        patched_fig.update_coloraxes(colorbar={'thickness': 10, 'title': '', 'len': 0.9})
        patched_fig.update_traces(patch={'marker':{'size': settings['size'], 'line': settings['outline']}})

        # adding helper-figure to keep camera-zoom the same, regardless of data(-slicing)-changes
        # equals the cell boundaries, but has slight offset to the main plot (due to not voxels, but ertices being scatter plotted)
        for i in fig_bound:
           patched_fig.add_trace(i)
        patched_fig.update_traces(patch={'line': {'width': settings['cell']}}, selector=dict(name="cell"))
        patched_fig.update_scenes(removeHoverLines)

        atom_colors = []
        for i in range(0, int(no_of_atoms)):
            atom_colors.append("green")
        patched_fig.add_trace(go.Scatter3d(name="Atoms", x=atoms['x'], y=atoms['y'], z=atoms['z'], mode='markers',
                                 marker=dict(size=15, color=atom_colors, line=dict(width=1, color='DarkSlateGrey'))))



    # SETTINGS
    elif dash.callback_context.triggered_id == "sc_settings":

        patched_fig['data'][0]['marker']['line'] = settings["outline"]
        patched_fig['data'][0]['marker']['size'] = settings["size"]
        patched_fig['data'][0]['marker']['opacity'] = settings["opac"]
        for i in [1,2,3,4]:
            patched_fig['data'][i]['line']['width'] = settings["cell"]
        patched_fig['data'][5]['visible'] = settings["atoms"]

    # CAMERA

    elif "cam" in dash.callback_context.triggered_id:
        print(dash.callback_context.triggered_id)
        if dash.callback_context.triggered_id == "default-cam":
            new_cam = dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        elif dash.callback_context.triggered_id == "x-y-cam":
            new_cam = dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=0, y=0, z=3.00)
            )
        elif dash.callback_context.triggered_id == "x-z-cam":
            new_cam = dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=0, y=3.00, z=0)
            )
        elif dash.callback_context.triggered_id == "y-z-cam":
            new_cam = dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=3.00, y=0, z=0))
    patched_fig['layout']['scene']['camera']= new_cam

    '''
    INIT PLOT
        Create a Figure that overwrites the default figure (a single blue dot)
        This is only run on the initial call of this callback (id ".")
        All following operations are optional and only triggered if their parameters change (they are trigger of this CB)
        They do not overwrite the figure, but patch their respective parameters of the initialised figure
        -> better performance
    
    SETTINGS
        Set:
            outline (width), 
            size (in px), opacity (0.1 - 1), 
            visibility of cell boundaries (width 1 / 0) and 
            visibility of atoms
    
    CAMERA
        set camera-position according to the clicked button, 
                                    OR 
                    - if no button has been clicked - 
        to the most recently stored manually adjusted camera position
    '''


    return patched_fig


''' maybe interesting: animations on plot change:

https://plotly.com/python-api-reference/generated/plotly.graph_objects.Figure.html
"transition
Sets transition options used during Plotly.react updates."

'''

# TODO optimize by using relayout to update camera instead of cam_store (or smth else entirely)
@app.callback(
    Output("scatter-plot", "figure"),
           # Tools
    Input("range-slider-dense", "value"),
    Input("active-dense", "active"),
    Input("range-slider-cs-x", "value"),
    Input("sc-active-x", "active"),
    Input("range-slider-cs-y", "value"),
    Input("sc-active-y", "active"),
    Input("range-slider-cs-z", "value"),
    Input("sc-active-z", "active"),
            # Data
    State("df_store", "data"),
    State("cam_store", "data"),
    prevent_initial_call=True,
           )
def slicePlot(slider_range, dense_inactive, slider_range_cs_x, cs_x_inactive, slider_range_cs_y, cs_y_inactive,
               slider_range_cs_z, cs_z_inactive, f_data, cam):
    if f_data is None:
        raise PreventUpdate

    df = pd.DataFrame(f_data['MALA_DF']['scatter'])
    dfu = df.copy()     # this is a subset of df after one if-case is run. For every if-case, we need the subset+the original

    # TOOLS
    # filter-by-density
    if slider_range is not None and dense_inactive:  # Any slider Input there? Do:
        low, high = slider_range
        mask = (dfu['val'] >= np.unique(df['val'])[low]) & (dfu['val'] <= np.unique(df['val'])[high])
        dfu = dfu[mask]

    # slice X
    if slider_range_cs_x is not None and cs_x_inactive:  # Any slider Input there? Do:
        low, high = slider_range_cs_x
        mask = (dfu['x'] >= np.unique(df['x'])[low]) & (dfu['x'] <= np.unique(df['x'])[high])
        dfu = dfu[mask]

    # slice Y
    if slider_range_cs_y is not None and cs_y_inactive:  # Any slider Input there? Do:
        low, high = slider_range_cs_y
        mask = (dfu['y'] >= np.unique(df['y'])[low]) & (dfu['y'] <= np.unique(df['y'])[high])
        dfu = dfu[mask]

    # slice Z
    if slider_range_cs_z is not None and cs_z_inactive:  # Any slider Input there? Do:
        low, high = slider_range_cs_z
        mask = (dfu['z'] >= np.unique(df['z'])[low]) & (dfu['z'] <= np.unique(df['z'])[high])
        dfu = dfu[mask]

    patched_fig = Patch()
    patched_fig['data'][0]['x'] = dfu['x']
    patched_fig['data'][0]['y'] = dfu['y']
    patched_fig['data'][0]['z'] = dfu['z']
    patched_fig['data'][0]['marker']['color'] = dfu['val']
    # sadly the patch overwrites our cam positioning, which is why we have to re-patch it everytime
    patched_fig['layout']['scene']['camera'] = cam

    return patched_fig


# TODO this can be optimized (link womewhere)
@app.callback(
    Output("orientation", "figure"),
    Input("cam_store", "data"),
    prevent_initial_call=True
)
def updateOrientation(saved_cam):
    fig_upd = orient_fig
    fig_upd.update_layout(scene_camera={'up': {'x': 0, 'y': 0, 'z': 1}, 'center': {'x': 0, 'y': 0, 'z': 0},
                                        'eye': saved_cam['eye']}, clickmode="none", dragmode=False)
    return fig_upd

# TODO this can be optimized by patching
@app.callback(
    Output("dos-plot", "figure"),
    Output("bandEn", "children"),
    Output("totalEn", "children"),
    Output("fermiEn", "children"),
    [Input("df_store", "data"),
     Input("page_state", "data")],
    prevent_initial_call=True
)
def update_bot_canv(f_data, state):

    if state == "landing":
        raise PreventUpdate

    if f_data is not None:
        # PLOT data
        dOs = f_data['MALA_DATA']['density_of_states']
        df = pd.DataFrame(dOs)

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=df.index, y=df[0], name='densityOfstate',
                       line=dict(color='#f15e64', width=2, dash='dot')))
        fig.update_layout(margin=dict(l=0, r=0, b=0, t=0),
                          modebar_remove=["zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d", "zoomOut2d",
                                          "autoScale2d", "resetScale2d"], paper_bgcolor='#f8f9fa',
                          plot_bgcolor='#f8f9fa',
                          xaxis={'gridcolor': '#D3D3D3', 'dtick': 1, 'linecolor': 'black'},
                          yaxis={'gridcolor': '#D3D3D3', 'linecolor': 'black'}
                          )

        # TABLE data
        # take the first
        band_en = f_data['MALA_DATA']['band_energy']
        total_en = f_data['MALA_DATA']['total_energy']
        fermi_en = f_data['MALA_DATA']['fermi_energy']

    else:
        fig = px.scatter()

        band_en = '-'
        total_en = '-'
        fermi_en = '-'

    return fig, band_en, total_en, fermi_en


# END OF CALLBACKS FOR DOS PLOT


# CALLBACKS FOR SIDEBAR

# Update settings sidebar
@app.callback(
    Output("sz/isosurf-label", "children"),
    Output("opac-label", "style"),
    Output("sc-opac", "style"),
    Input("run-mala", "n_clicks"),
    prevent_initial_call=True
)
def updateSettings(run_mala):
    return "Size", {'visibility': 'visible'}, {'visibility': 'visible', 'width': '5em', 'margin-left': '0.25em'}


@app.callback(  # sidebar_r canvas (1/?)
    Output("offcanvas-r-sc", "is_open"),
    Input("page_state", "data"),
    Input("open-settings", "n_clicks"),
    [State("offcanvas-r-sc", "is_open")],
    prevent_initial_call=True
)
def toggle_settings_bar(page_state, n1, is_open):
    if dash.callback_context.triggered_id == "page_state" and page_state == "plotting":
        return True
    elif dash.callback_context.triggered_id[0:4] == "open":
        return not is_open
    else:
        return is_open


@app.callback(
    Output("open-settings", "style"),
    Input("page_state", "data"),
    prevent_initial_call=True
)
def toggle_settings_button(state):
    if state == "plotting":
        return {'visibility': 'visible', 'margin-top': '40vh', 'position': 'absolute', 'right': '0'}
    else:
        return {'visibility': 'hidden', 'margin-top': '40vh', 'position': 'absolute', 'right': '0'}


# toggle canvas
@app.callback(  # sidebar_l canvas
    Output("offcanvas-l", "is_open"),
    Input("open-offcanvas-l", "n_clicks"),
    [State("offcanvas-l", "is_open")],
    prevent_initial_call=True
)
def toggle_offcanvas_l(n1, is_open):
    if n1:
        return not is_open
    return is_open


# END OF CALLBACKS FOR SIDEBAR

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port="8050")
