# IMPORTS
from collections import Counter

from pprint import pprint

import mala_inference
import ase.io
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table


import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

# visualization
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go

# to print whole arrays
np.set_printoptions(threshold=np.inf)

print("_________________________________________________________________________________________")
print("STARTING UP...")

# (a) GET (most) DATA FROM MALA (/ inference script)
bandEn = mala_inference.results['band_energy']
totalEn = mala_inference.results['total_energy']
density = mala_inference.results['density']
dOs = mala_inference.results['density_of_states']
enGrid = mala_inference.results['energy_grid']

# (b) GET ATOMPOSITION & AXIS SCALING FROM .cube CREATED BY MALA (located where 'mala-inference-script' is located
atomData = '/home/maxyyy/PycharmProjects/mala/app/Be2_density.cube'

# 0-1 = Comment, Energy, broadening     //      2 = number of atoms, coord origin
# 3-5 = number of voxels per Axis (x/y/z), lentgh of axis-vector -> info on cell-warping
# 6-x = atompositions
atoms = [[], [], [], [], []]

with open(atomData, 'r') as f:
    lines = f.read().splitlines()
    no_of_atoms, _, _, _ = lines[2].split()

    # AXIS-SCALING-FACTOR
    # axis-List-Format: voxelcount[0]   X-Scale[1]     Y-Scale[2]     Z-Scale[3]
    x_axis = [float(i) for i in lines[3].split()]
    y_axis = [float(i) for i in lines[4].split()]
    z_axis = [float(i) for i in lines[5].split()]

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

print("DATA IMPORT COMPLETE")
print("_________________________________________________________________________________________")

# Formatting + shearing Data
# density- import / conversion to pandas dataframe / fig - density-visualisation params / plot-layout params


# (a)
coord_arr = np.column_stack(
    list(map(np.ravel, np.meshgrid(*map(np.arange, density.shape), indexing="ij"))) + [density.ravel()])

# (b) SCALING to right voxel-size
df = pd.DataFrame(coord_arr, columns=['x', 'y', 'z', 'val'])
df['x'] *= x_axis[1]
df['y'] *= y_axis[2]
df['z'] *= z_axis[3]

scatter_df = df.copy()  # important to keep / save df as kartesian coordinates:
# they are used to calculate/scale shearing "factor" (actually summand)
# used for unsheared x-values for go.Volume


# SHEARING für scatter_3d
scatter_df.x += y_axis[1] * (df.y / y_axis[2])
scatter_df.x += z_axis[1] * (df.z / z_axis[3])

scatter_df.y += x_axis[2] * (df.x / x_axis[1])
scatter_df.y += z_axis[2] * (df.z / z_axis[3])

scatter_df.z += y_axis[3] * (df.y / y_axis[2])
scatter_df.z += x_axis[3] * (df.x / x_axis[1])

'''
(a) np columns coord_arr, each entry containing  a single coord
    - f.e. [x_val, y_val, z_val, dens_val]
    - count-order: z -> y -> x
        --> this is the order needed for scatter_3d
(b) SCATTER_3D-PLOT:
- fills the Dataframe for scatter_3D-rendering with integer coordinates and according density values
    - df['x'] / df['y'] / df['z'] / df['val']
- scales each x-/y-/z-column according to THAT axis' unit-vector

(c) VOLUME-PLOT

'''

# (c) DATA für Volume

#   Daten für Tabelle und vol_fig!!!)
volume_DF = pd.DataFrame(data={'x': df.x, 'y': scatter_df.y, 'z': scatter_df.z, 'val': df.val})

# SHEAR (as volume issues are fixed -  these will be deprecated
# --> one DF for all

# volume_DF.x += y_axis[1] * (df.y / y_axis[2])
# volume_DF.x += z_axis[1] * (df.z / z_axis[3])

volume_DF.y += x_axis[2] * (df.x / x_axis[1])
volume_DF.y += z_axis[2] * (df.z / z_axis[3])

