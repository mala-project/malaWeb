# IMPORTS

import mala_inference
import ase.io
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table

import dash_bootstrap_components as dbc
# from dash_bootstrap_templates import load_figure_template
from dash.exceptions import PreventUpdate

# visualization
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go

# Theming scatter
templ1 = dict(layout=go.Layout(
    scene={
        'xaxis': {'backgroundcolor': '#E5ECF6',
                  'gridcolor': 'white',
                  'gridwidth': 0,
                  'linecolor': 'white',
                  'showbackground': False,
                  'ticks': '',
                  'zerolinecolor': 'white',
                  'visible': False},
        'yaxis': {'backgroundcolor': '#E5ECF6',
                  'gridcolor': 'white',
                  'gridwidth': 0,
                  'linecolor': 'white',
                  'showbackground': False,
                  'ticks': '',
                  'zerolinecolor': 'white',
                  'visible': False},
        'zaxis': {'backgroundcolor': '#E5ECF6',
                  'gridcolor': 'white',
                  'gridwidth': 0,
                  'linecolor': 'white',
                  'showbackground': False,
                  'ticks': '',
                  'zerolinecolor': 'white',
                  'visible': False}
    },
    paper_bgcolor='#f8f9fa',
))

default_scatter_marker = dict(marker=dict(
    size=12,
    opacity=1,
    line=dict(width=1, color='DarkSlateGrey')),
)
# not tested

plot_layout = {
    'title': 'Test',
    'height': '80vh',
    'width': '80vw',
    'background': '#000',  # not working
}
dos_plot_layout = {
    'height': '400px',
    'width': '800px',
    'background': '#f8f9fa',
}

# TODO: (optional) ability to en-/disable individual Atoms (that are in the uploaded file) and let MALA recalculate
#  -> helps see each Atoms' impact in the grid


print("_________________________________________________________________________________________")
print("STARTING UP...")

