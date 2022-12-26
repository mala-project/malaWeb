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
    'height': '55vh',
    'width': '72vw',
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

# Formatting + shearing Data
# density- import / conversion to pandas dataframe / fig - density-visualisation params / plot-layout params


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

                dbc.Collapse(dbc.Card(dbc.CardBody(html.Div(children=dcc.Dropdown(
                    {'scatter': 'Scatter', 'volume': 'Volume', 'dos': 'DoS'}, multi=True,
                    id='plot-choice', placeholder='Choose Plot Type', persistence=True, persistence_type='memory')))),
                    id="collapse-plot-choice",
                    is_open=False,
                ),

            ], className="sidebar"
        ), id="offcanvas-l", is_open=True, scrollable=True, backdrop=False,
        style={'width': '15rem', 'margin-top': '1.5rem', 'margin-left': '0.5vw', 'border-radius': '10px',
               'height': 'min-content',
               'box-shadow': 'rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px'},
    ),
)

sc_fig = go.Figure()
vol_fig = go.Figure()
dos_fig = go.Figure()
# start plot with empty fig, fill on updateScatter-/...-callback
scatter_plot = html.Div(
    [
        # Plot Section
        html.Div(
            [
                html.H3([indent.join('3D-Density-Plot'), ' (scatter)'],
                        style={'color': 'white', 'margin-top': '1.5rem'}),
                dbc.Card(dbc.CardBody(
                    [
                        html.Div(
                            dcc.Graph(id="scatter-plot", figure=sc_fig, style=plot_layout),
                            className="density-scatter-plot"
                        ),
                        html.Hr(style={'margin-bottom': '2rem', 'margin-top': '2rem'}),
                        dbc.Button("Settings", id="open-sc-settings", n_clicks=0),
                        dbc.Collapse(
                            dbc.Card(dbc.CardBody(
                                [
                                    html.H5("Size"),
                                    dcc.Slider(6, 18, 2, value=12, id='size-slider'),
                                    html.H5("Opacity"),
                                    dcc.Slider(0.1, 1, 0.1, value=1, id='opacity-slider'),

                                    dcc.Checklist(options=[{'label': '  Outline', 'value': True}], value=[True],
                                                  id='outline-check'),
                                    dcc.Checklist(options=[{'label': '  Atoms', 'value': True}], value=[True],
                                                  id='scatter-atoms'),
                                    html.Div([
                                        html.Button('Default', id='default-cam', n_clicks=0),
                                        html.Button('X-Y', id='x-y-cam', n_clicks=0),
                                        html.Button('X-Z', id='x-z-cam', n_clicks=0),
                                        html.Button('Y-Z', id='y-z-cam', n_clicks=0)],
                                    ),
                                ], style={"display": "inline"}
                            )),
                            id="sc-settings-collapse",
                            is_open=False),
                    ]
                ), style={'background-color': 'rgba(248, 249, 250, 1)', 'width': 'min-content',
                          'align-content': 'center'}),
            ],
            className="plot-section"
        ),


    ],
    className="content"
)
# VOLUME
volume_plot = html.Div(
    [
        html.Div(
            [
                html.H5([indent.join('3D-Density-Plot (volume)')], style={'color': 'white', 'margin-top': '1.5rem'}),
                dbc.Card(dbc.CardBody(html.Div(
                    dcc.Graph(id="volume-plot", figure=vol_fig, style=plot_layout),
                    className="density-vol-plot"
                )), style={'background-color': 'rgba(248, 249, 250, 1)', 'width': 'min-content', 'margin-top': '1rem'}),
            ],
            className="plot-section"
        ),
    ],
    className="content"
)
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
                dbc.Col(id="l0"),
                dbc.Col(mc0_landing, id="mc0"),
                dbc.Col(id="r0"),
            ]),
            dbc.Row([
                dbc.Col(id="l1"),
                dbc.Col(id="mc1"),
                dbc.Col(id="r1"),
            ]),
            dbc.Row([
                dbc.Col(id="l2"),
                dbc.Col(id="mc2"),
                dbc.Col(id="r2"),
            ])
        ]