volume_DF.z += y_axis[3] * (df.y / y_axis[2])
volume_DF.z += x_axis[3] * (df.x / x_axis[1])

# DENSITY OF STATE
dosArr = np.column_stack(list(map(np.ravel, np.meshgrid(*map(np.arange, dOs.shape), indexing="ij"))) + [dOs.ravel()])
dosDf = pd.DataFrame(dosArr, columns=['x', 'y'])
# _____________________________________________________________________________________________________________________


# ATOMPOSITIONS
for i in range(0, int(no_of_atoms)):
    ordinalNumber, charge, x, y, z = lines[6 + i].split()  # atom-data starts @line-index 6
    # atoms-List-Format: ordinalNumber[0]    charge[1]  x[2]   y[3]   z[4]
    atoms[0].append(int(ordinalNumber))
    atoms[1].append(float(charge))
    atoms[2].append(float(x))
    atoms[3].append(float(y))
    atoms[4].append(float(z))
atoms_DF = pd.DataFrame(data={'x': atoms[2], 'y': atoms[3], 'z': atoms[4], 'ordinal': atoms[0], 'charge': atoms[1]})

# _______________________________________________________________________________________

# THEME & FIGUREs
templ = "ggplot2"
load_figure_template(templ)

templ1 = dict(layout=go.Layout(
    title_font=dict(family="Rockwell", size=24),
))

# relative color-scale, oder absolute Werte? Wenn letzteres: Welche Werte?
# df.max()-Wert in color-range etwas reduzieren (0.01), weil er dem Dichtewert für Atome entspricht.
# So ist Farbauflösung leicht reduziert und alles ist etwas heller

# DENSITY-FIG
fig1 = px.scatter_3d(
    scatter_df,
    x='x',
    y='y',
    z='z',
    color='val',
    color_continuous_scale=px.colors.sequential.Inferno_r,
    range_color=[df.min()['val'], df.max()['val']],
    template=templ1)

'''
# TODO: 10 verschiedene Traces für 10 verschieden Kugelgrößen und Deckkraft -> Koordinaten-Dichte in 10 Stufen rastern
    #  man könnte vlt auch Ebene für Ebene als trace hinzufügen und somit shearing erreichen, aber das wird langsam
    #
    )],
    layout={'uirevision': 'range_slider'}
)
'''

# ATOMS-FIG
# TODO: Atom color dependant on charge
fig1.add_trace(
    go.Scatter3d(x=atoms_DF['x'], y=atoms_DF['y'], z=atoms_DF['z'], mode='markers',
                 marker=dict(size=30, color=['black', 'black'])))

# SCATTER CAMERA
camera_params = dict(
    up=dict(x=0, y=0, z=1),
    center=dict(x=0, y=0, z=0),
    eye=dict(x=1.5, y=1.5, z=1.5)
)
# fig1.update_layout(scene_camera=camera_params)
# Default Marker Params Scatter Plot
fig1.update_traces(marker=dict(
    size=12,
    opacity=1,
    line=dict(width=1, color='DarkSlateGrey')),
    selector=dict(mode='markers'))
# END

# SCATTER GRID PROPERTIES
# (cam can be edited here aswell!)
fig1.update_scenes(xaxis_showgrid=False, yaxis_showgrid=False, zaxis_showgrid=False, camera=camera_params)
# https://plotly.com/python/reference/layout/scene/


# VOLUME-FIG - WORK IN PROGRESS
vol_fig = go.Figure(data=go.Volume(
    x=volume_DF.x,
    y=volume_DF.y,
    z=volume_DF.z,
    value=volume_DF.val,
    opacity=0.3,
    surface_count=17,
    colorscale=px.colors.sequential.Inferno_r
))

# TODO: Could get constant grid-size by drawing maximum vertices invisible

# TODO: Opacityscale
# opacityscale=[[0, 0.1], [max(df['val']), 1]]


