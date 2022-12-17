# IMPORTS

import mala_inference
import ase.io
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table

import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash.exceptions import PreventUpdate

# visualization
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go

# TODO:
#  ----------------------------------------------------------
#                       LANDING STATE
#  ----------------------------------------------------------

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



# TODO: run the following, IF page_state = uploaded; triggered page_state update
#  ----------------------------------------------------------
#                       UPLOADED STATE
#  ----------------------------------------------------------



print("_________________________________________________________________________________________")
print("STARTING UP...")

    # TODO: (optional) ability to en-/disable individual Atoms (that are in the uploaded file) and let MALA recalculate
    #  -> helps see each Atoms' impact in the grid

# (a) GET (most) DATA FROM MALA (/ inference script)
mala_data = mala_inference.results
bandEn = mala_data['band_energy']
totalEn = mala_data['total_energy']
density = mala_data['density']
dOs = mala_data['density_of_states']
enGrid = mala_data['energy_grid']

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
df = pd.DataFrame(coord_arr, columns=['x', 'y', 'z', 'val'])

# (b) SCALING to right voxel-size
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

#   Data table and vol_fig!!!)
volume_DF = pd.DataFrame(data={'x': df.x, 'y': scatter_df.y, 'z': scatter_df.z, 'val': df.val})

# SHEAR (as volume issues are fixed -  these might be deprecated ?
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

# DECIDING ON ATOM-COLOR BASEd OFF THEIR CHARGE TODO
atom_colors = []
for i in range(0, int(no_of_atoms)):
    if atoms[1][i] == 4.0:
        atom_colors.append("black")
    else:
        atom_colors.append("white")




# VOLUME-FIG - WORK IN PROGRESS
vol_fig = go.Figure(data=go.Volume(
    x=volume_DF.x,
    y=volume_DF.y,
    z=volume_DF.z,
    value=volume_DF.val,
    opacity=0.3,
    surface_count=17,
    colorscale=px.colors.sequential.Inferno_r,
    cauto=True
))

# TODO: Could get constant grid-size by drawing maximum vertices as invisible
# i think there was a property for disabling auto-resize

# DoS-Fig
dos_fig = go.Figure()
dos_fig.add_trace(
    go.Scatter(x=dosDf['x'], y=dosDf['y'], name='densityOfstate', line=dict(color='#f15e64', width=3, dash='dot')))









print("FIGURES LOADED")
print("_________________________________________________________________________________________")

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
row2 = html.Tr([html.Td(bandEn, style={'text-align': 'right'})])
row3 = html.Tr([html.Td(indent.join("Total - Energy"), style={'text-align': 'center'})], style={"font-weight": "bold"})
row4 = html.Tr([html.Td(totalEn, style={'text-align': 'right'})])
row5 = html.Tr([html.Td(indent.join("Fermi - Energy"), style={'text-align': 'center'})], style={"font-weight": "bold"})
row6 = html.Tr([html.Td("placeholder", style={'text-align': 'right'})])
table_body = [html.Tbody([row1, row2, row3, row4, row5, row6])]

# ----------------
# Left SIDEBAR
# START (or data reset)
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

                dbc.Card(html.H5(children='File-Upload', style={'margin': '5px'}, id="open-upload", n_clicks=0),
                         style={"text-align": "center"}),

                dbc.Collapse(
                            dbc.Card(dbc.CardBody(# Upload Section
                                html.Div([

                    html.Div(children='''
                            Upload atompositions via .cube! (later npy)
                            ''', style={'text-align': 'center'}),
                    # TODO: make this give dynamic promts (like "choose a plot!")
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
                        dbc.Col(html.Div(id='output-upload-state', style={'margin': '2px'}), style={'text-align': 'center'}, width=8)
                    ])

                ], className="upload-section"),)),
                            id="collapse-upload",
                            is_open=True,
                            style={'margin-bottom': '15px'}
                        ),

                dbc.Card(html.H5(children='Choose Plot Style', style={'margin': '5px'}, id="open-plot-choice", n_clicks=0),
                         style={"text-align": "center"}),

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