app = dash.Dash(__name__, external_stylesheets=[dbc.icons.BOOTSTRAP, dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)
app.title = 'MALAweb'

# until data is uploaded, show:
bandEn = 0
totalEn = 0
# TABLE SECTION
indent = '      '
# Data
row1 = html.Tr([html.Td(indent.join("Band - Energy"), style={'text-align': 'center'})], style={"font-weight": "bold"})
row2 = html.Tr([html.Td(0, id="bandEn", style={'text-align': 'right'})])
row3 = html.Tr([html.Td(indent.join("Total - Energy"), style={'text-align': 'center'})], style={"font-weight": "bold"})
row4 = html.Tr([html.Td(0, id="totalEn", style={'text-align': 'right'})])
row5 = html.Tr([html.Td(indent.join("Fermi - Energy"), style={'text-align': 'center'})], style={"font-weight": "bold"})
row6 = html.Tr([html.Td("placeholder", style={'text-align': 'right'})])
table_body = [html.Tbody([row1, row2, row3, row4, row5, row6])]

radioItems = dbc.RadioItems(
            options=[
                {"label": "Scatter", "value": "scatter"},
                {"label": "Isosurfae", "value": "volume"},
            ],
            inline=True,
            id="plot-choice",
        )

# ----------------
# Left SIDEBAR
sidebar = html.Div(
    dbc.Offcanvas(
        # default sidebar
        html.Div(
            [
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
                            Upload atompositions via .cube! (later npy)
                            ''', style={'text-align': 'center'}),
                            # TODO: make this give dynamic promts (like "choose a plot!")
                            # right now we're reloading the whole "welcome mala"-cell for that
                            dcc.Upload(
                                id='upload-data',
                                children=html.Div([
                                    'Drag & Drop', html.Br(), 'or ', html.Br(),
                                    html.A('Click to select Files')
                                ]),
                                style={
                                    'width': '90%',
                                    'height': 'auto',
                                    'lineHeight': '20px',
                                    'borderWidth': '1px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '5px',
                                    'textAlign': 'center',
                                    'margin': '1rem',
                                },
                                # don't allow multiple files to be uploaded
                                multiple=False
                            ),

                            dbc.Row([
                                dbc.Col(dbc.Button("reset", id="reset-data"), width=4),
                                dbc.Col(html.Div(id='output-upload-state', style={'margin': '2px'}),
                                        style={'text-align': 'center'}, width=8)
                            ])

                        ], className="upload-section"
                        ),
                    )),
                    id="collapse-upload",
                    is_open=True,
                ),

                dbc.Card(
                    html.H6(children='Choose Plot Style', style={'margin': '5px'}, id="open-plot-choice", n_clicks=0),
                    style={"text-align": "center", 'margin-top': '15px'}),

                dbc.Collapse(dbc.Card(dbc.CardBody(
                    html.Div(children=[radioItems]))),
                    id="collapse-plot-choice",
                    is_open=False,
                ),

            ], className="sidebar"
        ), id="offcanvas-l", is_open=True, scrollable=True, backdrop=False,
        style={'width': '15rem', 'margin-top': '3rem', 'margin-left': '0.5vw', 'border-radius': '10px',
               'height': 'min-content',
               'box-shadow': 'rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px'},
    ),
)

# Right SIDEBAR
side_r = html.Div()

sc_fig = go.Figure()
vol_fig = go.Figure()
dos_fig = go.Figure()
# start plot with empty fig, fill on updateScatter-/...-callback

# --------------------------
r_content_sc = html.Div([
    html.H5("Scatter"),
    dbc.Card(dbc.CardBody(
        [

            html.H5("Camera"),
            dbc.ButtonGroup(
                [
                    dbc.Button('Def.', id='default-cam', n_clicks=0),
                    dbc.Button('X-Y', id='x-y-cam', n_clicks=0),
                    dbc.Button('X-Z', id='x-z-cam', n_clicks=0),
                    dbc.Button('Y-Z', id='y-z-cam', n_clicks=0)
                ],
                size="sm",
            ),

            html.H5("Size"),
            dcc.Slider(6, 18, 2, value=12, id='sc-size'),

            html.H5("Opacity"),
            dbc.Input(type="number", min=0.1, max=1, step=0.1, id="sc-opac", placeholder="0.1 - 1", size="sm"),

            dbc.Checkbox(label='Outline', value=True, id='sc-outline'),
            dbc.Checkbox(label='Atoms', value=True, id='sc-atoms'),

        ]
    ))])
# --------------------------
r_content_vol = html.Div([
    html.H5("Volume"),
    dbc.Card(dbc.CardBody(
        [

            html.H5("Camera"),
            dbc.ButtonGroup(
                [
                    dbc.Button('Def.', id='default-cam-vol', n_clicks=0),
                    dbc.Button('X-Y', id='x-y-cam-vol', n_clicks=0),
                    dbc.Button('X-Z', id='x-z-cam-vol', n_clicks=0),
                    dbc.Button('Y-Z', id='y-z-cam-vol', n_clicks=0)
                ],
                size="sm",
            ),

            html.H5("Opacity"),
            dbc.Input(type="number", min=0.1, max=1, step=0.1, id="vol-opac", placeholder="0.1 - 1", size="sm"),
            dbc.Checkbox(label='Atoms', value=True, id='vol-atoms'),

        ]
    ))])
# ---------------------


scatter_plot = [
    # Center
    dbc.Row([

        # Plot section
        dbc.Col(
            [
                dbc.Card(dbc.CardBody(
                    [

                        html.Div(
                            dcc.Graph(id="scatter-plot", responsive=True, figure=sc_fig, style=plot_layout),
                            className="density-scatter-plot"
                        ),
                        # Tools
                        dbc.Button("Tools", id="open-sc-tools", n_clicks=0),
                        dbc.Collapse(
                            dbc.Card(dbc.CardBody(
                                [
                                    dbc.Row([
                                        # Buttons
                                        dbc.Col(
                                            dbc.ButtonGroup(
                                                [
                                                    dbc.Button('X', id='sc-active-x', active=False, outline=True,
                                                               color="primary", n_clicks=0),
                                                    dbc.Button('Y', id='sc-active-y', active=False, outline=True,
                                                               color="primary", n_clicks=0),
                                                    dbc.Button('Z', id='sc-active-z', active=False, outline=True,
                                                               color="primary", n_clicks=0),
                                                    dbc.Button("Density", id='active-dense', active=False, outline=True,
                                                               color="primary", n_clicks=0)

                                                ],
                                                vertical=True,
                                            ), width=1),

                                        # Sliders
                                        dbc.Col([
                                            dbc.Row([
                                                dbc.Col(dcc.RangeSlider(id='range-slider-cs-x',
                                                                        disabled=True,
                                                                        min=0,
                                                                        max=1,
                                                                        marks=None,
                                                                        pushable=True,
                                                                        tooltip={"placement": "bottom",
                                                                                 "always_visible": False},
                                                                        updatemode='drag')),
                                                dbc.Col(html.Img(id="reset-cs-x", src="/assets/x.svg", n_clicks=0,
                                                                 style={'width': '1.25em'}), width=1)
                                            ], style={"margin-top": "7px"}),  # X-Axis
                                            dbc.Row([
                                                dbc.Col(dcc.RangeSlider(
                                                    id='range-slider-cs-y',
                                                    disabled=True,
                                                    pushable=True,
                                                    min=0, max=1,
                                                    marks=None,
                                                    tooltip={"placement": "bottom", "always_visible": False},
                                                    updatemode='drag')),
                                                dbc.Col(html.Img(id="reset-cs-y", src="/assets/x.svg", n_clicks=0,
                                                                 style={'width': '1.25em'}), width=1)
                                            ]),  # Y-Axis
                                            dbc.Row([
                                                dbc.Col(dcc.RangeSlider(
                                                    id='range-slider-cs-z',
                                                    disabled=True,
                                                    pushable=True,
                                                    min=0, max=1,
                                                    marks=None,
                                                    tooltip={"placement": "bottom", "always_visible": False},
                                                    updatemode='drag')),
                                                dbc.Col(html.Img(id="reset-cs-z", src="/assets/x.svg", n_clicks=0,
                                                                 style={'width': '1.25em'}), width=1)

                                            ]),  # Z-Axis
                                            dbc.Row([

                                                dbc.Col(dcc.RangeSlider(
                                                    id='range-slider-dense',
                                                    disabled=True,
                                                    pushable=True,
                                                    min=0, max=1,
                                                    marks=None,
                                                    tooltip={"placement": "bottom", "always_visible": False},
                                                    updatemode='drag'), width=11),
                                                dbc.Col(html.Img(id="reset-dense", src="/assets/x.svg", n_clicks=0,
                                                                 style={'width': '1.25em', 'position': 'float'}),
                                                        width=1),

                                            ]),  # Density
                                        ], width=11),
                                    ]),
                                ]
                            )),
                            id="sc-tools-collapse",
                            is_open=False)
                    ]
                ), style={'background-color': 'rgba(248, 249, 250, 1)', 'width': 'min-content',
                          'align-content': 'center', 'margin-top': '1.5rem'}),
            ],
            className="plot-section"),

        # Right
        dbc.Col(
            #
            # ..
            # Settingsbar
            [
                dbc.Offcanvas(r_content_sc, id="offcanvas-r-sc", is_open=True,
                              style={'width': '15rem', 'height': 'min-content',
                                     'margin-top': '1.5vh',
                                     'margin-right': '0.5vw', 'border-radius': '10px',
                                     'box-shadow': 'rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px',
                                     'position': 'absolute', },
                              scrollable=True, backdrop=False, placement='end'),
                dbc.Button("<", id="open-settings-sc", n_clicks=0, style={'margin-top': '40vh'})

            ], style={}, id="r_sc")

    ]),

]

# VOLUME
volume_plot = dbc.Card(dbc.CardBody(html.Div(
                    dcc.Graph(id="volume-plot", figure=vol_fig, style=plot_layout),
                    className="density-vol-plot"
                )), style={'background-color': 'rgba(248, 249, 250, 1)', 'width': 'min-content', 'margin-top': '1rem'})


# DOS
dos_plot = html.Div(
    [
        # Density of State Section
        html.H4(indent.join('2D-Density-of-State-Plot'), style={'color': 'white', 'margin-top': '1.5rem'}),
        dbc.Card(dbc.CardBody(html.Div(
            dcc.Graph(id="dos-plot", figure=dos_fig, style=dos_plot_layout),
            className='dos-plot',
        )),
            style={'background-color': 'rgba(248, 249, 250, 1)', 'width': 'min-content',
                   'margin-bottom': '1rem', 'margin-top': '1rem',
                   'box-shadow': 'rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px'}),
    ],
    className="content"
)

# ----------------
# landing-cell for mc0
mc0_landing = html.Div([
    html.Div([html.H1([indent.join('Welcome')], className='greetings',
                      style={'text-align': 'center'}),
              html.H1([indent.join('To')], className='greetings',
                      style={'text-align': 'center'}),
              html.H1([indent.join('MALA')], className='greetings',
                      style={'text-align': 'center'}),
              html.Div('Upload a .cube-File for MALA to process', )],
             style={'text-align': 'center'}),
], style={'width': 'content-min', 'margin-top': '20vh'})

# updated cell for mc0
mc0_upd = html.Div([
    html.Div([html.H1([indent.join('Welcome')], className='greetings',
                      style={'text-align': 'center'}),
              html.H1([indent.join('To')], className='greetings',
                      style={'text-align': 'center'}),
              html.H1([indent.join('MALA')], className='greetings',
                      style={'text-align': 'center'}),
              html.Div('Please choose a plotting style', )],
             style={'text-align': 'center'}),
], style={'width': 'content-min', 'margin-top': '20vh'})
skel_layout = [
    dbc.Row([
        dbc.Col(id="l0", width=1, style={'background-color': 'red'}),
        dbc.Col(mc0_landing, id="mc0", width=10, style={'background-color': 'blue'}),
        dbc.Col(id="r0", width=1, style={'background-color': 'green'})

    ]),
    dbc.Row([
        dbc.Col(id="l1"),
        dbc.Col(id="mc1"),
        dbc.Col(id="r1")

    ]),
    dbc.Row([
        dbc.Col(id="l2"),
        dbc.Col(id="mc2"),
        dbc.Col(id="r2")

    ])
]

p_layout_landing = html.Div([

    dcc.Store(id="page_state", data="landing"),
    dcc.Store(id="cam_store"),
    dcc.Store(id="cam_store_v"),
    dcc.Store(id="df_store", storage_type="session"),
    dcc.Store(id="choice_store"),
    dcc.Store(id="sc_settings"),

    sidebar,
    dbc.Button(">", id="open-offcanvas-l", n_clicks=0, style={'position': 'fixed', 'margin-top': '40vh',
                                                              'margin-left': '0.5vw'}),

    html.Div(skel_layout, id="content-layout", style={'height': '100vh', 'background-color': '#023B59'}),

    side_r,
    dbc.Button("<", id="open-offcanvas-r", n_clicks=0, style={'position': 'fixed', 'margin-top': '40vh',
                                                              'margin-left': '0.5vw'}),

])
app.layout = p_layout_landing


# p_layout_plotting will be redefined on page_state-change
# parts of plotting_layout will be redefined on data-upload

# FGEDF4 as contrast ??


# CALLBACKS & FUNCTIONS

# sidebar_l collapses
@app.callback(
    Output("collapse-upload", "is_open"),
    Input("open-upload", "n_clicks"),
    Input("collapse-upload", "is_open"),
    prevent_initial_call=True,
)
def toggle_upload(n_header, is_open):
    if n_header:
        return not is_open


# this callback is totally optional and only decides if the reset-button should also reset plot-choice
# turned off by PreventingUpdate for now
@app.callback(
    Output("plot-choice", "value"),
    Input("reset-data", "n_clicks"),
    prevent_initial_call=True,
)
def resetPlotChoice(trigger_reset):
    raise PreventUpdate
    return []


@app.callback(
    Output("collapse-plot-choice", "is_open"),
    [Input("open-plot-choice", "n_clicks"),
     Input("page_state", "data"),
     Input("collapse-plot-choice", "is_open")],
    prevent_initial_call=True,
)
def toggle_plot_choice(n_header, page_state, is_open):
    # open plot-style-chooser when state is uploaded
    if dash.callback_context.triggered_id == "page_state" and page_state == "uploaded" or "plotting":
        return True
    elif n_header:
        return not is_open


# end of sidebar_l collapses


# CALLBACKS FOR SCATTERPLOT

# collapsable cross-section and density tools
@app.callback(
    Output("sc-tools-collapse", "is_open"),
    Input("open-sc-tools", "n_clicks"),
    Input("sc-tools-collapse", "is_open"),
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


# END OLD SC CS X


# OLD SC CS Y
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


# END OLD SC CS Y

# OLD SC CS Z
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


# END OLD SC CS Z


# OLD SC DENS
@app.callback(
    Output("range-slider-dense", "disabled"),
    Output("active-dense", "active"),
    Input("active-dense", "n_clicks"),
    Input("range-slider-dense", "disabled"),
    State("active-dense", "active"),
    prevent_initial_call=True)
def toggle_density_sc(n_d, active, bc):
    if n_d:
        return not active, not bc


# END OLD SC DENS


@app.callback(
    Output("range-slider-cs-x", "value"),
    Input("reset-cs-x", "n_clicks"),
    Input("df_store", "data"),
    prevent_initial_call=True)
def reset_cs_x(n_clicks, data):
    if data is not None:
        scatter_df = pd.DataFrame(data['MALA_DF']['scatter'])
        return [min(scatter_df['x']), max(scatter_df['x'])]


@app.callback(
    Output("range-slider-cs-y", "value"),
    Input("reset-cs-y", "n_clicks"),
    Input("df_store", "data"),
    prevent_initial_call=True)
def reset_cs_y(n_clicks, data):
    if data is not None:
        scatter_df = pd.DataFrame(data['MALA_DF']['scatter'])
        return [min(scatter_df['y']), max(scatter_df['y'])]


@app.callback(
    Output("range-slider-cs-z", "value"),
    Input("reset-cs-z", "n_clicks"),
    Input("df_store", "data"),
    prevent_initial_call=True)
def reset_cs_z(n_clicks, data):
    if data is not None:
        scatter_df = pd.DataFrame(data['MALA_DF']['scatter'])
        return [min(scatter_df['z']), max(scatter_df['z'])]


@app.callback(
    Output("range-slider-dense", "value"),
    Input("reset-dense", "n_clicks"),
    Input("df_store", "data"),
    prevent_initial_call=True)
def reset_cs_dense(n_clicks, data):
    if data is not None:
        scatter_df = pd.DataFrame(data['MALA_DF']['scatter'])
        return [min(scatter_df['val']), max(scatter_df['val'])]


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
def store_Scatter_CamSettings(default_clicks, x_y_clicks, x_z_clicks, y_z_clicks, user_in):
    print("stored scattercam")
    print("triggered by:", dash.callback_context.triggered_id)
    print(user_in)
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
        print("a")
        if user_in is None:
            raise PreventUpdate
        else:
            if 'scene.camera' in user_in.keys():
                print("c")
                return user_in['scene.camera']
                # stops the update in case the callback is triggered by zooming/smth else
            else:
                print("d")
                raise dash.exceptions.PreventUpdate
    # Feels very unelegant -> this is always run twice when switching to scatter for example
    # END OF SCATTER CALLBACKS



@app.callback(
    Output("cam_store_v", "data"),
    [
        # Input("default-cam", "n_clicks"),
        # Input("x-y-cam", "n_clicks"),
        # Input("x-z-cam", "n_clicks"),
        # Input("y-z-cam", "n_clicks"),
        Input("volume-plot", "relayoutData")],
    prevent_initial_call=True,
)
def store_Volume_CamSettings(user_in):
    # user_in is the camera position set by mouse movement, it has to be updated on every mouse input on the fig
    if dash.callback_context.triggered_id is not None:
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
        # reset stored_cam_setting if user moves camera
        elif dash.callback_context.triggered_id == "volume-plot":
            if user_in is not None:
                if 'scene.camera' in user_in.keys():
                    print("stored vol cam")
                    return user_in['scene.camera']
                    # stops the update in case the callback is triggered by zooming/smth else
            else:
                raise dash.exceptions.PreventUpdate
        else:
            raise dash.exceptions.PreventUpdate



# UPDATE STORED DATA

# page state
@app.callback(
    Output("page_state", "data"),
    [Input("df_store", "data"),
     Input("choice_store", "data"),
     Input("reset-data", "n_clicks")],
    prevent_initial_call=True)
def updatePageState(trig1, trig2, trig3):
    if trig1 is not None and trig2 is not None and (
            dash.callback_context.triggered_id == "choice_store" or "df_store"):
        print(trig2)
        print("State changed to: plotting")
        return "plotting"

    if ((trig1 is not None) and trig2 is not None) and dash.callback_context.triggered_id != "reset-data":
        print("State changed to: uploaded")
        # TODO: maybe green border around upload section?
        return "uploaded"

    if trig3 is not None and dash.callback_context.triggered_id == "reset-data":
        print("State changed to: landing")
        return "landing"


# dataframes
@app.callback(
    Output("df_store", "data"),
    Output('upload-data', 'contents'),
    [Input('upload-data', 'contents'),
     Input("reset-data", "n_clicks")],
    prevent_initial_call=True)
def updateDF(f_data, reset):
    # GOAL:
    # f_data = uploaded data -> to be .npy
    # TODO: smth like (mala_data = mala.webAPI(f_data)) (run a mala .getter(uploadedData))
    #  --> mala takes uploaded data and returns calculations
    #  --> waiting for Lenz

    # TODO: check if data is valid before updating
    #  maybe do this on upload, so this callback isn't even run
    #  --> raise preventUpdate if not

    # Always returning None for the Upload-Component as well, so that it's possible to reupload
    # (-> gotta clear up the space first)

    if dash.callback_context.triggered_id == "reset-data":
        return None, None
    # (a) GET DATA FROM MALA (/ inference script)
    print("Running MALA-Inference")
    mala_data = mala_inference.results
    bandEn = mala_data['band_energy']
    totalEn = mala_data['total_energy']
    density = mala_data['density']
    dOs = mala_data['density_of_states']
    enGrid = mala_data['energy_grid']

    coord_arr = np.column_stack(
        list(map(np.ravel, np.meshgrid(*map(np.arange, density.shape), indexing="ij"))) + [density.ravel()])
    data0 = pd.DataFrame(coord_arr, columns=['x', 'y', 'z', 'val'])  # untransformed Dataset

    atoms = [[], [], [], [], []]

    # Reding .cube-File
    # TODO: this has to be done with uploaded .npy

    # (b) GET ATOMPOSITION & AXIS SCALING FROM .cube CREATED BY MALA (located where 'mala-inference-script' is located
    atom_data = '/home/maxyyy/PycharmProjects/mala/app/Be2_density.cube'

    # 0-1 = Comment, Energy, broadening     //      2 = number of atoms, coord origin
    # 3-5 = number of voxels per Axis (x/y/z), lentgh of axis-vector -> info on cell-warping
    # 6-x = atompositions

    with open(atom_data, 'r') as f:
        lines = f.read().splitlines()
        no_of_atoms, _, _, _ = lines[2].split()

        # AXIS-SCALING-FACTOR
        # axis-List-Format: voxelcount[0]   X-Scale[1]     Y-Scale[2]     Z-Scale[3]
        x_axis = [float(i) for i in lines[3].split()]
        y_axis = [float(i) for i in lines[4].split()]
        z_axis = [float(i) for i in lines[5].split()]

    # READING ATOMPOSITIONS
    for i in range(0, int(no_of_atoms)):
        ordinal_number, charge, x, y, z = lines[6 + i].split()  # atom-data starts @line-index 6
        # atoms-List-Format: ordinalNumber[0]    charge[1]  x[2]   y[3]   z[4]
        atoms[0].append(int(ordinal_number))
        atoms[1].append(float(charge))
        atoms[2].append(float(x))
        atoms[3].append(float(y))
        atoms[4].append(float(z))
    atoms_data = pd.DataFrame(
        data={'x': atoms[2], 'y': atoms[3], 'z': atoms[4], 'ordinal': atoms[0], 'charge': atoms[1]})

    # SCALING AND SHEARING SCATTER DF
    # (b) SCALING to right voxel-size
    # need to bring atompositions and density-voxels to the same scaling
    data0['x'] *= x_axis[1]
    data0['y'] *= y_axis[2]
    data0['z'] *= z_axis[3]
    data_sc = data0.copy()
    data_vol = data0.copy()

    # SHEARING für scatter_3d
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
                   - so far only doing that in a complicated way for dataframe in scatter_3d format
                   - need to to this for volume too
                   --> good way would be a matrix multiplication of some sort
    '''

    # _______________________________________________________________________________________

    df_store = {'MALA_DF': {'default': data0.to_dict("records"), 'scatter': data_sc.to_dict("records"),
                            'volume': data_vol.to_dict("records")}, 'MALA_DATA': mala_data,
                'INPUT_DF': atoms_data.to_dict("records"),
                'SCALE': {'x_axis': x_axis, 'y_axis': y_axis, 'z_axis': z_axis}}

    print("DATA IMPORT COMPLETE")
    print("_________________________________________________________________________________________")
    return df_store, None


# PLOT-CHOICE STORING

@app.callback(
    Output("choice_store", "data"),
    [Input('plot-choice', 'value')],
    prevent_initial_call=True)
def updatePlotChoice(choice):
    return choice


# SC SETTINGS STORING
# TODO: fix Opacity/Outline (Double Binding?)
@app.callback(
    Output("sc_settings", "data"),
    [Input('sc-size', 'value'),
     Input("sc-outline", "value"),
     Input("sc-atoms", "value"),
     Input("sc-opac", "value")
     ],
    State("sc_settings", "data"))
def updateSCsettings(size, outline, atoms, opac, saved):
    print("sc settings updated")

    if saved is None:
        settings = {
            "size": 12,
            "opac": 1,
            "outline": True,
            "atoms": True,
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
            settings["outline"] = False
        print(settings["opac"])
    elif dash.callback_context.triggered_id == "sc-outline":
        settings["outline"] = outline
    elif dash.callback_context.triggered_id == "sc-atoms":
        settings["atoms"] = atoms
    return settings


# END UPDATE FOR STORED DATA


# LAYOUT CALLBACKS
# UPDATE BASE LAYOUT
# unused right now
@app.callback(
    Output("content-layout", "children"),
    [State("choice_store", "data"),
     Input("df_store", "data")],
    prevent_initial_call=True)
def updateLayout(plots, page_state):
    # could change size of rows/columns here
    raise PreventUpdate
    # return skel_layout


# UPDATING CONTENT-CELL 0

@app.callback(
    Output("mc0", "children"),
    Input("page_state", "data"),
    State("choice_store", "data"),
    State("df_store", "data"),
    prevent_initial_call=True)
def updateMC0(state, plots, data):
    if data is None or state == "landing":
        return mc0_landing
    elif plots is None or state == "updated":
        return mc0_upd

    elif state == "plotting" and data is not None:
        if plots == "scatter":
            # TODO: extract this into a function which can be called by all three update_mc callbacks
            # update c0
            return scatter_plot
        elif plots == "volume":
            return volume_plot
        elif plots == "dos":
            return dos_plot


# UPDATING CONTENT-CELL 1
@app.callback(
    Output("mc1", "children"),
    Input("page_state", "data"),
    State("choice_store", "data"),
    State("df_store", "data"),
    prevent_initial_call=True,
)
def updateMC1(state, plots, data):
    if data is None or state == "landing" or "updated":
        return html.Div()

    elif state == "plotting" and data is not None:
        if len(plots) > 1:
            if plots[1] == "scatter":
                # TODO: extract this into a function which can be called by all three update_mc callbacks
                # update c1
                return scatter_plot
            elif plots[1] == "volume":
                return volume_plot
            elif plots[1] == "dos":
                return dos_plot


# UPDATING CONTENT-CELL 1
@app.callback(
    Output("mc2", "children"),
    Input("page_state", "data"),
    State("choice_store", "data"),
    State("df_store", "data"),
    prevent_initial_call=True,
)
def updateMC2(state, plots, data):
    if data is None or state == "landing" or "updated":
        return html.Div()

    elif state == "plotting" and data is not None:
        if len(plots) > 2:
            if plots[2] == "scatter":
                # TODO: extract this into a function which can be called by all three update_mc callbacks
                # update c0
                return scatter_plot
            elif plots[2] == "volume":
                return volume_plot
            elif plots[2] == "dos":
                return dos_plot


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
def update_scatter_tools(data):
    if data is None:    # in case of reset:
        raise PreventUpdate
    else:
        df = pd.DataFrame(data['MALA_DF']['scatter'])
        scale = pd.DataFrame(data['SCALE'])
        x_step = scale["x_axis"][1]

        y_step = scale["y_axis"][2]
        z_step = scale["z_axis"][3]
        dense_step = round((max(df['val']) - min(df['val'])) / 30, ndigits=5)
        print(dense_step + min(df["val"]))
        print(min(df["val"]), max(df["val"]))
        return min(df["x"]), max(df["x"]), x_step, \
               min(df["y"]), max(df["y"]), y_step, \
               min(df["z"]), max(df["z"]), z_step, \
               min(df["val"]), max(df["val"]), dense_step


'''
# cam-position buttons have to stay as parameters, so they trigger an update. 
cam_store can't be an input or else it triggers an update everytime the cam is moved
'''


@app.callback(
    Output("scatter-plot", "figure"),
    [
        # Tools
        Input("range-slider-dense", "value"),
        Input("active-dense", "active"),
        Input("range-slider-cs-x", "value"),
        Input("sc-active-x", "active"),
        Input("range-slider-cs-y", "value"),
        Input("sc-active-y", "active"),
        Input("range-slider-cs-z", "value"),
        Input("sc-active-z", "active"),
        # Settings
        Input("sc_settings", "data"),
        Input("default-cam", "n_clicks"),
        Input("x-y-cam", "n_clicks"),
        Input("x-z-cam", "n_clicks"),
        Input("y-z-cam", "n_clicks"),
        Input("choice_store", "data")
    ],
    [State("scatter-plot", "relayoutData"),
     State("cam_store", "data"),
     State("df_store", "data"),
     ],
    prevent_initial_call=True,
)
def updateScatter(slider_range, dense_inactive, slider_range_cs_x, cs_x_inactive, slider_range_cs_y, cs_y_inactive,
                  slider_range_cs_z, cs_z_inactive,
                  settings,
                  cam_default, cam_xy, cam_xz, cam_yz, plots, relayout_data, stored_cam_settings, f_data, ):
    # DATA
    if f_data is None:
        raise PreventUpdate
    print("UPDATING SCATTER")
    # the denisity-Dataframe  for Scatter that we're updating, taken from df_store (=f_data)
    df = pd.DataFrame(f_data['MALA_DF']['scatter'])
    dfu = df.copy()
    # mala_data = pd.DataFrame().from_dict(f_data.MALA_DATA)    # not necessary here
    # atoms-Dataframe also taken from f_data
    atoms = pd.DataFrame(f_data['INPUT_DF'])
    no_of_atoms = len(atoms)
    # Dataframes are ready

    # TOOLS
    # (inside Collapsable)
    # TODO: slider functionality
    # filter-by-density
    if slider_range is not None and dense_inactive:  # Any slider Input there?
        print("dense")
        low, high = slider_range
        mask = (dfu['val'] >= low) & (dfu['val'] <= high)
        dfu = dfu[mask]
    else:
        mask = (dfu['val'] >= min(dfu['val'])) & (dfu['val'] <= max(dfu['val']))
        # TODO: mask could be referenced without being defined
    # x-Cross-section
    if slider_range_cs_x is not None and cs_x_inactive:  # Any slider Input there?
        low, high = slider_range_cs_x
        mask = (dfu['x'] >= low) & (dfu['x'] <= high)
        dfu = dfu[mask]
    else:
        mask = (dfu['x'] >= min(dfu['x'])) & (dfu['x'] <= max(dfu['x']))
        dfu = dfu[mask]
    # Y-Cross-section
    if slider_range_cs_y is not None and cs_y_inactive:  # Any slider Input there?
        low, high = slider_range_cs_y
        mask = (dfu['y'] >= low) & (dfu['y'] <= high)
        dfu = dfu[mask]
    else:
        mask = (dfu['y'] >= min(dfu['y'])) & (dfu['y'] <= max(dfu['y']))
        dfu = dfu[mask]
    # Z-Cross-section
    if slider_range_cs_z is not None and cs_z_inactive:  # Any slider Input there?
        low, high = slider_range_cs_z
        mask = (dfu['z'] >= low) & (dfu['z'] <= high)
        dfu = dfu[mask]
    else:
        mask = (dfu['z'] >= min(dfu['z'])) & (dfu['z'] <= max(dfu['z']))
        dfu = dfu[mask]

        # SETTINGS
        # plot-settings

    # SETTINGS

    # updating fig according to (cs'd) DF
    fig_upd = px.scatter_3d(
        dfu, x="x", y="y", z="z",
        color="val",
        hover_data=['val'],
        opacity=settings["opac"],
        color_continuous_scale=px.colors.sequential.Inferno_r,
        range_color=[df.min()['val'], df.max()['val']],
        # takes color range from original dataset, so colors don't change
        template=templ1,
    )

    # UPDATING FIG-SCENE- PROPERTIES
    fig_upd.update_scenes(xaxis_showgrid=False, yaxis_showgrid=False, zaxis_showgrid=False)

    # CAMERA
    if dash.callback_context.triggered_id == "default-cam":
        fig_upd.update_layout(scene_camera=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=1.5, y=1.5, z=1.5)
        ))
    elif dash.callback_context.triggered_id == "x-y-cam":
        fig_upd.update_layout(scene_camera=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=0, y=0, z=3.00)
        ))
    elif dash.callback_context.triggered_id == "x-z-cam":
        fig_upd.update_layout(scene_camera=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=0, y=3.00, z=0)
        ))
    elif dash.callback_context.triggered_id == "y-z-cam":
        fig_upd.update_layout(scene_camera=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=3.00, y=0, z=0)))

    else:
        fig_upd.update_layout(scene_camera=stored_cam_settings)
    '''
    set camera-position according to the clicked button, 
                                OR 
                - if no button has been clicked - 
    to the most recently stored manually adjusted camera position
    '''

    # WAY TO CHANGE SIZE, OPACITY, OUTLINE

    # Outline settings
    if settings["outline"]:
        outlined = dict(width=1, color='DarkSlateGrey')
    else:
        outlined = dict(width=0, color='DarkSlateGrey')

    fig_upd.update_traces(marker=dict(size=settings["size"], line=outlined), selector=dict(mode='markers'))

    # ADD ATOMS

    # TODO: COLOR-CODING ATOMS BASED OFF THEIR CHARGE
    if settings["atoms"]:
        atom_colors = []
        for i in range(0, int(no_of_atoms)):
            if atoms['charge'][i] == 4.0:
                atom_colors.append("black")
            else:
                atom_colors.append("white")
        fig_upd.add_trace(
            go.Scatter3d(name="Atoms", x=atoms['x'], y=atoms['y'], z=atoms['z'], mode='markers',
                         marker=dict(size=30, color=atom_colors)))

    return fig_upd