# DoS-Fig
dos_fig = go.Figure()
dos_fig.add_trace(
    go.Scatter(x=dosDf['x'], y=dosDf['y'], name='densityOfstate', line=dict(color='#f15e64', width=3, dash='dot')))

plot_layout = {
    'title': 'Test',
    'height': '55vh',
    'width': '55vw',
    'background': '#000',  # not working
}

dos_plot_layout = {
    'height': '400px',
    'width': '800px',
    'background': '#f8f9fa',
}

print("FIGURES LOADED")
print("_________________________________________________________________________________________")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR, dbc.icons.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = 'MALA'

# TABLE SECTION


indent = '      '
# Data
row1 = html.Tr([html.Td(indent.join("Band - Energy"), style={'text-align': 'center'})], style={"font-weight": "bold"})
row2 = html.Tr([html.Td(bandEn, style={'text-align': 'right'})])
row3 = html.Tr([html.Td(indent.join("Total - Energy"), style={'text-align': 'center'})], style={"font-weight": "bold"})
row4 = html.Tr([html.Td(totalEn, style={'text-align': 'right'})])
row5 = html.Tr([html.Td(indent.join("Fermi - Energy"), style={'text-align': 'center'})], style={"font-weight": "bold"})
row6 = html.Tr([html.Td("placeholder", style={'text-align': 'right'})])
table_body = [html.Tbody([row1, row2, row3, row4, row5, row6])]

# ----------------


# SIDEBAR
sidebar = html.Div(

    [
        # upper sidebar
        html.Div(
            [
                # Logo Section
                html.Div([
                    html.Img(src='https://avatars.githubusercontent.com/u/81354661?s=200&v=4', className="logo"),
                    html.H2(children='MALA', style={'text-align': 'center'}),
                    html.Div(children='''
        Framework for machine learning materials properties from first-principles data.
    ''', style={'text-align': 'center'})], className="logo"),

                html.Hr(style={'margin-bottom': '2rem', 'margin-top': '2rem'}),

                # Upload Section
                html.Div([
                    html.H5(children='File-Upload'),

                    # maybe do as info-on-hover
                    html.Div(children='''
                MALA needs Atompositions
                ''', style={'text-align': 'center'}),

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
                            'margin': '0.5rem',
                        },
                        # Allow multiple files to be uploaded
                        multiple=False
                    ),

                ], className="upload-section"),

                html.Hr(style={'margin-bottom': '2rem', 'margin-top': '2rem'}),

                # Status section
                html.Div([
                    html.H5(children='Status'),
                    html.Div(children='''
                Awaiting Data Input
                ''', style={'text-align': 'left'}),

                    html.Div(id='output-upload-state', style={'margin': '10px'})
                ], className="status-section"),

                html.Hr(style={'margin-bottom': '2rem'}),

                # Plot Display Settings
                html.H5(children='Plot Settings'),

                html.Div(children=dcc.Dropdown(
                    {'scatter': 'Scatter', 'volume': 'Volume', 'dos': 'DoS'}, multi=True,
                    id='plot-choice', placeholder='Choose Plot Type', persistence=True
                ),
                ),

            ],
            className="sidebar",
            style={
                'top': '5vh',
                'left': 0,
                'bottom': 0,
                'width': '15rem',
                'padding': '2rem 1rem',
                'background-color': '#f8f9fa',
                'border-radius': '10px',
                'height': 'min-content',
                'box-shadow': 'rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px'
            },
        ),
        # Energy-Table
        html.Div([
            html.H4(indent.join('Value Table'), style={'margin-top': '2rem'}),
            dbc.Card(dbc.CardBody(html.Div(
                dbc.Table(table_body, bordered=True, striped=True)
            )), style={'background-color': 'rgba(248, 249, 250, 1)', 'width': '15em', 'float': 'left'},
            )
        ], style={'height': 'min-content'}),

    ], style={'margin-top': '5vh'}
)
# __________________________________________________________________________________________________