sidebar_uploaded = html.Div(
    dbc.Offcanvas(
        # uploaded sidebar
        html.Div(
            [
                dbc.Button("Reupload data", id="reset-data"),
                html.Hr(style={'margin-bottom': '2rem'}),
                # Plot Chooser
                html.H5(children='Choose Plots'),
                html.Div(children=dcc.Dropdown(
                    {'scatter': 'Scatter', 'volume': 'Volume', 'dos': 'DoS'}, multi=True,
                    id='plot-choice', placeholder='Choose Plot Type', persistence=True)),
                html.Hr(style={'margin-bottom': '2rem'}),
                html.H5(children='Values'),
                dbc.Table(table_body, bordered=True, striped=True)

            ], className="sidebar"
        ), id="offcanvas-l", is_open=True, scrollable=True, backdrop=False,
        style={'width': '15rem', 'margin-top': '1.5rem', 'margin-left': '0.5vw', 'border-radius': '10px',
               'height': 'min-content',
               'box-shadow': 'rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px'},
    ),
)
sidebar_uploaded = sidebar
# __________________________________________________________________________________________________

# Right sidebar CONTENT        -       Options

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
                    html.Img(src="assets/dens.png", id='collapse-dense', style={"width": "1.8em", "height": "1.8em"},
                             n_clicks=0))
            ], className='g-0'),
            # Sliderrow
            dbc.Row([
                dbc.Col(
                    dbc.Collapse(
                        [
                            html.Img(id="reset-cs-x", src="/assets/x.svg", n_clicks=0, style={'width': '1.25em'}),
                            dcc.RangeSlider(id='range-slider-cs-x', min=min(scatter_df['x']), max=max(scatter_df['x']),
                                            marks=None, tooltip={"placement": "bottom", "always_visible": False},
                                            updatemode='drag', vertical=True, verticalHeight=800, pushable=x_axis[1])
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
r_canvas_sc = html.Div(dbc.Offcanvas(r_content_sc, id="offcanvas-r-sc", is_open=True,
                                     style={'width': '15rem', 'height': 'min-content', 'margin-top': '2.5vh',
                                            'margin-right': '0.5vw', 'border-radius': '10px',
                                            'box-shadow': 'rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px'},
                                     scrollable=True, backdrop=False, placement='end'))

# __________________________________________________________________________________________________

# MAIN CONTENT / PLOT

# column 2 | PRE UPLOAD
default_main = html.Div([
    html.Div([html.H1([indent.join('Welcome')], className='greetings', style={'text-align': 'center', 'width': '10em'}),
              html.H1([indent.join('To')], className='greetings', style={'text-align': 'center', 'width': '10em'}),
              html.H1([indent.join('MALA')], className='greetings', style={'text-align': 'center', 'width': '10em'}),
              html.Div('Upload a .cube-File for MALA to process', )],
             style={'text-align': 'center', 'margin-left': '1vw'}),
], style={'width': 'content-min', 'margin-top': '20vh'})
default_main2 = html.Div(html.Div(), style={'width': '200px', 'height': '200px', 'color': '#fff'})

# column 2 | UPLOAD SUCCESS
uploaded_main = html.Div([
    html.H1("Upload Successful", style={'margin-top': '30vh', 'margin-left': '15vw', 'color': '#3da839'}),
    html.Div(children=['''
                     Choose the Type of plot
                    '''], style={'margin-top': '5vh', 'margin-left': '5vw'}),
], style={"width": "66vw"})
uploaded_main2 = html.Div()

# column 2 | PLOT(S) CHOSEN
# SCATTER
sc_fig = go.Figure()
scatter_plot = html.Div(
    [
        # Plot Section
        html.Div(
            [
                html.H3([indent.join('3D-Density-Plot'), ' (scatter)'], style={'color': 'white', 'margin-top': '1.5rem'}),
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
                    dcc.Graph(figure=vol_fig, style=plot_layout),
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
            dcc.Graph(figure=dos_fig, style=dos_plot_layout),
            className='dos-plot',
        )),
            style={'background-color': 'rgba(248, 249, 250, 1)', 'width': 'min-content',
                   'margin-bottom': '1rem', 'margin-top': '1rem',
                   'box-shadow': 'rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px'}),
    ],
    className="content"
)




# ----------------
# landing-layout
p_layout_landing = html.Div([

    dcc.Store(id="page_state", data="landing"),
    dcc.Store(id="cam_store"),
    dcc.Store(id="df_store"),
    dcc.Store(id="choice_store"),
    html.Div([

        dbc.Row(
            [
                dbc.Col(sidebar),
                dbc.Col(html.Div([
    html.Div([html.H1([indent.join('Welcome')], className='greetings', style={'text-align': 'center', 'width': '10em'}),
              html.H1([indent.join('To')], className='greetings', style={'text-align': 'center', 'width': '10em'}),
              html.H1([indent.join('MALA')], className='greetings', style={'text-align': 'center', 'width': '10em'}),
              html.Div('Upload a .cube-File for MALA to process', )],
             style={'text-align': 'center', 'margin-left': '1vw'}),
                ], style={'width': 'content-min', 'margin-top': '20vh'})),  # content ROW 1
                dbc.Col(html.Div()),  # empty settings tab
            ],
        )
    ], id="content-layout", style={'height': '100vh', 'background-color': '#023B59'})

    ])
app.layout = p_layout_landing

# p_layout_plotting will be redefined on plot-choice Input
    # parts of plotting_layout will be redefined on data-upload

# FGEDF4 as contrast

print("COMPONENTS LOADED")
print("_________________________________________________________________________________________")


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

@app.callback(
    Output("collapse-plot-choice", "is_open"),
    Input("open-plot-choice", "n_clicks"),
    Input("page_state", "data"),
    Input("collapse-plot-choice", "is_open"),
    prevent_initial_call=True,
)
def toggle_plot_choice(n_header, page_state, is_open):
    # open plot-style-chooser when state is uploaded
    if dash.callback_context.triggered_id == "page_state":
        print("choice-toggle bc page_state changed")
        return True
    elif n_header:
        return not is_open
# end of sidebar_l collapses


                # CALLBACKS FOR SCATTERPLOT

# collapsable cross-section settings
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
def toggle_y_cs(n_y, is_open):
    if n_y:
        return not is_open


@app.callback(
    Output("z-collapse", "is_open"),
    Input("collapse-z", "n_clicks"),
    Input("z-collapse", "is_open")
)
def toggle_z_cs(n_z, is_open):
    if n_z:
        return not is_open


@app.callback(
    Output("dense-collapse", "is_open"),
    Input("collapse-dense", "n_clicks"),
    Input("dense-collapse", "is_open")
)
def toggle_density_rs(n_d, is_open):
    if n_d:
        return not is_open


@app.callback(
    Output("range-slider-cs-x", "value"),
    Input("reset-cs-x", "n_clicks")
)
def reset_cs_x(n_clicks):
    return [min(scatter_df['x']), max(scatter_df['x'])]


@app.callback(
    Output("range-slider-cs-y", "value"),
    Input("reset-cs-y", "n_clicks")
)
def reset_cs_y(n_clicks):
    return [min(scatter_df['y']), max(scatter_df['y'])]


@app.callback(
    Output("range-slider-cs-z", "value"),
    Input("reset-cs-z", "n_clicks")
)
def reset_cs_z(n_clicks):
    return [min(scatter_df['z']), max(scatter_df['z'])]


@app.callback(
    Output("range-slider-dense", "value"),
    Input("reset-dense", "n_clicks")
)
def reset_cs_dense(n_clicks):
    return [min(scatter_df['val']), max(scatter_df['val'])]

# end of collapsable cross-section settings


                # PAGE STATE
@app.callback(
    Output("page_state", "data"),
    [Input("df_store", "data"),
     Input("choice_store", "data"),
     Input("reset-data", "n_clicks")],
    prevent_initial_call=True,
)
def updatePageState(trig1, trig2, trig3):
        # TODO: check if data is valid
    if trig1 is not None and dash.callback_context.triggered_id == "df_store":
        print("Current state: uploaded")
        return "uploaded"

    if trig2 is not None and dash.callback_context.triggered_id == "choice_store":
        print("Current state: plotting")
        return "plotting"


    if trig3 is not None and dash.callback_context.triggered_id == "reset-data":
        print("Current state: landing")
        return "landing"


                # DATA STORING
# storing uploaded data as a DF.to_dict in dcc.Store -- don't think this is working properly
@app.callback(
    Output("df_store", "data"),
    [Input('upload-data', 'contents')],
    prevent_initial_call=True,
)
def updateDF(f_data):
    # TODO:
    #  smth like "mala_data = mala_inference(f_data)"
    #  --> mala takes uploaded data and returns calculations



    # playground

    # SCATTER-FIG
    sc_fig = px.scatter_3d(
        scatter_df,
        x='x',
        y='y',
        z='z',
        color='val',
        color_continuous_scale=px.colors.sequential.Inferno_r,
        range_color=[df.min()['val'], df.max()['val']],
        template=templ1)

    # Default Marker Params Scatter Plot
    sc_fig.update_traces(default_scatter_marker)

    # ATOMS-FIG
    sc_fig.add_trace(
        go.Scatter3d(x=atoms_DF['x'], y=atoms_DF['y'], z=atoms_DF['z'], mode='markers',
                     marker=dict(size=30, color=atom_colors)))

    # SCATTER default CAMERA
    camera_params = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=1.5, y=1.5, z=1.5)
    )

    # SCATTER GRID PROPERTIES
    sc_fig.update_scenes(xaxis_showgrid=False, yaxis_showgrid=False, zaxis_showgrid=False, camera=camera_params)

    #end playground





    # (a) GET (most) DATA FROM MALA (/ inference script)
    # mala_data = mala_inference.results
    bandEn = mala_data['band_energy']
    totalEn = mala_data['total_energy']
    density = mala_data['density']
    dOs = mala_data['density_of_states']
    enGrid = mala_data['energy_grid']

    coord_arr = np.column_stack(
        list(map(np.ravel, np.meshgrid(*map(np.arange, density.shape), indexing="ij"))) + [density.ravel()])
    dfst=pd.DataFrame(coord_arr, columns=['x', 'y', 'z', 'val'])
    print("DATA has been stored in df_store")
    return dfst.to_dict()
# TODO: this is a mess - find a way to store dataframes


                # PLOT-CHOICE STORING
@app.callback(
    Output("choice_store", "data"),
    [Input('plot-choice', 'value')],
    prevent_initial_call=True,
)
def updatePlotChoice(choice):
    return choice


@app.callback(
    Output("content-layout", "children"),
    [State("df_store", "data"),       # this one might be unnecessary if figs are properly updated/initilized
    State("choice_store", "data"),
    Input("page_state", "data")],
    prevent_initial_call=True,
)
# so wie zuvor schon gemacht prüfen, was der letze input war (cam stored)
def updateLayout(df, plots, page_state):

    # add plots as parameter instead of defining it here

    lc = [sidebar, html.Div(), html.Div()]
    mc = [html.Div(), html.Div(), html.Div()]  # main content components
    rc = [html.Div(), html.Div(), html.Div()]  # right side content
    # each element(component) of mc[] is one centered cell of content
    # rc contains settings-elements for the according mc-element


    print("Updating layout according to ", page_state, " state")

# on page-load, page_state will be None. Default-layout before updateLayout is run is p_layout_landing though, so it's fine
    if page_state == "landing":
        print("STATE: landing")
        print("updated layout to page_state: ", page_state)
        return p_layout_landing
    elif page_state == "uploaded":
        print("updated (naja) layout to page_state: ", page_state)
        raise dash.exceptions.PreventUpdate

    elif page_state == "plotting":
        print("STATE: plotting")
        if len(plots) > 0:
            index = 0
            for choice in plots:
                if choice == "scatter":
                    mc[index] = scatter_plot
                    rc[index] = r_canvas_sc
                    index += 1
                if choice == "volume":
                    mc[index] = volume_plot
                    index += 1
                if choice == "dos":
                    mc[index] = dos_plot
                    index += 1

        p_layout_plotting = [

            dbc.Row(  # First Plot
                [
                    dbc.Col(
                        [dbc.Button(">", id="open-offcanvas-l", n_clicks=0,
                                    style={'position': 'fixed', 'margin-top': '40vh', 'margin-left': '0.5vw'}),
                         lc[0]],
                        width=1),
                    dbc.Col(mc[0],
                        width=9),
                    dbc.Col(
                        [
                        rc[0],
                        dbc.Button("<", id="open-offcanvas-r0", n_clicks=0,
                        style={'margin-top': '35vh', 'margin-right': '0.5vw'})],
                        width=2),  # settings
                ], style={'width': '100vw'}, justify='center'
            ),
            dbc.Row(  # Second Plot
                [
                    dbc.Col(html.Div(), width=1, ),
                    dbc.Col(mc[1], width=9, ),
                    dbc.Col(rc[1], width=2, ),  # gonna be the settings tab
                ], style={'width': '100vw'}
            ),
            dbc.Row(  # Third Plot
                [
                    dbc.Col(html.Div(), width=1, ),
                    dbc.Col(mc[2], width=9, ),  # DOF Plot
                    dbc.Col(rc[2], width=2, ),
                ], style={'width': '100vw'}
            )
        ]
        print("updated layout to page_state: ", page_state)
        return p_layout_plotting



# (STORED) CAM SETTINGS
@app.callback(
    Output("cam_store", "data"),
    [Input("default-cam", "n_clicks"),
    Input("x-y-cam", "n_clicks"),
    Input("x-z-cam", "n_clicks"),
    Input("y-z-cam", "n_clicks"),
    Input("scatter-plot", "relayoutData")],
    prevent_initial_call=True,
)
def storeCamSettings(default_clicks, x_y_clicks, x_z_clicks, y_z_clicks, user_in):
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
        elif dash.callback_context.triggered_id == "scatter-plot":
            return None


                # UPDATE / INIT FIGS

@app.callback(  # UPDATE SCATTER PLOT
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
     Input("cam_store", "data"),
     State("df_store", "data"),
     Input("scatter-atoms", "value")],
    [State("scatter-plot", "relayoutData")],
    prevent_initial_call=True
    )
def updateScatter(slider_range, dense_active, slider_range_cs_x, cs_x_active, slider_range_cs_y, cs_y_active,
                   slider_range_cs_z, cs_z_active,
                   size_slider, opacity_slider, outline, stored_cam_settings, f_data, atoms_enabled, relayout_data):


# df transmission via .to_dict() seems to be working
# TODO: transmit the right (scaled, etc) DF)
    df_try = pd.DataFrame.from_dict(f_data)
    print(df)
    print("dataframing", df_try)

    dfu = scatter_df.copy()
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

    if relayout_data is not None:  # no user input has been made
        if "scene.camera" in relayout_data:
            # custom re-layout cam settings
            fig_upd.update_layout(scene_camera=relayout_data['scene.camera'])
    if stored_cam_settings is not None:
        # locked cam settings
        fig_upd.update_layout(scene_camera=stored_cam_settings)

    # Outline settings
    if outline:
        outlined = dict(width=1, color='DarkSlateGrey')
    else:
        outlined = dict(width=0, color='DarkSlateGrey')

    # WAY TO CHANGE SIZE, OPACITY, OUTLINE
    fig_upd.update_traces(marker=dict(size=marker_size, opacity=opac, line=outlined)
                          , selector=dict(mode='markers'))

    # enable Atoms
    if True in atoms_enabled:
        fig_upd.add_trace(
            go.Scatter3d(x=atoms[2], y=atoms[3], z=atoms[4], mode='markers',
                         marker=dict(size=30, color=atom_colors)))

    return fig_upd


# END OF CALLBACKS FOR SCATTERPLOT
# -------------
# CALLBACKS FOR SIDEBAR


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
    Input("open-offcanvas-r0", "n_clicks"),
    [State("offcanvas-r-sc", "is_open")],
)
def toggle_offcanvas_r(n1, is_open):
    if n1:
        return not is_open
    return is_open


# part of this is more relevant to updateDF
@app.callback(  # FILE-UPLOAD-STATUS
    Output('output-upload-state', 'children'),
    [Input('upload-data', 'filename'),
     Input('upload-data', 'contents'), ],
    prevent_initial_call=True,
)
def uploadInput(filename, contents):
    # checks for .cubes for now, as long as im working on visuals
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

            return 'Upload successful'
        else:
            return 'Wrong file-type. .cube required'
    else:
        return ''


# END OF CALLBACKS FOR SIDEBAR

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