# CALLBACKS FOR VOLUME PLOT
# TODO: still has the settings-inputs of scatter + data still not sheared
# could also sync cam position of both scatter and volume. would save a store, but would run both "constructors" on cam movement
@app.callback(
    Output("volume-plot", "figure"),
    [
        # Input("range-slider-cs-x", "value"),
        # Input("x-collapse", "is_open"),
        # Input("range-slider-cs-y", "value"),
        # Input("y-collapse", "is_open"),
        # Input("range-slider-cs-z", "value"),
        # Input("z-collapse", "is_open"),
        # Input("opacity-slider", 'value'),
        # Input("scatter-atoms", "value")
        Input("choice_store", "data")
    ],
    [
        State("volume-plot", "relayoutData"),
        State("df_store", "data"),
        State("cam_store_v", "data")
    ]
)
def updateVolume(plot_choice, relayout_data, f_data, stored_cam_settings):
    if f_data is None:
        raise PreventUpdate
    dfu = pd.DataFrame(f_data['MALA_DF']['volume'])
    atoms = pd.DataFrame(f_data['INPUT_DF'])
    no_of_atoms = len(atoms)

    atoms_enabled = [True]  # as long as volume doesn't have it's own settings yet
    # DECIDING ON ATOM-COLOR BASEd OFF THEIR CHARGE TODO
    atom_colors = []
    for i in range(0, int(no_of_atoms)):
        if atoms['charge'][i] == 4.0:
            atom_colors.append("black")
        else:
            atom_colors.append("white")

    fig_upd = go.Figure(data=go.Volume(
        x=dfu.x,
        y=dfu.y,
        z=dfu.z,
        value=dfu.val,
        opacity=0.3,
        surface_count=17,
        colorscale=px.colors.sequential.Inferno_r,
        cauto=True
    ))

    # ADD ATOMS
    # seemingly in wrong position, but they are right. Vol_fig just isn't sheared properly (yet)
    if True in atoms_enabled:
        fig_upd.add_trace(
            go.Scatter3d(x=atoms['x'], y=atoms['y'], z=atoms['z'], mode='markers',
                         marker=dict(size=30, color=atom_colors)))

    # SCATTER GRID PROPERTIES
    fig_upd.update_scenes(xaxis_showgrid=False, yaxis_showgrid=False, zaxis_showgrid=False)

    # TODO: SETTINGS

    # CAMERA
    if dash.callback_context.triggered_id == "default-cam":
        fig_upd.update_layout(scene_camera=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=1.5, y=1.5, z=1.5)
        ))
    elif dash.callback_context.triggered_id == "x-y-cam":
        fig_upd.update_layout(scene_camera=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=0, y=0, z=3.00)
        ))
    elif dash.callback_context.triggered_id == "x-z-cam":
        fig_upd.update_layout(scene_camera=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=0, y=3.00, z=0)
        ))
    elif dash.callback_context.triggered_id == "y-z-cam":
        fig_upd.update_layout(scene_camera=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=3.00, y=0, z=0)))

    else:
        fig_upd.update_layout(scene_camera=stored_cam_settings)
    '''
    set camera-position according to the clicked button, 
                                OR 
                - if no button has been clicked - 
    to the most recently stored manually adjusted camera position
    '''

    # <----------------------------------------------------->

    return fig_upd