# Right side content        -       settings
# scatter
r_content_sc = html.Div(
    [
        # Crosssection Settings
        dbc.Card([
            html.Button('X', id='collapse-x', n_clicks=0, style={'width': '2em'}),

            dbc.Collapse(
                dbc.Card(dbc.CardBody(
                    [
                    html.I(className="bi bi-x"),        # why not working????
                    dcc.RangeSlider(  # TODO: allow direct keyboard input
                        id='range-slider-cs-x',
                        min=min(scatter_df['x']), max=max(scatter_df['x']),
                        marks=None, tooltip={"placement": "bottom", "always_visible": False},
                        updatemode='drag', vertical=True, verticalHeight=800, pushable=x_axis[1])
                    ], style={'padding': '7px'}

                )),
                id="x-collapse",
                is_open=False),
        ], style={'width': '2em'}),
        dbc.Card([
            html.Button('Y', id='collapse-y', n_clicks=0, style={'width': '2em'}),

            dbc.Collapse(
                dbc.Card(dbc.CardBody(
                    dcc.RangeSlider(  # TODO: allow direct keyboard input
                        id='range-slider-cs-y',
                        min=min(scatter_df['y']), max=max(scatter_df['y']),
                        marks=None, tooltip={"placement": "bottom", "always_visible": False},
                        updatemode='drag', vertical=True, verticalHeight=800,  pushable=y_axis[2]), style={'padding': '7px'})),
                id="y-collapse",
                is_open=False),
        ], style={'width': '2em'}),
        dbc.Card([
            html.Button('Z', id='collapse-z', n_clicks=0, style={'width': '2em'}),

            dbc.Collapse(dbc.Card(dbc.CardBody(
                dcc.RangeSlider(  # TODO: allow direct keyboard input
                    id='range-slider-cs-z',
                    min=min(scatter_df['z']), max=max(scatter_df['z']),
                    marks=None, tooltip={"placement": "bottom", "always_visible": False},
                    updatemode='drag', vertical=True, verticalHeight=800,  pushable=z_axis[3]), style={'padding': '7px'})),
                id="z-collapse",
                is_open=False)
        ], style={'width': '2em'})
    ], style={"display": "flex", 'margin-top': '5vh'}
)
# TODO:
#  - ability to lock range
#  - top range-marker pushable??
#  - one card gets opened->all cards open, just without sliders
#  - slider max value is x-/y-/z-max-value - 1
# __________________________________________________________________________________________________

# MAIN CONTENT / PLOT

load_figure_template("quartz")

# column 2 PRE UPLOAD
default_main = html.Div(
    dbc.Col(
        [
            html.H1([indent.join('Welcome To MALA')], style={'text-align': 'center', 'width': '10em'}),
            html.Div(children=['''
             Upload a .cube-File for MALA to process
            '''], style={'margin-top': '25vh'}),
        ]), style={"width": "min-content"})


default_main2 = html.Div(
    dbc.Col(
        [

        ]))

# column 2 POST UPLOAD
uploaded_main = html.Div([
                    html.H1("Upload Successful", style={'text-align': 'center', 'color': '#3da839'}),
                    html.Div(children=['''
                     Choose the Type of plot
                    '''], style={'margin-top': '30vh'}),
                ], style={"width": "66vw"})
uploaded_main2 = html.Div()