p_layout_landing = html.Div([

    dcc.Store(id="page_state", data="landing"),
    dcc.Store(id="cam_store"),
    dcc.Store(id="cam_store_v"),
    dcc.Store(id="df_store"),
    dcc.Store(id="choice_store"),
    sidebar,
    dbc.Button(">", id="open-offcanvas-l", n_clicks=0, style={'position': 'fixed', 'margin-top': '40vh',
            'margin-left': '0.5vw'}),

    html.Div(skel_layout, id="content-layout", style={'height': '100vh', 'background-color': '#023B59'})

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

# sidebar-sc collapse
@app.callback(
    Output("r_canvas_sc", "is_open"),
    Input("open-canvas-r", "n_clicks"),
    State("r_canvas_sc", "is_open"),
    prevent_initial_call=True,
)
def openScatterSettings(n_clicks, is_open):
    print("lol")
    return not is_open



# CALLBACKS FOR SCATTERPLOT

# collapsable cross-section settings
@app.callback(
    Output("sc-settings-collapse", "is_open"),
    Input("open-sc-settings", "n_clicks"),
    Input("sc-settings-collapse", "is_open"),
    prevent_initial_call=True)
def toggle_sc_settings(n_sc_s, is_open):
    if n_sc_s:
        return not is_open

@app.callback(
    Output("x-collapse", "is_open"),
    Input("collapse-x", "n_clicks"),
    Input("x-collapse", "is_open"),
    prevent_initial_call=True)
def toggle_x_cs(n_x, is_open):
    if n_x:
        return not is_open

@app.callback(
    Output("y-collapse", "is_open"),
    Input("collapse-y", "n_clicks"),
    Input("y-collapse", "is_open"),
    prevent_initial_call=True)
def toggle_y_cs(n_y, is_open):
    if n_y:
        return not is_open

@app.callback(
    Output("z-collapse", "is_open"),
    Input("collapse-z", "n_clicks"),
    Input("z-collapse", "is_open"),
    prevent_initial_call=True)
def toggle_z_cs(n_z, is_open):
    if n_z:
        return not is_open

@app.callback(
    Output("dense-collapse", "is_open"),
    Input("collapse-dense", "n_clicks"),
    Input("dense-collapse", "is_open"),
    prevent_initial_call=True)
def toggle_density_rs(n_d, is_open):
    if n_d:
        return not is_open

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
        # user input camera:
        elif dash.callback_context.triggered_id == "scatter-plot":
            if user_in is not None:
                if 'scene.camera' in user_in.keys():
                    return user_in['scene.camera']
                    # stops the update in case the callback is triggered by zooming/smth else
            else:
                raise dash.exceptions.PreventUpdate


    # END OF SCATTER CALLBACKS


# UPDATE STORED DATA

    # page state
@app.callback(
    Output("page_state", "data"),
    [Input("df_store", "data"),
     Input("choice_store", "data"),
     Input("reset-data", "n_clicks")],
    prevent_initial_call=True)
def updatePageState(trig1, trig2, trig3):
    if trig1 is not None and trig2 is not None and len(trig2) != 0 and (dash.callback_context.triggered_id == "choice_store" or "df_store"):
        print(trig2)
        print("State changed to: plotting")
        return "plotting"

    if ((trig1 is not None) and trig2 is not None and len(trig2) == 0) and dash.callback_context.triggered_id != "reset-data":
        print("State changed to: uploaded")
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
    atoms_data = pd.DataFrame(data={'x': atoms[2], 'y': atoms[3], 'z': atoms[4], 'ordinal': atoms[0], 'charge': atoms[1]})

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
                'INPUT_DF': atoms_data.to_dict("records"), 'SCALE': {'x_axis': x_axis, 'y_axis': y_axis, 'z_axis': z_axis}}

    print("DATA IMPORT COMPLETE")
    print("_________________________________________________________________________________________")
    return df_store, None



# PLOT-CHOICE STORING

@app.callback(
    Output("choice_store", "data"),
    [Input('plot-choice', 'value')],
    prevent_initial_call=True)
def updatePlotChoice(choice):
    print("choice updated")
    return choice

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
    #return skel_layout


# UPDATING CONTENT-CELL 0

# maybe work with relayout to figure out if cells needs update in plot-choice-change
# -> can we ID what figure is displayed when the cells needs updating?
@app.callback(
    Output("mc0", "children"),
    Output("r0", "children"),
    Input("page_state", "data"),
    State("choice_store", "data"),
    State("df_store", "data"),
    prevent_initial_call=True)
def updateMC0(state, plots, data):
    if data is None or state == "landing":
        return mc0_landing, html.Div()
    elif plots is None or len(plots) == 0 or state == "updated":
        return mc0_upd, html.Div()

    elif state == "plotting" and data is not None:
        r_canvas_sc = html.Div()
        scale = pd.DataFrame(data['SCALE'])
            # scale['x_axis'][0] = x_axis Voxels // [1] = X-scaling on x // [2] = X-scaling on y // [3] = X-scaling on z
        if plots[0] == "scatter":
            # TODO: extract this into a function which can be called by all three update_mc callbacks
            scatter_df = pd.DataFrame(data['MALA_DF']['scatter'])
            # scatter
            r_content_sc = html.Div(
                # Idea: draw markers on coord-rangeslider where atoms are
                dbc.Card(dbc.CardBody(
                    [
                        # Buttonrow
                        dbc.Row([
                            dbc.Col(html.Button('X', id='collapse-x', n_clicks=0, style={'width': '2em'})),
                            dbc.Col(html.Button('Y', id='collapse-y', n_clicks=0, style={'width': '2em'})),
                            dbc.Col(html.Button('Z', id='collapse-z', n_clicks=0, style={'width': '2em'})),
                            dbc.Col(
                                html.Img(src="assets/dens.png", id='collapse-dense',
                                         style={"width": "1.8em", "height": "1.8em"},
                                         n_clicks=0))
                        ], className='g-0'),
                        # Sliderrow
                        dbc.Row([
                            dbc.Col(
                                dbc.Collapse(
                                    [
                                        html.Img(id="reset-cs-x", src="/assets/x.svg", n_clicks=0,
                                                 style={'width': '1.25em'}),
                                        dcc.RangeSlider(id='range-slider-cs-x', min=min(scatter_df['x']),
                                                        max=max(scatter_df['x']),
                                                        marks=None,
                                                        tooltip={"placement": "bottom", "always_visible": False},
                                                        updatemode='drag', vertical=True, verticalHeight=800,
                                                        pushable=scale['x_axis'][1])
                                    ], style={'padding': '8px', 'width': '2em'}, id="x-collapse", is_open=False
                                )
                            ),
                            dbc.Col(
                                dbc.Collapse(
                                    [
                                        html.Img(id="reset-cs-y", src="/assets/x.svg", n_clicks=0,
                                                 style={'width': '1.25em'}),
                                        dcc.RangeSlider(
                                            id='range-slider-cs-y',
                                            min=min(scatter_df['y']), max=max(scatter_df['y']),
                                            marks=None, tooltip={"placement": "bottom", "always_visible": False},
                                            updatemode='drag', vertical=True, verticalHeight=800, pushable=scale['y_axis'][2])],
                                    style={'padding': '7px', 'width': '2em'}, id="y-collapse", is_open=False
                                )
                            ),
                            dbc.Col(
                                dbc.Collapse(
                                    [
                                        html.Img(id="reset-cs-z", src="/assets/x.svg", n_clicks=0,
                                                 style={'width': '1.25em'}),
                                        dcc.RangeSlider(
                                            id='range-slider-cs-z',
                                            min=min(scatter_df['z']), max=max(scatter_df['z']),
                                            marks=None, tooltip={"placement": "bottom", "always_visible": False},
                                            updatemode='drag', vertical=True, verticalHeight=800, pushable=scale['z_axis'][3])],
                                    style={'padding': '7px', 'width': '2em'}, id="z-collapse", is_open=False
                                )
                            ),
                            dbc.Col(
                                dbc.Collapse(
                                    [
                                        # density range-slider
                                        html.Img(id="reset-dense", src="/assets/x.svg", n_clicks=0, width="content-min",
                                                 style={'width': '1.25em'}),
                                        dcc.RangeSlider(
                                            id='range-slider-dense',
                                            min=min(scatter_df['val']), max=max(scatter_df['val']),
                                            step=round((max(scatter_df['val']) - min(scatter_df['val'])) / 30),
                                            marks=None, tooltip={"placement": "bottom", "always_visible": False},
                                            updatemode='drag', vertical=True, verticalHeight=800
                                        )], style={'width': '2em', 'padding': '7px'}, id="dense-collapse", is_open=False
                                )
                            )
                        ], className='g-0')

                    ]
                ))
            )

            # TODO:
            #  - ability to lock range? (difficult/rechenintensiv)
            #  - top range-marker reverse-pushable??
            #  - one card gets opened->all cards open, just without sliders
            #  - slider max value is x-/y-/z-max-value - 1
            #   - allow direct keyboard input for range sliders?

            # Right side-bar
            r_canvas_sc = html.Div([
                dbc.Offcanvas(r_content_sc, id="offcanvas-r-sc", is_open=True,
                                                 style={'width': '15rem', 'height': 'min-content',
                                                        'margin-top': '2.5vh',
                                                        'margin-right': '0.5vw', 'border-radius': '10px',
                                                        'box-shadow': 'rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px'},
                                                 scrollable=True, backdrop=False, placement='end'),
                dbc.Button("<", id="open-settings-sc", n_clicks=0, style={'margin-top': '40vh', 'margin-left': '0px'})
                                   ], style={'align': 'right'}, id="r_sc")



# THIS ONE:
            '''
            Update sidebar together with c0 in updateScatter
            '''


            # update c0
            return scatter_plot, r_canvas_sc
        elif plots[0] == "volume":
            return volume_plot, r_canvas_sc
        elif plots[0] == "dos":
            return dos_plot, r_canvas_sc




# UPDATING CONTENT-CELL 1
@app.callback(
    Output("mc1", "children"),
    Input("page_state", "data"),
    State("choice_store", "data"),
    State("df_store", "data"),
    prevent_initial_call=True,
)
def updateMC1(state, plots, data):


    if data is None or state == "landing":
        raise PreventUpdate
    elif state == "updated":
        raise PreventUpdate

    elif state == "plotting" and data is not None:
        if len(plots)>1:
            r_canvas_sc = html.Div()
            scale = pd.DataFrame(data['SCALE'])
            # scale['x_axis'][0] = x_axis Voxels // [1] = X-scaling on x // [2] = X-scaling on y // [3] = X-scaling on z
            if plots[1] == "scatter":
                # TODO: extract this into a function which can be called by all three update_mc callbacks
                scatter_df = pd.DataFrame(data['MALA_DF']['scatter'])
                # scatter
                r_content_sc = html.Div(
                    # Idea: draw markers on coord-rangeslider where atoms are
                    dbc.Card(dbc.CardBody(
                        [
                            # Buttonrow
                            dbc.Row([
                                dbc.Col(html.Button('X', id='collapse-x', n_clicks=0, style={'width': '2em'})),
                                dbc.Col(html.Button('Y', id='collapse-y', n_clicks=0, style={'width': '2em'})),
                                dbc.Col(html.Button('Z', id='collapse-z', n_clicks=0, style={'width': '2em'})),
                                dbc.Col(
                                    html.Img(src="assets/dens.png", id='collapse-dense',
                                             style={"width": "1.8em", "height": "1.8em"},
                                             n_clicks=0))
                            ], className='g-0'),
                            # Sliderrow
                            dbc.Row([
                                dbc.Col(
                                    dbc.Collapse(
                                        [
                                            html.Img(id="reset-cs-x", src="/assets/x.svg", n_clicks=0,
                                                     style={'width': '1.25em'}),
                                            dcc.RangeSlider(id='range-slider-cs-x', min=min(scatter_df['x']),
                                                            max=max(scatter_df['x']),
                                                            marks=None,
                                                            tooltip={"placement": "bottom", "always_visible": False},
                                                            updatemode='drag', vertical=True, verticalHeight=800,
                                                            pushable=scale['x_axis'][1])
                                        ], style={'padding': '8px', 'width': '2em'}, id="x-collapse", is_open=False
                                    )
                                ),
                                dbc.Col(
                                    dbc.Collapse(
                                        [
                                            html.Img(id="reset-cs-y", src="/assets/x.svg", n_clicks=0,
                                                     style={'width': '1.25em'}),
                                            dcc.RangeSlider(
                                                id='range-slider-cs-y',
                                                min=min(scatter_df['y']), max=max(scatter_df['y']),
                                                marks=None, tooltip={"placement": "bottom", "always_visible": False},
                                                updatemode='drag', vertical=True, verticalHeight=800,
                                                pushable=scale['y_axis'][2])],
                                        style={'padding': '7px', 'width': '2em'}, id="y-collapse", is_open=False
                                    )
                                ),
                                dbc.Col(
                                    dbc.Collapse(
                                        [
                                            html.Img(id="reset-cs-z", src="/assets/x.svg", n_clicks=0,
                                                     style={'width': '1.25em'}),
                                            dcc.RangeSlider(
                                                id='range-slider-cs-z',
                                                min=min(scatter_df['z']), max=max(scatter_df['z']),
                                                marks=None, tooltip={"placement": "bottom", "always_visible": False},
                                                updatemode='drag', vertical=True, verticalHeight=800,
                                                pushable=scale['z_axis'][3])],
                                        style={'padding': '7px', 'width': '2em'}, id="z-collapse", is_open=False
                                    )
                                ),
                                dbc.Col(
                                    dbc.Collapse(
                                        [
                                            # density range-slider
                                            html.Img(id="reset-dense", src="/assets/x.svg", n_clicks=0,
                                                     width="content-min",
                                                     style={'width': '1.25em'}),
                                            dcc.RangeSlider(
                                                id='range-slider-dense',
                                                min=min(scatter_df['val']), max=max(scatter_df['val']),
                                                step=round((max(scatter_df['val']) - min(scatter_df['val'])) / 30),
                                                marks=None, tooltip={"placement": "bottom", "always_visible": False},
                                                updatemode='drag', vertical=True, verticalHeight=800
                                            )], style={'width': '2em', 'padding': '7px'}, id="dense-collapse",
                                        is_open=False
                                    )
                                )
                            ], className='g-0')

                        ]
                    ))
                )

                # TODO:
                #  - ability to lock range? (difficult/rechenintensiv)
                #  - top range-marker reverse-pushable??
                #  - one card gets opened->all cards open, just without sliders
                #  - slider max value is x-/y-/z-max-value - 1
                #   - allow direct keyboard input for range sliders?

                # Right side-bar
                r_canvas_sc = html.Div([
                    dbc.Offcanvas(r_content_sc, id="offcanvas-r-sc", is_open=True,
                                  style={'width': '15rem', 'height': 'min-content',
                                         'margin-top': '2.5vh',
                                         'margin-right': '0.5vw', 'border-radius': '10px',
                                         'box-shadow': 'rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px'},
                                  scrollable=True, backdrop=False, placement='end'),
                    dbc.Button("<", id="open-settings-sc", n_clicks=0,
                               style={'margin-top': '40vh', 'margin-left': '0px'})
                ], style={'align': 'right'}, id="r_sc")

                # THIS ONE:
                '''
                Update sidebar together with c0 in updateScatter
                '''

                # update c0
                return scatter_plot, r_canvas_sc
            elif plots[1] == "volume":
                return volume_plot
            elif plots[1] == "dos":
                return dos_plot



# UPDATING CONTENT-CELL 1
@app.callback(
    Output("mc2", "children"),
    Input("page_state", "data"),
    State("choice_store", "data"),
    prevent_initial_call=True,
)
def updateMC2(state, plots):
    if plots is not None and len(plots) > 2:
        if state == "landing":
            return html.Div()
        elif state == "uploaded":
            return html.Div()
        elif state == "plotting":
            if plots[2] == "scatter":
                return scatter_plot
            elif plots[2] == "volume":
                return volume_plot
            elif plots[2] == "dos":
                return dos_plot
    else:
        return html.Div()




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
            return None

# pretty sure this is never triggered
@app.callback(
    Output("r_canvas_rc", "children"),
    Input("df_store", "data"),
    prevent_initial_call=True,
)
def updateRightSideSC(data):
    # Right sidebar CONTENT        -       Options
    print("Updating right side canvas")
    scatter_df = pd.DataFrame(data['MALA_DF']['scatter'])
    scale = pd.DataFrame(data['SCALE'])
    x_axis = scale['x_axis']
    y_axis = scale['y_axis']
    z_axis = scale['z_axis']

    # scatter
    # TODO: give default-values instead of the dfs-values and update these values in updateScatter-callback
    r_content_sc = html.Div(
        # Idea: draw markers on coord-rangeslider where atoms are
        dbc.Card(dbc.CardBody(
            [
                # Buttonrow
                dbc.Row([
                    dbc.Col(html.Button('X', id='collapse-x', n_clicks=0, style={'width': '2em'})),
                    dbc.Col(html.Button('Y', id='collapse-y', n_clicks=0, style={'width': '2em'})),
                    dbc.Col(html.Button('Z', id='collapse-z', n_clicks=0, style={'width': '2em'})),
                    dbc.Col(
                        html.Img(src="assets/dens.png", id='collapse-dense',
                                 style={"width": "1.8em", "height": "1.8em"},
                                 n_clicks=0))
                ], className='g-0'),
                # Sliderrow
                dbc.Row([
                    dbc.Col(
                        dbc.Collapse(
                            [
                                html.Img(id="reset-cs-x", src="/assets/x.svg", n_clicks=0, style={'width': '1.25em'}),
                                dcc.RangeSlider(id='range-slider-cs-x', min=min(scatter_df['x']),
                                                max=max(scatter_df['x']),
                                                marks=None, tooltip={"placement": "bottom", "always_visible": False},
                                                updatemode='drag', vertical=True, verticalHeight=800,
                                                pushable=x_axis[1])
                            ], style={'padding': '8px', 'width': '2em'}, id="x-collapse", is_open=False
                        )
                    ),
                    dbc.Col(
                        dbc.Collapse(
                            [
                                html.Img(id="reset-cs-y", src="/assets/x.svg", n_clicks=0, style={'width': '1.25em'}),
                                dcc.RangeSlider(
                                    id='range-slider-cs-y',
                                    min=min(scatter_df['y']), max=max(scatter_df['y']),
                                    marks=None, tooltip={"placement": "bottom", "always_visible": False},
                                    updatemode='drag', vertical=True, verticalHeight=800, pushable=y_axis[2])],
                            style={'padding': '7px', 'width': '2em'}, id="y-collapse", is_open=False
                        )
                    ),
                    dbc.Col(
                        dbc.Collapse(
                            [
                                html.Img(id="reset-cs-z", src="/assets/x.svg", n_clicks=0, style={'width': '1.25em'}),
                                dcc.RangeSlider(
                                    id='range-slider-cs-z',
                                    min=min(scatter_df['z']), max=max(scatter_df['z']),
                                    marks=None, tooltip={"placement": "bottom", "always_visible": False},
                                    updatemode='drag', vertical=True, verticalHeight=800, pushable=z_axis[3])],
                            style={'padding': '7px', 'width': '2em'}, id="z-collapse", is_open=False
                        )
                    ),
                    dbc.Col(
                        dbc.Collapse(
                            [
                                # density range-slider
                                html.Img(id="reset-dense", src="/assets/x.svg", n_clicks=0, width="content-min",
                                         style={'width': '1.25em'}),
                                dcc.RangeSlider(
                                    id='range-slider-dense',
                                    min=min(scatter_df['val']), max=max(scatter_df['val']),
                                    step=round((max(scatter_df['val']) - min(scatter_df['val'])) / 30),
                                    marks=None, tooltip={"placement": "bottom", "always_visible": False},
                                    updatemode='drag', vertical=True, verticalHeight=800
                                )], style={'width': '2em', 'padding': '7px'}, id="dense-collapse", is_open=False
                        )
                    )
                ], className='g-0')

            ]
        ))
    )

    # TODO:
    #  - ability to lock range? (difficult/rechenintensiv)
    #  - top range-marker reverse-pushable??
    #  - one card gets opened->all cards open, just without sliders
    #  - slider max value is x-/y-/z-max-value - 1
    #   - allow direct keyboard input for range sliders?

    # Right side-bar
    sc_canv_upd = html.Div(dbc.Offcanvas(r_content_sc, id="offcanvas-r-sc", is_open=True,
                                         style={'width': '15rem', 'height': 'min-content', 'margin-top': '2.5vh',
                                                'margin-right': '0.5vw', 'border-radius': '10px',
                                                'box-shadow': 'rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px'},
                                         scrollable=True, backdrop=False, placement='end'), id="l_sc")
    print("????????")
    return sc_canv_upd

@app.callback(
    Output("scatter-plot", "figure"),
    [Input("range-slider-dense", "value"),
     Input("dense-collapse", "is_open"),
     Input("range-slider-cs-x", "value"),
     Input("x-collapse", "is_open"),
     Input("range-slider-cs-y", "value"),
     Input("y-collapse", "is_open"),
     Input("range-slider-cs-z", "value"),
     Input("z-collapse", "is_open"),
     Input("size-slider", 'value'),
     Input("opacity-slider", 'value'),
     Input("outline-check", 'value'),
     Input("scatter-atoms", "value"),
     State("cam_store", "data"),
     State("df_store", "data"),
     Input("default-cam", "n_clicks"),
     Input("x-y-cam", "n_clicks"),
     Input("x-z-cam", "n_clicks"),
     Input("y-z-cam", "n_clicks"),
     ],
    [State("scatter-plot", "relayoutData"),
     State("scatter-plot", "figure")],
    prevent_initial_call=True,
)
def updateScatter(slider_range, dense_active, slider_range_cs_x, cs_x_active, slider_range_cs_y, cs_y_active,
                  slider_range_cs_z, cs_z_active, size_slider, opacity_slider, outline, atoms_enabled, stored_cam_settings, f_data,
                  cam_default, cam_xy, cam_xz, cam_yz, relayout_data, fig):
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

    # SETTINGS
        # offcanvas

    # filter-by-density
    if slider_range is not None and dense_active:  # Any slider Input there?
        low, high = slider_range
        mask = (dfu['val'] >= low) & (dfu['val'] <= high)
        dfu = dfu[mask]
    else:
        mask = (dfu['val'] >= min(dfu['val'])) & (dfu['val'] <= max(dfu['val']))
        # TODO: mask could be referenced without being defined
    # x-Cross-section
    if slider_range_cs_x is not None and cs_x_active:  # Any slider Input there?
        low, high = slider_range_cs_x
        mask = (dfu['x'] >= low) & (dfu['x'] <= high)
        dfu = dfu[mask]
    else:
        mask = (dfu['x'] >= min(dfu['x'])) & (dfu['x'] <= max(dfu['x']))
        dfu = dfu[mask]
    # Y-Cross-section
    if slider_range_cs_y is not None and cs_y_active:  # Any slider Input there?
        low, high = slider_range_cs_y
        mask = (dfu['y'] >= low) & (dfu['y'] <= high)
        dfu = dfu[mask]
    else:
        mask = (dfu['y'] >= min(dfu['y'])) & (dfu['y'] <= max(dfu['y']))
        dfu = dfu[mask]
    # Z-Cross-section
    if slider_range_cs_z is not None and cs_z_active:  # Any slider Input there?
        low, high = slider_range_cs_z
        mask = (dfu['z'] >= low) & (dfu['z'] <= high)
        dfu = dfu[mask]
    else:
        mask = (dfu['z'] >= min(dfu['z'])) & (dfu['z'] <= max(dfu['z']))
        dfu = dfu[mask]

        # SETTINGS
        # plot-settings

    # size-slider
    if size_slider is not None:
        marker_size = size_slider
    else:
        marker_size = 12

    # opacity-slider
    # it would be great if we could each point an opacity-value according to it's density-value - seems to be impossible (to do smoothly)
    if opacity_slider is not None:
        opac = opacity_slider
    else:
        opac = 1

    # UPDATING DATASET

    fig_upd = px.scatter_3d(
        dfu, x="x", y="y", z="z",
        color="val",
        hover_data=['val'],
        opacity=opac,
        color_continuous_scale=px.colors.sequential.Inferno_r,
        range_color=[df.min()['val'], df.max()['val']],
        # takes color range from original dataset, so colors don't change
        template=templ1,
    )

    # Default Marker Params Scatter Plot
    fig_upd.update_traces(default_scatter_marker)

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

    # Outline settings
    if outline:
        outlined = dict(width=1, color='DarkSlateGrey')
    else:
        outlined = dict(width=0, color='DarkSlateGrey')

    # WAY TO CHANGE SIZE, OPACITY, OUTLINE
    fig_upd.update_traces(marker=dict(size=marker_size, opacity=opac, line=outlined)
                          , selector=dict(mode='markers'))

    # ADD ATOMS

        # TODO: COLOR-CODING ATOMS BASED OFF THEIR CHARGE
    if True in atoms_enabled:
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
        #Input("range-slider-cs-x", "value"),
        #Input("x-collapse", "is_open"),
        #Input("range-slider-cs-y", "value"),
        #Input("y-collapse", "is_open"),
        #Input("range-slider-cs-z", "value"),
        #Input("z-collapse", "is_open"),
        #Input("opacity-slider", 'value'),
        #Input("scatter-atoms", "value")
        Input("cam_store_v", "data"),
        State("df_store", "data"),
    ],
    [State("volume-plot", "relayoutData")],
    prevent_initial_call=True
)
def updateVolume(stored_cam_settings, f_data, relayout_data):
    if f_data is None:
        raise PreventUpdate
    dfu = pd.DataFrame(f_data['MALA_DF']['volume'])
    atoms = pd.DataFrame(f_data['INPUT_DF'])
    no_of_atoms = len(atoms)

    atoms_enabled = [True]        # as long as volume doesn't have it's own settings yet
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
    # HIER CAMERA VON SCRATCH.PY ODER SCATTER_UPDATE EINFÜGEN
    # <----------------------------------------------------->

    return fig_upd
# END OF CALLBACKS FOR VOLUME PLOT

# TODO: updateDoS


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
def toggle_offcanvas_r(n1, is_open):
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