# END OF CALLBACKS FOR VOLUME PLOT

# TODO: updateDoS
@app.callback(
    Output("dos-plot", "figure"),
    [Input("choice_store", "data")],
    [State("df_store", "data")]
)
def updateDoS(plot_choice, f_data):
    print("update dos")
    if f_data is None:
        raise PreventUpdate
    dOs = f_data['MALA_DATA']['density_of_states']
    df = pd.DataFrame(dOs, columns=['density of state'])
    upd_fig = px.scatter(df)
    return upd_fig


# END OF CALLBACKS FOR DOS PLOT


# CALLBACKS FOR SIDEBAR

# toggle canvas
@app.callback(  # sidebar_l canvas
    Output("offcanvas-l", "is_open"),
    Input("open-offcanvas-l", "n_clicks"),
    [State("offcanvas-l", "is_open")],
)
def toggle_offcanvas_l(n1, is_open):
    if n1:
        return not is_open
    return is_open


@app.callback(  # sidebar_r canvas (1/?)
    Output("offcanvas-r-sc", "is_open"),
    Input("open-settings-sc", "n_clicks"),
    [State("offcanvas-r-sc", "is_open")],
)
def toggle_scatter_settings(n1, is_open):
    print("toggle")
    if n1:
        return not is_open
    return is_open


# FILE-UPLOAD-STATUS
@app.callback(
    Output('output-upload-state', 'children'),
    [Input('upload-data', 'filename'),
     Input('upload-data', 'contents'),
     Input('df_store', 'data')],
    prevent_initial_call=True,
)
def uploadStatus(filename, contents, data):
    # checks for .cubes for now, as long as im working on visuals
    # will check for .npy when mala is ready to give .cube output from
    # is this enough input-sanitization or proper type-check needed?
    # upload component also has accept property to allow only certain types - might be better
    print(dash.callback_context.triggered_id)
    if data is None:
        return "Awaiting Upload.."
    elif filename is not None and data is not None:
        if filename.endswith('.cube'):

            # USER INPUT ATOM POSITIONS - .cube File Upload
            # 1. File Upload of .cube File
            # 2. TODO: parse file with ASE
            # ase.io.read(contents)
            # 3. process with MALA
            # DONE:
            # receiving MALA Input (from script for now)
            # 4. contents

            return 'Upload successful'
        else:
            return 'Wrong file-type. .cube required'
    else:
        return ''


# END OF CALLBACKS FOR SIDEBAR

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