# column 2 on plotting
# scatter
scatter_plot = html.Div(
    [
        # Plot Section
        html.Div(
            [
                # Density Scatter opacity Section
                html.H3([indent.join('3D-Density-Plot'), ' (scatter)'], style={'margin-top': '1.5rem'}),
                dbc.Card(dbc.CardBody(
                    [html.Div(
                        dcc.Graph(id="scatter-plot", figure=fig1, style=plot_layout),
                        className="density-scatter-plot"
                    ),
                        html.Hr(style={'margin-bottom': '2rem', 'margin-top': '2rem'}),
                        dbc.Button("Settings", id="open-sc-settings", n_clicks=0),
                        dbc.Collapse(
                            dbc.Card(dbc.CardBody(
                            [
                                html.H5("Filter by density"),
                                dcc.RangeSlider(  # TODO: allow direct keyboard input
                                id='range-slider',
                                min=min(scatter_df['val']), max=max(scatter_df['val']),
                                step=round((max(scatter_df['val']) - min(scatter_df['val'])) / 30),
                                marks=None, tooltip={"placement": "bottom", "always_visible": False},
                                updatemode='drag'
                                ),
                                html.H5("Size"),
                                dcc.Slider(6, 18, 2, value=12, id='size-slider'),
                                html.H5("Opacity"),
                                dcc.Slider(0.1, 1, 0.1, value=1, id='opacity-slider'),
                                dcc.Checklist(options=[{'label': '  Outline', 'value': True}], value=[True],
                                              id='outline-check'),
                                html.Div(
                                    dcc.RadioItems(
                                        ['Standard', 'X-Y', 'X-Z', 'Y-Z', 'Custom'],
                                        'Standard',
                                        id='cam-pos',
                                        persistence=False,
                                        inputStyle={"margin-left": "10px", "margin-right": "3px"}
                                    ),
                                ),
                            ]
                        )),
                            id="sc-settings-collapse",
                            is_open=False),


                    ]
                ), style={'background-color': 'rgba(248, 249, 250, 1)', 'width': 'min-content', 'align-content': 'center'}),
            ],
            className="plot-section"
        ),
    ],
    className="content"
)

# volume
volume_plot = html.Div(
    [
        # Plot Section
        html.Div(
            [
                # Density volume Section
                html.H5([indent.join('3D-Density-Plot (volume)')], style={'margin-top': '1.5rem'}),
                dbc.Card(dbc.CardBody(html.Div(
                    dcc.Graph(figure=vol_fig, style=plot_layout),
                    className="density-vol-plot"
                )), style={'background-color': 'rgba(248, 249, 250, 1)', 'width': 'min-content', 'margin-top': '1rem'}),
            ],
            className="plot-section"
        ),
    ],
    className="content",
    # style={'margin-left': '1.5vw'}
)

# DOS (+table)
dos_plot = html.Div(
    [
        # Density of State Section
        html.H4(indent.join('2D-Density-of-State-Plot'), style={'margin-top': '1.5rem'}),
        dbc.Card(dbc.CardBody(html.Div(
            dcc.Graph(figure=dos_fig, style=dos_plot_layout),
            className='dos-plot',
        )),
            style={'position': 'float', 'background-color': 'rgba(248, 249, 250, 1)', 'width': 'min-content',
                   'margin-bottom': '1rem', 'margin-top': '1rem',
                   'box-shadow': 'rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px'}),
    ],
)

# ----------------
# standard layout
app.layout = dbc.Container(
    [
        dbc.Row(  # SCATTER PLOT
            [
                dbc.Col(sidebar, width=2),
                dbc.Col(default_main, width=8),
                dbc.Col(r_content_sc, width=2, style={'align': 'right'}),  # going to be the settings tab
            ],
        ),
        dbc.Row(  # VOLUME PLOT
            [
                dbc.Col(html.Div(), width=2),
                dbc.Col(default_main2, width="auto"),
                dbc.Col(html.Div(), width=2),  # going to be the settings tab
            ]
        ),
        dbc.Row(  # DOF
            [
                dbc.Col(html.Div(), width=2),
                dbc.Col(html.Div(), width=5),  # DOF Plot
                dbc.Col(html.Div(), width=5),
            ]
        )
    ], id="content-layout")

# _____________________________________________________________________________________________________________________
print("COMPONENTS LOADED")
print("_________________________________________________________________________________________")


# -----------------------------------------------------
# CALLBACKS & FUNCTIONS

# collapsable crosssection settings
@app.callback(
    Output("sc-settings-collapse", "is_open"),
    Input("open-sc-settings", "n_clicks"),
    Input("sc-settings-collapse", "is_open")
)
def toggle_sc_settings(n_sc_s, is_open):
    if n_sc_s:
        return not is_open

@app.callback(
    Output("x-collapse", "is_open"),
    Input("collapse-x", "n_clicks"),
    Input("x-collapse", "is_open")
)
def toggle_x_cs(n_x, is_open):
    if n_x:
        return not is_open


@app.callback(
    Output("y-collapse", "is_open"),
    Input("collapse-y", "n_clicks"),
    Input("y-collapse", "is_open")
)
def toggle_x_cs(n_y, is_open):
    if n_y:
        return not is_open


@app.callback(
    Output("z-collapse", "is_open"),
    Input("collapse-z", "n_clicks"),
    Input("z-collapse", "is_open")
)
def toggle_x_cs(n_z, is_open):
    if n_z:
        return not is_open

    # UPDATE VISIBLE CONTENT


@app.callback(
    Output("content-layout", "children"),
    Input("plot-choice", "value")
)
def change_layout(plots):
    mc = [html.Div(), html.Div(), html.Div()]  # main content components
    rc = [html.Div(), html.Div(), html.Div()]  # right side content
    # this one could contain a little guide on how the app works / where to upload / ...
    # each element(component) of mc[] is one centered cell of content

    if len(plots) > 0:
        index = 0
        for choice in plots:
            if choice == "scatter":
                mc[index] = scatter_plot
                rc[index] = r_content_sc
                index += 1
            if choice == "volume":
                mc[index] = volume_plot
                index += 1
            if choice == "dos":
                mc[index] = dos_plot
                index += 1
    else:
        if len(df) == 0:  # df nicht gefüllt = Upload hat noch nicht stattgefunden
            mc[0] = default_main
            mc[1] = default_main2

        if len(df) != 0:  # df gefüllt = Upload hat stattgefunden
            mc[0] = uploaded_main  # zur plotauswahl auffordern
            mc[1] = uploaded_main2
            # File Upload Section durch Plot Settings ersetzen

    # returning new page layout
    return dbc.Container([
        dbc.Row(  # First Plot
            [
                dbc.Col(sidebar, width='auto',
                        style={'background': 'red', 'width': 'min-content', 'height': 'min-content'}),
                dbc.Col(mc[0], width=8,
                        style={'background': 'blue', 'width': 'min-content', 'height': 'min-content'}),
                dbc.Col(rc[0], width='auto', style={'background': 'green'}),  # settings
            ]
        ),

        dbc.Row(  # Second Plot
            [
                dbc.Col(html.Div(), width='auto'),
                dbc.Col(mc[1], width=8),
                dbc.Col(rc[1], width=2),  # gonna be the settings tab
            ]
        ),
        dbc.Row(  # Third Plot
            [
                dbc.Col(html.Div(), width=2),
                dbc.Col(mc[2], width='auto'),  # DOF Plot
                dbc.Col(rc[2], width=5),
            ]
        )
    ])


# ------------------------------------------------------
@app.callback(  # UPDATE SCATTER PLOT
    Output("scatter-plot", "figure"),
    [Input("range-slider", "value"),
    Input("range-slider-cs-x", "value"),
    Input("x-collapse", "is_open"),
    Input("range-slider-cs-y", "value"),
    Input("y-collapse", "is_open"),
    Input("range-slider-cs-z", "value"),
    Input("z-collapse", "is_open"),
    Input("size-slider", 'value'),
    Input("opacity-slider", 'value'),
    Input("outline-check", 'value'),
    Input("cam-pos", 'value')],
    [State("scatter-plot", "relayoutData")])
def update_scatter(slider_range, slider_range_cs_x, cs_x_active, slider_range_cs_y, cs_y_active, slider_range_cs_z, cs_z_active,
                   size_slider, opacity_slider, outline, cam_pos, relayout_data):
    dfu = scatter_df.copy()

    # filter-by-density
    if slider_range is not None:  # Any slider Input there?
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
        mask = (dfu['x'] >= min(scatter_df['x'])) & (dfu['x'] <= max(scatter_df['x']))
        dfu = dfu[mask]
    # Y-Cross-section
    if slider_range_cs_y is not None and cs_y_active:  # Any slider Input there?
        low, high = slider_range_cs_y
        mask = (dfu['y'] >= low) & (dfu['y'] <= high)
        dfu = dfu[mask]
    else:
        mask = (dfu['y'] >= min(scatter_df['y'])) & (dfu['y'] <= max(scatter_df['y']))
        dfu = dfu[mask]
    # Z-Cross-section
    if slider_range_cs_z is not None and cs_z_active:  # Any slider Input there?
        low, high = slider_range_cs_z
        mask = (dfu['z'] >= low) & (dfu['z'] <= high)
        dfu = dfu[mask]
    else:
        mask = (dfu['z'] >= min(scatter_df['z'])) & (dfu['z'] <= max(scatter_df['z']))
        dfu = dfu[mask]

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
        dfu[mask], x="x", y="y", z="z",
        color="val",
        hover_data=['val'],
        opacity=opac,
        color_continuous_scale=px.colors.sequential.Inferno_r,
        range_color=[df.min()['val'], df.max()['val']],
        # takes color range from original dataset, so colors don't change
        template=templ1,
    )

    def cam_lock(cam_user_in):
        if cam_user_in == "Standard":
            fig_upd.update_layout(scene_camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=1.5, y=1.5, z=1.5)
            ))
        elif cam_user_in == "X-Y":
            fig_upd.update_layout(scene_camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=0, y=0, z=3.00)
            ))
        elif cam_user_in == "X-Z":
            fig_upd.update_layout(scene_camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=0, y=3.00, z=0)
            ))
        elif cam_user_in == "Y-Z":
            fig_upd.update_layout(scene_camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=3.00, y=0, z=0))
            )

# TODO: wenn kamera bewegt wird, Kamerasettings auf 5. RadioButton ("Custom") setzen -> Input/State relayout_data auch für RadioItems
# add custom value for camera position set by user
# radio needs a custom option then

    if relayout_data is not None:       # no user input has been made
        if "scene.camera" in relayout_data:
            # custom re-layout cam settings
            fig_upd.update_layout(scene_camera=relayout_data['scene.camera'])
        else:
            # locked cam settings
            cam_lock(cam_pos)


    # Outline settings
    if outline:
        outlined = dict(width=1, color='DarkSlateGrey')
    else:
        outlined = dict(width=0, color='DarkSlateGrey')

    # WAY TO CHANGE SIZE, OPACITY, OUTLINE
    fig_upd.update_traces(marker=dict(size=marker_size, opacity=opac, line=outlined)
                          , selector=dict(mode='markers'))
    # Atoms-Fig
    fig_upd.add_trace(
        go.Scatter3d(x=atoms[2], y=atoms[3], z=atoms[4], mode='markers',
                     marker=dict(size=30, color=['black', 'black'])))

    return fig_upd


@app.callback(  # FILE-UPLOAD
    Output('output-upload-state', 'children'),
    [Input('upload-data', 'filename'),
     Input('upload-data', 'contents'), ]
)
def uploadInput(filename, contents):
    # checks for .cubes for now, as long as im working on vis
    # will check for .npy when mala is ready to give .cube output from
    # is this enough input-sanitization or proper type-check needed?
    # upload component also has accept property to allow only certain types - might be better
    if filename is not None:
        if filename.endswith('.cube'):

            # USER INPUT ATOM POSITIONS - .cube File Upload
            # 1. File Upload of .cube File
            # 2. TODO: parse file with ASE
            # ase.io.read(contents)
            # 3. process with MALA
            # DONE:
            # receiving MALA Input (from script for now)
            # 4. contents

            return 'Upload successful. Filename: {filename}'.format(filename=filename)
        else:
            return 'Wrong file-type. .cube required'
    else:
        return ''


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
